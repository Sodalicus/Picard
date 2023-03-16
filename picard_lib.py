#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2022 Paweł Krzemiński 
#
# Distributed under terms of the MIT license.

"""

"""
DEFAULTS = {
           "USE_DISPLAY":True,
           "USE_IRDA":True,
           "DBFILE":"base.db",
           "DBFILE_PATH":"./",
           "SADDRESS":"127.0.0.1",
           "SPORT":65432,
           "CADDRESS":"127.0.0.1",
           "CPORT": 5000,
           "IRDA_DEV": "/dev/input/event0",
           "ARD_USB": "/dev/ttyUSB0",
           }

SETABLES = {
           "USE_DISPLAY":"bool",
           "USE_IRDA":"bool",
           "DBFILE":"string",
           "DBFILE_PATH":"string",
           "SADDRESS":"string",
           "SPORT":"integer",
           "CADDRESS":"string",
           "CPORT": "integer",
           "IRDA_DEV": "string",
           "ARD_USB": "string",
           }

def load_config():
    config_file = "./picard.conf"
    config = DEFAULTS
    lineCount = 1
    try:
        with open(config_file) as conf:
            for line in conf.readlines():
                if line[0] == "#" or line[0] == "\n":
                #if line starts with # or newline character - omit it
                    lineCount +=1
                    continue
                data = line.rstrip("\n").split("=")
                #strip the new line character and split key and value by equals sign
                #as the result we get a list with hopefully two items
                if len(data) == 2:
                    #if we got more than two items in the list, it means there was an extra unecessary equals sign
                    dataStripped = []
                    for item in data:
                        #strip keys and values of leading and trailing whitespaces
                        dataStripped.append( item.strip())
                    key,value = dataStripped
                    if key in SETABLES.keys():
                        # Check if the given value meets the required type in general,
                        # perhaps more specific check later
                        if SETABLES[key] == "bool":
                            # is value true or false
                            if value.lower() in ["true", "false"]:
                                config[key] = value.capitalize()
                            else:
                                print("Wrong value for key: {}, in line {}. Excpected: True, or False.".format(key, lineCount))
                        elif SETABLES[key] == "integer":
                            #Try converting value to integer and catch exception if it's not.
                            try:
                                value = int(value)
                                config[key] = value
                            except ValueError:
                                print("Expected integer value for key: {}, in line {}. Got {}.".format(key, lineCount, value))
                        elif SETABLES[key] == "string":
                            #Pretty much anything can be string, and checking for logic makes no sense at this point
                            config[key] = value
                    else:
                        # key from config file is in unknown, spelling maybe, obsolete option?
                        print("Unknown option: {}, in line {}.".format(key, lineCount))
                else:
                    print("Parsing error in line {}, too many equals sings?".format(lineCount))
                lineCount += 1
    except FileNotFoundError:
        print("Configuration file not found. Running on defaults")
    return config



class DummyDisplay:
    """To use in case of no display connected."""
    def msg(self, msg):
        print("msg")
    def update_clock(self):
        pass
    def update(self):
        pass

def main():
    print("end of story")

if __name__ == '__main__':
    main()
