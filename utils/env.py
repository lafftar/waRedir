import asyncio
import functools
import sys
from json import dumps
from os import listdir, makedirs
from random import choice

import aiohttp
from aiohttp import ClientTimeout
from colorama import init, Fore
from faker import Faker

from utils import terminal
from utils.base_exceptions import CouldNotGetWorkingProxy, NoProxiesLoaded
from utils.custom_logger import Log
from utils.data_structs import Proxy
from utils.req_senders import send_req
from utils.root import get_project_root
from utils.terminal import update_title

init()
terminal.clear()
makedirs(f'{get_project_root()}/program_data/akamai/', exist_ok=True)
makedirs(f'{get_project_root()}/user_data/', exist_ok=True)

def line_not_empty(each): return len(each.strip()) > 0
def split_by_comma(each): return [line.strip() for line in each.strip().split(',')]
def strip_each(line): return [item.strip() for item in line.strip().split(',')][:2]


class Env:
    client: aiohttp.ClientSession = None
    proxies = []
    log: Log = Log('[ENV]', do_update_title=False)
    fake = Faker()
    update_title('Setting Up Env')

    def __init__(self):
        self.increase_limits()
        self.make_files()
        self.is_running_on_server = True
        # check if in dev, by existence of `.dev` in `~/shapeGen/user_data/`
        if '.dev' in listdir(f'{get_project_root()}/user_data'):
            self.is_running_on_server = False

        # self.log.debug(f'Is Running On Server - {self.is_running_on_server}')

        # proxies
        self.load_proxies(f'{get_project_root()}/user_data/proxies.txt')

        # emails
        self.emails = []
        self.load_emails(f'{get_project_root()}/user_data/emails.txt')

        # print(self)

    def __str__(self):
        out = ''
        for key, val in self.__dict__.items():
            if key in ('log', 'counter', 'fake'):
                continue
            if key in ('proxies', 'emails', 'accs'):
                val = len(val)
            val = '\n\t'.join(dumps(val, indent=4).split("\n"))
            out += f'\t[{key.upper()}]: {val}\n'
        return f"{Fore.BLUE}\n" \
               f"\t[ENV SUMMARY]\n\n" \
               f"{out}"

    def restart(self):
        self.load_config()
        self.load_proxies(f'{get_project_root()}/user_data/proxies.txt')
        self.load_emails(f'{get_project_root()}/user_data/emails.txt')

    def make_files(self):
        # make required files
        base_user_path = f'{get_project_root()}/user_data'
        required_files = ['emails.txt', 'proxies.txt', 'webhooks.txt', 'config.csv']
        current_files = listdir(base_user_path)
        for item in required_files:
            if item not in current_files:
                if self.make_default_file(item):
                    continue
                with open(f'{get_project_root()}/user_data/{item}', 'w') as file:
                    file.write('')

    @staticmethod
    def make_default_file(item):
        with open(f'{get_project_root()}/user_data/{item}', 'w') as file:
            if item == 'config.csv':
                out = "SETTING, VALUE\n"
                to_write = [
                    ('DOMAIN', 'www.zalando.co.uk'),
                ]
                for setting, value in to_write:
                    out += f'{setting}, {value}\n'
                file.write(out)
                return True
            return False

    """Loading ENV object."""
    def load_config(self):
        # grab config
        with open(f'{get_project_root()}/user_data/config.csv') as file:
            settings = {
                split_by_comma(line)[0].strip(): split_by_comma(line)[1].strip()
                for line in file.readlines()
                if line_not_empty(line)
            }

            self.key = settings['KEY']
            self.two_cap_key = settings['2CAPTCHA KEY']
            self.email = settings['EMAIL']
            self.password = settings['PASSWORD']
            self.mailbox = settings['MAILBOX']
            self.imap_server = settings['IMAP_SERVER']

        out = ''
        for key, val in settings.items():
            out += f'\t{key}: {val}\n'
        # self.log.info('\n'
        #               '\t[SETTINGS]\n'
        #               f'{out}')

    def load_proxies(self, proxies_file):
        with open(proxies_file) as file:
            self.proxies = [line.strip().split(':') for line in file.readlines() if line_not_empty(line)]
            self.proxies = [
                Proxy(host=line[0], port=line[1])
                if len(line) == 2
                else
                Proxy(host=line[0], port=line[1], username=line[2], password=line[3])
                for line in self.proxies
            ]
        Env.proxies = self.proxies

    def load_emails(self, email_file):
        with open(email_file) as file:
            self.emails = [line.split(':')[0] for line in file.readlines() if line_not_empty(line)]

    @staticmethod
    def increase_limits():
        if sys.platform == 'win32':
            import win32file

            # asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
            win32file._setmaxstdio(8192)

        if sys.platform == 'linux':
            import resource

            before, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
            try:
                resource.setrlimit(resource.RLIMIT_NOFILE, (1048576, hard))
            except ValueError:
                Env.log.debug(f'Already at max limit - {before}')

    @staticmethod
    async def check_proxy(proxy: Proxy) -> str | None:
        await Env.create_http_client()
        resp: aiohttp.ClientResponse = await send_req(functools.partial(Env.client.get,
                                                                        url='https://api.ipify.org',
                                                                        proxy=str(proxy),
                                                                        headers={}),
                                                      num_tries=2)
        if not resp:
            return

        ip = await resp.text()
        return ip

    @staticmethod
    async def return_proxy() -> Proxy:
        """
        Pick a proxy randomly, test it and return it.
        :return:
        """
        proxy, ip = None, ''
        await Env.create_http_client()
        for _ in range(10):
            try:
                proxy = choice(Env.proxies)
            except IndexError:
                raise NoProxiesLoaded
            # proxy = Proxy(host='192.168.0.28', port='4000')
            # proxy = Proxy(host='localhost', port='8082')
            Env.log.debug(f'Testing - {proxy}.')
            ip: str = await Env.check_proxy(proxy)
            if not ip:
                Env.log.error(f'Test Failed - {proxy}.')
                proxy = None
                continue
            break

        if not ip:
            raise CouldNotGetWorkingProxy
        Env.log.info(f'Test Good - {proxy} - {ip}.')
        return proxy

    @staticmethod
    async def create_http_client():
        if not Env.client:
            ClientTimeout.total = 5.0
            Env.client = aiohttp.ClientSession(connector=aiohttp.TCPConnector(), trust_env=True)

    @staticmethod
    async def close_http_client():
        if Env.client:
            await Env.client.close()


ENV = Env()

# if __name__ == "__main__":
#     asyncio.run(Env.return_proxy())