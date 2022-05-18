import asyncio

from colorama import Fore
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm import Session, sessionmaker

from db.base import MainDB
from db.tables import Admins, Users
from utils.custom_logger import Log
from utils.terminal import color_wrap

log = Log("[SERVER_DB]")


class ServerDBFX:
    # create db session
    main_session: Session = sessionmaker(bind=MainDB.base_db_engine, expire_on_commit=False)
    MainDB.init_tables()

    @staticmethod
    async def update_acc(acc: Admins | Users):
        """
        Will update account or make a new account.
        :param acc:
        :return: None
        """
        if isinstance(acc, Admins):
            table = Admins
        elif isinstance(acc, Users):
            table = Users
        else:
            raise Exception('acc type not `Admins` or `Users`. What\'s going on?')

        def _update_acc():
            with ServerDBFX.main_session.begin() as short_session:
                current_acc_info: table | None = \
                    short_session.query(table) \
                        .filter(table.winx4_key == acc.winx4_key) \
                        .first()
                try:
                    if current_acc_info:
                        current_acc_info.update_from_dict(acc.to_dict())
                        log.debug(color_wrap(f'Updated {acc.email} in db.', fore_color=Fore.WHITE))
                    else:
                        short_session.add(acc)
                        log.debug(color_wrap(f'Added {acc.email} to db.', fore_color=Fore.BLUE))
                except InvalidRequestError:
                    log.exception('Error Adding/Updating Account.')
                    input('Waiting')

        await asyncio.get_event_loop().run_in_executor(None, _update_acc)

    @staticmethod
    async def return_col(col):
        """
        Will return winx4 keys for specified table.
        :param col: Admins.winx4_key | Users.winx4_key
        :return: None |
        """

        def _return_col():
            with ServerDBFX.main_session.begin() as short_session:
                try:
                    items: list[str] | None | None = short_session.query(col).all()
                    if not items:
                        log.debug(color_wrap(f'Found {len(items)} [{col}] in db.', fore_color=Fore.RED))
                        return
                    log.debug(color_wrap(f'Found {len(items)} [{col}] in db.', fore_color=Fore.WHITE))
                    items = [row[0] for row in items]
                    return items
                except InvalidRequestError:
                    log.exception('Error Adding/Updating Account.')
                    input('Waiting')

        return await asyncio.get_event_loop().run_in_executor(None, _return_col)


if __name__ == "__main__":
    asyncio.run(ServerDBFX.return_acc('lilu03@gmx.de', 'LuLu010903'))
