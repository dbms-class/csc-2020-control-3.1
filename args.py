import argparse

parser = argparse.ArgumentParser(description='Hello DB web application')
parser.add_argument('--pg-host', help='PostgreSQL host name', default='localhost')
parser.add_argument('--pg-port', help='PostgreSQL port', default=5432)
parser.add_argument('--pg-user', help='PostgreSQL user', default='postgres')
parser.add_argument('--pg-password', help='PostgreSQL password', default='postgres')
parser.add_argument('--pg-database', help='PostgreSQL database', default='postgres')

_args = parser.parse_args()


def args():
    global _args
    return _args
