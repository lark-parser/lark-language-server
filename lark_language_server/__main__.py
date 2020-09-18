"""Main entry point for starting the server"""

import argparse
import logging

from .server import lark_server

# setup python logging to lark-ls.log
logging.basicConfig(filename="lark-ls.log", level=logging.DEBUG, filemode="w")


def main():
    parser = argparse.ArgumentParser(description="Lark Language Server. Defaults over stdio.", prog="lark_language_server")

    parser.add_argument(
        "--tcp", action="store_true",
        help="Use TCP server instead of stdio"
    )
    parser.add_argument(
        "--host", default="127.0.0.1",
        help="Bind to this address"
    )
    parser.add_argument(
        "--port", type=int, default=2087,
        help="Bind to this port"
    )
    args = parser.parse_args()

    if args.tcp:
        lark_server.start_tcp(args.host, args.port)
    else:
        lark_server.start_io()


if __name__ == '__main__':
    main()
