# encoding: UTF-8
# В этом файле реализованы методы для подключения к PostgreSQL

from psycopg2 import pool
from psycopg2.extras import LoggingConnection
import psycopg2 as pg_driver
from playhouse.pool import PooledPostgresqlDatabase
import cherrypy
import argparse

# Драйвер PostgreSQL
# Находится в модуле psycopg2-binary, который можно установить командой
# pip install psycopg2-binary или её аналогом.
import psycopg2 as pg_driver

from psycopg2 import pool

# Драйвер SQLite3
# Находится в модуле sqlite3, который можно установить командой
# pip install sqlite3 или её аналогом.
import sqlite3 as sqlite_driver


import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

from args import *

pg_pool = pool.SimpleConnectionPool(
    1, 50, user=args().pg_user, password=args().pg_password, host=args().pg_host, port=args().pg_port)


def getconn():
    # return pg_pool.getconn()
    return pg_driver.connect(user=args().pg_user, password=args().pg_password, host=args().pg_host, port=args().pg_port)



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



# Разбирает аргументы командной строки.
# Выплевывает структуру с полями, соответствующими каждому аргументу.
def parse_cmd_line():
    parser = argparse.ArgumentParser(description='Эта программа вычисляет 2+2 при помощи реляционной СУБД')
    parser.add_argument('--pg-host', help='PostgreSQL host name', default='kandula.db.elephantsql.com')
    parser.add_argument('--pg-port', help='PostgreSQL port', default=5432)
    parser.add_argument('--pg-user', help='PostgreSQL user', default='dqwnxlam')
    parser.add_argument('--pg-password', help='PostgreSQL password', default='8rOhtlwX1ahP6YT4b1dGWbcSkvnnE_6O')
    parser.add_argument('--pg-database', help='PostgreSQL database', default='dqwnxlam')
    parser.add_argument('--sqlite-file', help='SQLite3 database file. Type :memory: to use in-memory SQLite3 database', default=None)
    return parser.parse_args()


class ConnectionFactory:
    def __init__(self, open_fxn, close_fxn):
        self.open_fxn = open_fxn
        self.close_fxn = close_fxn

    def getconn(self):
        return self.open_fxn()

    def putconn(self, conn):
        return self.close_fxn(conn)


def create_connection_factory(args):
    # Создаёт подключение к SQLite в соответствии с аргументами командной строки.
    def open_sqlite():
        return sqlite_driver.connect(args.sqlite_file)

    def close_sqlite(conn):
        pass

    # Создаёт подключение в соответствии с аргументами командной строки.
    # Если указан аргумент --sqlite-file то создается подключение к SQLite,
    # в противном случае создаётся подключение к PostgreSQL
    if args.sqlite_file is not None:
        return ConnectionFactory(open_fxn=open_sqlite, close_fxn=close_sqlite)
    else:
        # Создаёт подключение к постгресу в соответствии с аргументами командной строки.
        pg_pool = pool.SimpleConnectionPool(1, 5,
                                  user=args.pg_user, password=args.pg_password, host=args.pg_host, port=args.pg_port)
        count = 0
        def open_pg():
            nonlocal count
            count += 1
            print(f"We issued {count} queries")
            return pg_pool.getconn()

        def close_pg(conn):
            pg_pool.putconn(conn)

        return ConnectionFactory(open_fxn=open_pg, close_fxn=close_pg)


connection_factory = create_connection_factory(parse_cmd_line())