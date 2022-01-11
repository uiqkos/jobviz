import argparse

from src import settings


class DefaultArgumentParser(argparse.ArgumentParser):
    def __init__(self, *args, db_connection_args=True, use_proxy=False, **kwargs):
        super().__init__(*args, **kwargs)

        self.add_argument(
            '--db',
            default=settings.db_name,
            help='Имя бд (если не указано, берется из .env)'
        )

        self.add_argument(
            '--db-host',
            default=settings.db_host,
            help='Хост подключения к mongodb (если не указано, берется из .env)'
        )

        self.add_argument(
            '--db-port',
            default=settings.db_port,
            help='Порт подключения к mongodb (если не указано, берется из .env)'
        )
