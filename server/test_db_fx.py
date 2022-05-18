import asyncio

from db.tables import Users, Admins
from server.db_fx import ServerDBFX
from utils.data_structs import UserSubInfo


async def test_update_user():
    await ServerDBFX.update_acc(
        Users(
            winx4_key='WINX4-USER-DB-TEST',
            email='test@gmail.com',
            discord_id='1337',
            sub_info=UserSubInfo().__dict__,
            auth_ips=['1.1.1.1']
        )
    )


async def test_update_admin():
    await ServerDBFX.update_acc(
        Admins(
            winx4_key='WINX4-ADMIN-DB-TEST',
            email='test@gmail.com',
            discord_id='1337',
            auth_ips=['1.1.1.1']
        )
    )


async def test_return_col():
    flatten = lambda *n: (e for a in n
                          for e in (flatten(*a) if isinstance(a, (tuple, list)) else (a,)))
    items = await ServerDBFX.return_col(Admins.auth_ips)
    print(list(flatten(items)))


if __name__ == "__main__":
    asyncio.run(test_return_col())