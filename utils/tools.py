import asyncio
from datetime import datetime
from json import dumps, JSONDecodeError, loads
from os import makedirs
from typing import Union

import aiofiles
import httpx
from bs4 import BeautifulSoup
from colorama import Fore, Back, Style
from playwright import async_api

from utils.custom_logger import Log
from utils.root import get_project_root
from utils.terminal import color_wrap


def print_req_obj(req: httpx.Request, res: Union[httpx.Response, None] = None, print_now: bool = False) -> str:
    if res:
        res.read()
        req = res.request
        http_ver = res.http_version
    else:
        http_ver = 'HTTP/1.1(Guess.)'
    req.read()
    req_str = f'{color_wrap(Fore.BLACK + str(req.method), Back.MAGENTA)} {req.url} {http_ver}\n'
    for key, val in req.headers.multi_items():
        req_str += f'{key.title()}: {val}\n'

    if req.content:
        try:
            req_str += f"Req Body (JSON): \n{color_wrap(Fore.BLACK + dumps(loads(req.read()), indent=4))}"
        except JSONDecodeError:
            req_str += f"Req Body (HTML): \n" \
                       f"{color_wrap(Fore.BLACK + BeautifulSoup(req.read().decode('utf-8'), 'lxml').prettify())}"
    req_str += '\n'
    if print_now:
        print(f'{Fore.LIGHTBLUE_EX}{req_str}{Style.RESET_ALL}')
    return req_str


def print_req_info(res: httpx.Response, print_headers: bool = False, print_body: bool = False):
    if not res:
        print('No Response Body')
        return

    with open(f'{get_project_root()}/src.html', mode='w', encoding='utf-8') as file:
        try:
            with open(f'{get_project_root()}/src.json', mode='w', encoding='utf-8') as js_file:
                js_file.write(dumps(res.json(), indent=4))
                # print('wrote json')
        except JSONDecodeError:
            file.write(res.text)
    if not print_headers:
        return

    req_str = print_req_obj(res.request, res)

    resp_str = f'{res.http_version} {color_wrap(Fore.BLACK + str(res.status_code), Back.MAGENTA)} {res.reason_phrase}\n'
    for key, val in res.headers.multi_items():
        resp_str += f'{key.title()}: {val}\n'
    resp_str += f'Cookie: '
    for key, val in res.cookies.items():
        resp_str += f'{key}={val};'
    resp_str += '\n'

    if print_body:
        try:
            resp_str += f"Resp Body (JSON): \n{color_wrap(Fore.BLACK + dumps(res.json(), indent=4))}"
        except JSONDecodeError:
            resp_str += f"Resp Body (HTML): \n{color_wrap(Fore.BLACK + BeautifulSoup(res.text, 'lxml').prettify())}"
    resp_str += '\n|\n|'

    sep_ = '-' * 10
    boundary = '|'
    boundary += '=' * 100
    print(boundary)
    print(f'|{sep_}REQUEST{sep_}')
    print(req_str)
    print(f'|{sep_}RESPONSE{sep_}')
    print(resp_str)
    print(f'|History: {res.history}')
    for resp in res.history:
        print(resp.url, end='\n')
    print()
    print(boundary)


async def print_pw_req_info(
        req: async_api.Request,
        include_headers: bool = True,
        include_body: bool = True,
        include_httpx_repr: bool = True,
        print_now: bool = True
):
    log: Log = Log('[PW REQ PRINTER]', do_update_title=False)
    body: dict | str = ''
    is_json: bool = False
    headers = await req.all_headers()

    req_str = f'{Style.RESET_ALL}{"=" * 20}{Style.BRIGHT}REQUEST{Style.RESET_ALL}{"=" * 20}\n\n'  # final str
    # req line
    req_str += f'{color_wrap(Fore.BLACK + str(req.method), Back.MAGENTA)} {req.url} HTTP 2.0/(Guess)\n'

    if include_headers:
        for key, val in headers.items():
            req_str += f'{key.title()}: {val}\n'

    try:
        req_post_data = req.post_data
    except UnicodeDecodeError:
        log.error(f'UnicodeDecodeError when trying to get req.post_data for {req.url}')
        return

    if req_post_data:
        try:
            body = dumps(loads(req_post_data), indent=4)
            file_name = f'{get_project_root()}/pw_req_src.json'
            if include_body:
                req_str += f"Req Body (JSON): \n{color_wrap(Fore.BLACK + body)}\n"
        except JSONDecodeError:
            body = BeautifulSoup(req_post_data, 'lxml').prettify()
            file_name = f'{get_project_root()}/pw_req_src.html'
            if include_body:
                req_str += f"Req Body (HTML): \n{color_wrap(Fore.BLACK + body)}\n"

        with open(file_name, mode='w', encoding='utf-8') as file:
            file.write(body)
    else:
        req_str += f"Req Body (None):\n{body}\n"

    if include_httpx_repr:
        httpx_repr = ''
        httpx_repr += 'httpx.Request(\n' \
                   f'\tmethod="{req.method.upper()}",\n' \
                   f'\turl="{req.url}",\n' \
                   f'\theaders={dumps(headers, indent=4)},\n'
        if body:
            if is_json:
                httpx_repr += f'\tjson={req.post_data_json}\n'
            else:
                httpx_repr += f'\tcontent={req.post_data}\n'

        httpx_repr += ')\n\n'
        makedirs(f'{get_project_root()}/{datetime.now().date()}', exist_ok=True)
        await write(f'{get_project_root()}/{datetime.now().date()}/httpx_repr.txt', httpx_repr)
        req_str += httpx_repr

    req_str += f'\n\n{Style.RESET_ALL}{"=" * 20}{Style.BRIGHT}REQUEST{Style.RESET_ALL}{"=" * 20}'
    if print_now:
        print(req_str)
    await write(f'{get_project_root()}/{datetime.now().date()}/pw_repr.txt', req_str)
    return req_str

sem: asyncio.Semaphore = asyncio.Semaphore(1)
async def write(file: str, body: str):
    async with sem:
        async with aiofiles.open(file, 'a') as file:
            await file.write(body)