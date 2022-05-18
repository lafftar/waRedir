import asyncio
import functools
import re
from asyncio import sleep
from json import dumps, loads, JSONDecodeError

import aiohttp
import anyio
import httpx
from aiohttp import client_exceptions
from bs4 import BeautifulSoup
from colorama import Fore, Style
from httpx import AsyncClient

from utils.custom_logger import Log
from utils.terminal import color_wrap
from utils.tools import print_req_info

log = Log('[REQ SENDER]')


async def send_req(req_obj: functools.partial, num_tries: int = 5) -> \
        httpx.Response | aiohttp.ClientResponse | None:
    """
    Central Request Handler. All requests should go through this.
    :param num_tries:
    :param req_obj:
    :return:
    """
    for _ in range(num_tries):
        try:
            item = await req_obj()
            return item
        except (
                # httpx errors
                httpx.ConnectTimeout, httpx.ProxyError, httpx.ConnectError,
                httpx.ReadError, httpx.ReadTimeout, httpx.WriteTimeout, httpx.RemoteProtocolError,

                # aiohttp errors
                asyncio.exceptions.TimeoutError, client_exceptions.ClientHttpProxyError,
                client_exceptions.ClientProxyConnectionError,
                client_exceptions.ClientOSError,
                client_exceptions.ServerDisconnectedError,

                # any io errors
                anyio.ClosedResourceError
        ) as c:
            print(c)
            await sleep(2)
    return


def robot_cookie(cookie: str, parent_domain: str):
    items = cookie.split(';')
    SameSite = HttpOnly = Secure = Domain = Path = Expires = Comment = MaxAge = CookieName = CookieValue \
        = Size = Sessionkey = Version = Priority = None
    CookieName = CookieValue = None
    idx = len(items) - 1
    while idx >= 0:
        item = items[idx].strip()
        idx -= 1
        if not item:
            continue
        SameSiteMatched = re.match(r'^SameSite(.*)?', item, re.I)
        HttpOnlyMatched = SameSiteMatched or re.match(r'^HttpOnly(.*)$', item, re.I)
        SecureMatched = HttpOnlyMatched or re.match(r'^Secure(.*)$', item, re.I)
        DomainMatched = SecureMatched or re.match(r'^Domain(.*)?', item, re.I)
        PathMatched = DomainMatched or re.match(r'^Path(.*)?', item, re.I)
        ExpiresMatched = PathMatched or re.match(r'^Expires(.*)?', item, re.I)
        CommentMatched = ExpiresMatched or re.match(r'^Comment(.*)?', item, re.I)
        MaxAgeMatched = ExpiresMatched or re.match(r'^Max-Age=(.*)?', item, re.I)
        VersionMatched = MaxAgeMatched or re.match(r'^Version=(.*)?', item, re.I)
        PriorityMatched = VersionMatched or re.match(r'^priority=(.*)?', item, re.I)
        matched = SameSiteMatched or HttpOnlyMatched or SecureMatched or DomainMatched or PathMatched or \
                  ExpiresMatched or CommentMatched or MaxAgeMatched or VersionMatched or PriorityMatched
        if matched:
            val = matched.groups(0)[0].lstrip('=')
            if matched == SameSiteMatched:
                SameSite = val if val.lower() in ['strict', 'lax', 'none'] else None
            elif matched == HttpOnlyMatched:
                HttpOnly = True
            elif matched == SecureMatched:
                Secure = True
            elif matched == DomainMatched:
                Domain = val
            elif matched == PathMatched:
                Path = val
            elif matched == PathMatched:
                Path = val
            elif matched == ExpiresMatched:
                Expires = val
            elif matched == CommentMatched:
                Comment = val
            elif matched == MaxAgeMatched:
                MaxAge = val
            elif matched == VersionMatched:
                Version = val
            elif matched == PriorityMatched:
                Priority = val
        else:
            CookieMatched = re.match(r'^(.[^=]*)=(.*)?', item, re.I)
            if CookieMatched:
                CookieName, CookieValue = CookieMatched.groups(0)

    Sessionkey = True if not Expires else False
    Size = (len(CookieName) if CookieName else 0) + (len(CookieValue) if CookieValue else 0)

    Domain = parent_domain if CookieName and not Domain else Domain
    Path = '/' if CookieName and not Path else Path
    Priority = 'Medium' if CookieName and not Priority else Priority.title() if Priority else 'Medium'

    Cookie = {
        CookieName: CookieValue,
        'Name': CookieName,
        'Value': CookieValue,
        'Domain': Domain,
        'Path': Path,
        'Expires': Expires,
        'Comment': Comment,
        'MaxAge': MaxAge,
        'SameSite': SameSite,
        'HttpOnly': HttpOnly,
        'Secure': Secure,
        'Size': Size,
        'Sessionkey': Sessionkey,
        'Version': Version,
        'Priority': Priority
    }
    return Cookie if CookieName else None


