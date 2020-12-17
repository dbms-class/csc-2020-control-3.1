# encoding: UTF-8
# В этом файле реализованы методы для подключения к PostgreSQL

from psycopg2 import pool
from psycopg2.extras import LoggingConnection
import psycopg2 as pg_driver
from playhouse.pool import PooledPostgresqlDatabase
from contextlib import contextmanager
from playhouse.db_url import connect

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

from args import *

# pg_pool = pool.SimpleConnectionPool(
    # 1, 50, user=args().pg_user, password=args().pg_password, host=args().pg_host, port=args().pg_port)


class ConnectionFactory:
    def __init__(self, open_fxn, close_fxn):
        self.open_fxn = open_fxn
        self.close_fxn = close_fxn

    def getconn(self):
        return self.open_fxn()

    def putconn(self, conn):
        return self.close_fxn(conn)

    @contextmanager
    def conn(self):
        try:
            result = self.open_fxn()
            yield result
        finally:
            self.close_fxn(result)


def create_connection_factory():
    def open_pg():
        _args = args()
        return connect(f"postgres+pool://{_args.pg_user}:{_args.pg_password}@{_args.pg_host}:{_args.pg_port}/{_args.pg_database}")

    def close_pg(conn):
        conn.close()

    return ConnectionFactory(open_fxn=open_pg, close_fxn=close_pg)


connection_factory = create_connection_factory()

# def getconn():
#     return pg_pool.getconn()
    #return pg_driver.connect(user=args().pg_user, password=args().pg_password, host=args().pg_host, port=args().pg_port)



class LoggingDatabase(PooledPostgresqlDatabase):
    def __init__(self, args):
        super(LoggingDatabase, self).__init__(
            database=args.pg_database, register_unicode=True, encoding=None,
            isolation_level=None, host=args.pg_host, user=args.pg_user, port=args.pg_port, password=args.pg_password,
            connection_factory=LoggingConnection)

    def _connect(self):
        conn = super(LoggingDatabase, self)._connect()
        conn.initialize(logger)
        return conn
