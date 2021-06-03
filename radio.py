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


class MPlayer:
    sources = { "radio" : "https://ch02.cdn.eurozet.pl/CHIDEP.mp3",
            "noise" : "./noise.mp3" }

    def __init__(self):
        self.vlcInstance = vlc.Instance("--aout=pulseaudio")
        self.player = self.vlcInstance.media_player_new()
        self.nowPlaying = None

    def play(self, srcName):
        if srcName in MPlayer.sources.keys():
            if srcName  == self.nowPlaying:
                self.player.stop()
                self.nowPlaying = None
            else:
                source = self.vlcInstance.media_new(MPlayer.sources[srcName])
                self.player.set_media(source)
                self.player.play()
                self.nowPlaying = srcName
        else:
            self.player.stop()
            self.nowPlaying = None

    def now_playing(self):
        if self.player.is_playing():
            return self.nowPlaying
        else:
            return None






