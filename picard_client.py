#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2021 Paweł Krzemiński
#
# Distributed under terms of the MIT license.

"""
Client
"""
import sys
#import logging
import socket
#import lorem


#logging.basicConfig(format="%(asctime)s %(message)s",
#                    filename="/home/pi/Picard/log.txt", datefmt="%y.%m.%d %H:%M:%S")



def send(what, addr):
    addr = ("127.0.0.1", 65432)
    sock = socket.socket()
    what = what.encode('ascii')
    try:
        sock.connect_ex(addr)
        sent = None
        while sent != what:
            sentCount = sock.send(what)
            sent = what[0:sentCount]
    except:
        print(sys.exc_info())
        #logging.error(sys.exc_info()[0:2])
    finally:
        sock.close()

#send("okey", addr)
def main():
    sock = socket.socket()
    addr = ("127.0.0.1", 65432)
    choice = None
    menu = """Pick what to send.
    1. Send "ok".
    2. Send "nok"
    choice: """
    def send(what, addr):
        what = what.encode('ascii')
        logging.warning("yes")
        try:
            sock.connect_ex(addr)
            sent = None
            while sent != what:
                sentCount = sock.send(what)
                sent = what[0:sentCount]
                print(what, sent, sentCount)
        except:
            logging.error(sys.exc_info()[0:2])
        finally:
            return

    while choice != "0":
        choice = None
        choice = input(menu)
        print(menu, end="")
        if choice == "1":
            print("1")
            send("test",addr)
        elif choice == "2":
            print("2")
            send("noknok22",addr)
if __name__ == "__main__":
    main()
