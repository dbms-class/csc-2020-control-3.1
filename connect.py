# encoding: UTF-8
# В этом файле реализованы методы для подключения к PostgreSQL

from psycopg2 import pool
from psycopg2.extras import LoggingConnection
import psycopg2 as pg_driver
from playhouse.pool import PooledPostgresqlDatabase

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

from args import *

pg_pool = pool.SimpleConnectionPool(
    1, 50, user=args().pg_user, password=args().pg_password, host=args().pg_host, port=args().pg_port)


def getconn():
    return pg_pool.getconn()
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