async def tls_send(req: httpx.Request, client: httpx.AsyncClient, proxies: str = '') -> httpx.Response | None:
    """
    Just for the TLS.
    :param proxies:
    :param client:
    :param req:
    :return:
    """
    old_url = str(req.url)
    req.headers['poptls-url'] = old_url
    # {choice(TLS_PORTS)}
    req.url = httpx.URL(f'http://localhost:8082')
    if proxies:
        req.headers['poptls-proxy'] = proxies

    # adding redirects, so we can build history on the resp object
    req.headers['poptls-allowredirect'] = 'false'
    res: httpx.Response = await send_req(functools.partial(client.send, req), num_tries=5)
    req.headers.pop('poptls-url')
    req.headers.pop('poptls-proxy', None)
    req.headers.pop('Poptls-Allowredirect', None)
    req.url = old_url

    # set cookies on the client, for some reason carcraftz doesn't play well with this
    if res and res.headers:
        for key, val in res.headers.multi_items():
            if key.lower() != 'set-cookie':
                continue
            cookie = robot_cookie(val, parent_domain=httpx.URL(res.url).host)
            # print(dumps(cookie, indent=4))

            # delete from jar if there
            try:
                client.cookies.delete(
                    name=cookie['Name'],
                    domain=cookie['Domain'],
                    path=cookie['Path']
                )
            except KeyError:
                pass  # is not in jar

            # set in jar
            client.cookies.set(
                name=cookie['Name'],
                value=cookie['Value'],
                domain=cookie['Domain'],
                path=cookie['Path']
            )
    return res


async def ext_tls_send(req: httpx.Request, client: httpx.AsyncClient, proxies: str = '') -> httpx.Response | None:
    """
    Just for the TLS. Turns httpx req obj into tls-compliant req obj.
    Does not work for deflate/zlib.
    :param proxies:
    :param client:
    :param req:
    :return:
    """
    # turn request object into tls compliant
    headers = [
        f":method!=!{req.method}",
        f":authority!=!{req.url.host}",
        f":scheme!=!{req.url.scheme}",
        f":path!=!{req.url.path}{req.url.params}"
    ]

    for key, val in req.headers.items():
        if key.lower() in ('connection', 'host', 'content-length'):  # dunno why, but it fucks shit up
            continue
        headers.append(f'{key}!=!{val}')

    req_body = ''
    if req.content:
        try:
            req_body = dumps(loads(req.read()))
        except JSONDecodeError:
            req_body = BeautifulSoup(req.read().decode('utf-8'), 'lxml').prettify()

    req_info = {
        "url": str(req.url),
        "headers": headers,
        "body": req_body,
        "proxy": proxies,
        "method": req.method,
        "ja3": "CHROME_93",
        "bodyBytes": isinstance(req_body, bytes),
        "timeout": 8000,
        "settings": [
            "1!=!65536",
            "3!=!1000",
            "4!=!6291456",
            "6!=!262144"
        ],
        "windowupdate": 15663105,
        "http2support": True
    }
    tls_req: httpx.Request = httpx.Request(
        method='POST',
        url='http://localhost:8080',
        headers={
            "auth": "5504455571"
        },
        json=req_info
    )

    res: httpx.Response = await send_req(functools.partial(client.send, tls_req), num_tries=5)
    if not res:
        return

    # construct response object
    try:
        res_body: dict = res.json()
    except JSONDecodeError as e:
        specific_error = ''
        if 'Proxy responded with non 200 code' in res.text:
            specific_error = 'Proxy Failed'
            print_req_info(res, True, True)
        elif 'unexpected EOF' in res.text:
            specific_error = 'unexpected EOF'
        elif 'bad record MAC' in res.text:
            specific_error = 'bad record MAC'
        elif 'client connection lost' in res.text:
            specific_error = 'client connection lost'.title()
        elif 'certificate signed by unknown authority' in res.text:
            specific_error = 'certificate signed by unknown authority'.title()
        else:
            print_req_info(res, True, True)
        log.error(color_wrap(Fore.RED + f'ERROR MAKING HTTPX RESPONSE OBJECT! ' + specific_error +
                             ' on TLS Client.' + Style.RESET_ALL))
        return res

    tls_res: httpx.Response = httpx.Response(
        status_code=res_body.get('StatusCode'),
        content=res_body.get('Body'),
        request=req,
        history=res.history
    )

    # set response headers
    headers = []
    for key, main_val in res_body.get('Headers').items():
        # might be many main_val
        for val in main_val:
            headers.append((key, val))
    tls_res.headers = httpx.Headers(headers)

    # add cookies to client
    client.cookies.extract_cookies(tls_res)
    return tls_res


if __name__ == "__main__":


    asyncio.run(test_2())
