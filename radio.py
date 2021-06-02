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

sources = { "radio" : "https://ch02.cdn.eurozet.pl/CHIDEP.mp3",
            "noise" : "./noise.mp3" }

class MPlayer:
    radioStream = "https://ch02.cdn.eurozet.pl/CHIDEP.mp3"
    noiseFile = "./noise.mp3"
    noisePlaying = False
    radioPlaying = False

    def __init__(self):
        self.vlcInstance = vlc.Instance("--aout=pulseaudio")
        self.player = self.vlcInstance.media_player_new()


    def radio(self):
        if  MPlayer.noisePlaying == True: 
            self.player.stop()
            MPlayer.noisePlaying = False
        if  MPlayer.radioPlaying == False:
            source = self.vlcInstance.media_new(MPlayer.radioStream)
            self.player.set_media(source)
            self.player.play()
            MPlayer.radioPlaying = True
        else:
            self.player.stop()
            MPlayer.radioPlaying = False

    def noise(self):
        if  MPlayer.radioPlaying == True: 
            self.player.stop()
            MPlayer.radioPlaying = False
        if  MPlayer.noisePlaying == False:
            source = self.vlcInstance.media_new(MPlayer.noiseFile)
            self.player.set_media(source)
            self.player.play()
            MPlayer.noisePlaying = True
        else:
            self.player.stop()
            MPlayer.noisePlaying = False





