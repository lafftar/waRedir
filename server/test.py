import asyncio

import httpx

from browser_based.db_fx import ZBDB
from db.tables import Accounts
from utils.globals import ENV
from utils.tools import print_req_info


async def test_return_bp_cookie():
    path: str = '/return-bp-cookie'
    host = 'https://hcbp.winx4.net'
    # url = 'http://localhost:1337'
    async with httpx.AsyncClient(
            headers={'X-Token': "WINX4-ADMIN"}
    ) as c:
        res: httpx.Response = await c.get(url=f'{host}{path}')
    print_req_info(res, True, True)


async def test_update_acc():
    acc: Accounts = await ZBDB.return_acc('turnerziskylarzihq9904@gmail.com')
    print(acc)
    acc.num_used_total += 1
    async with httpx.AsyncClient(
            # headers={'X-Token': "WINX4-ADMIN"}
    ) as c:
        # url = 'https://hcbp.winx4.net'
        url = 'http://localhost:1337'
        res: httpx.Response = await c.post(url=f'{url}/update-acc', json=acc.to_dict())
    print_req_info(res, True, True)


if __name__ == "__main__":
    try:
        asyncio.run(test_return_bp_cookie())
    finally:
        asyncio.run(ENV.close_http_client())