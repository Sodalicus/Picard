#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2021 Paweł Krzemiński 
#
# Distributed under terms of the MIT license.

"""

"""
import vlc
from picard_base import update_now_playing, update_volume



class Radio:

    def __init__(self):
        self.vlcInstance = vlc.Instance("--aout=pulseaudio")
        self.player = self.vlcInstance.media_player_new()
        self.nowPlaying = None
        self.volume = 0

    def play(self, source, name):
        print("self.nowPlaying: {}".format(self.nowPlaying))
        print("source, name = ({}, {})".format(source, name))
        if source:
            if (source,name)  == self.nowPlaying:
                """Stop playing if trying to play the same station again."""
                self.player.stop()
                self.nowPlaying = None
                update_now_playing(("Nothing", "None"))
                update_volume(0)
            else:
                """The source is new, play it and update db"""
                source = source
                media = self.vlcInstance.media_new(source)
                self.player.set_media(media)
                self.player.play()
                self.nowPlaying = source, name
                update_now_playing((name,source))
                update_volume(self.return_volume())
        else:
            self.player.stop()
            self.nowPlaying = None
            update_now_playing(("Nothing", "None"))
            update_volume(0)

    def stop(self):
        self.nowPlaying = None
        self.player.stop()
        update_now_playing(("Nothing", "None"))
        update_volume(0)


    def now_playing(self):
        if self.player.is_playing():
            return self.nowPlaying
        else:
            return None

    def return_volume(self):
        return self.player.audio_get_volume()

    def volume_up(self):
        currentVolume = self.return_volume()
        if currentVolume + 5 > 140:
            newVolume = 140
        else:
            newVolume = currentVolume + 5
            self.player.audio_set_volume(newVolume)
            update_volume(newVolume)

    def volume_down(self):
        currentVolume = self.return_volume()
        if currentVolume - 5 < 0:
            newVolume = 0
        else:
            newVolume = currentVolume - 5
            self.player.audio_set_volume(newVolume)
            update_volume(newVolume)


def main():
    print("This file should be loaded as a module")

if __name__ == '__main__':
    main()




