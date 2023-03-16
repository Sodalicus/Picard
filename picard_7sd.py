# /usr/bin/env python3
# -*- codng: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2021 Paweł Krzemiński 
#
# Distributed under terms of the MIT license.

"""

"""

import time
import socket, sys
import selectors, logging

from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.virtual import viewport, sevensegment

class SevenSegDisplay():

    def __init__(self):
        serial = spi(port=0, device=0, gpio=noop())
        device = max7219(serial, cascaded=1)
        device.contrast(15)
        self.seg = sevensegment(device)
        self.update_clock()
        self.messages = []
        self.t0 = time.time()

    def update_clock(self):
        text = time.strftime("%H%M")
        self.seg.text = str(text)[0:8]# 7 seg can only display 8 digits

    def update(self):
        t1 = time.time()
        if len(self.messages) == 0 and ((t1 - self.t0) > 5):
            self.update_clock()
            self.t0 = time.time()
        elif len(self.messages) > 1 and (t1 - self.t0) > 2:
            self.seg.text = self.messages.pop()[0:8]
            self.t0 = time.time()



    def msg(self,mess):
        #self.messages.append(mess)
        text = mess
        self.seg.text = str(text)[0:8] # 7 seg can only display 8 digits





if __name__ == '__main__':
    print("This script should be loaded as a module.")
