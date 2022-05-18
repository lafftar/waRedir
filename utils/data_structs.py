from dataclasses import dataclass, astuple
from typing import NamedTuple

from playwright.async_api import ProxySettings


class Proxy:
    def __init__(self, host: str, port: str, username: str = '', password: str = '', protocol: str = 'http'):
        self.host: str = host
        self.port: str = port
        self.username: str = username
        self.password: str = password
        self.protocol: str = protocol

    def __str__(self) -> str:
        if self.password:
            return f'{self.protocol}://{self.username}:{self.password}@{self.host}:{self.port}'
        return f'{self.protocol}://{self.host}:{self.port}'

    def to_pw(self) -> ProxySettings:
        return ProxySettings(server=f'{self.protocol}://{self.host}:{self.port}',
                             username=f'{self.username}',
                             password=f'{self.password}')

    def to_httpx(self) -> str:
        if self.password:
            return f'{self.protocol}://{self.username}:{self.password}@{self.host}:{self.port}'
        return f'{self.protocol}://{self.host}:{self.port}'

    def to_winx4(self) -> tuple:
        if self.password:
            return self.protocol, self.username, self.password, self.host, self.port
        return self.protocol, self.host, self.port

    @staticmethod
    def from_winx4(proxy: tuple):
        if len(proxy) == 3:
            return Proxy(protocol=proxy[0], host=proxy[1], port=proxy[2])
        return Proxy(protocol=proxy[0], username=proxy[1], password=proxy[2], host=proxy[3], port=proxy[4])

    @staticmethod
    def from_playwright_fmt(proxy: ProxySettings):
        """
        Converts from playwright fmt to this.
        :param proxy:
        :return: this Proxy object
        """
        user = proxy.get('username')
        passwd = proxy.get('password')
        server = proxy.get('server').split('://')
        protocol = server[0]
        server = server[1]
        host, port = server.split(':')
        return Proxy(host=host, port=port, username=user, password=passwd, protocol=protocol)


@dataclass
class Resp:
    body: str | bytes = None
    headers: dict = None
    status: int = 200

    def __iter__(self):
        return iter(astuple(self))

    @property
    def to_pw(self):
        return {'status': self.status, 'headers': self.headers, 'body': self.body}

@dataclass
class ZLoginStatus:
    done: bool = None
    success: bool = None
    fail_message: str = ''

    def is_success(self):
        self.done = True
        self.success = True

    def is_failed(self, fail_msg: str):
        self.done = True
        self.success = False
        self.fail_message = fail_msg


@dataclass
class LoggedInState:
    redirect_url: str
    headers: dict
    cookies: dict

@dataclass
class AkamStatus:
    abck_limit: int = 3
    pixel_limit: int = 1
    abck_post: int = 0
    pixel_post: int = 0
    ready: bool = False

    def set_ready(self):
        if self.abck_post >= self.abck_limit - 1 and self.pixel_post >= self.pixel_limit:
            self.ready = True

    def incr_abck_post(self):
        self.abck_post += 1
        self.set_ready()

    def incr_pixel_post(self):
        self.pixel_post += 1
        self.set_ready()

@dataclass
class APIPayload:
    # for jevi's akamai api
    ua: str
    abck: str = None
    bmsz: str = None
    site: str = None
    v2: bool = False
    script_val: str = None
    pixel_id: str = None
    winx4_key: str = None
    mode: str = 'API'


@dataclass
class Package:
    num_zlogin_requests: int = None
    created_ts: str = None

@dataclass
class UserSubInfo:
    packages: list[Package] = None
