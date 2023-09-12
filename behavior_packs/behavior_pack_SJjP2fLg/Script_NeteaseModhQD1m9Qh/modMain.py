# -*- coding: utf-8 -*-

from mod.common.mod import Mod


@Mod.Binding(name="Script_NeteaseModhQD1m9Qh", version="0.0.1")
class Script_NeteaseModhQD1m9Qh(object):

    def __init__(self):
        pass

    @Mod.InitServer()
    def Script_NeteaseModhQD1m9QhServerInit(self):
        pass

    @Mod.DestroyServer()
    def Script_NeteaseModhQD1m9QhServerDestroy(self):
        pass

    @Mod.InitClient()
    def Script_NeteaseModhQD1m9QhClientInit(self):
        pass

    @Mod.DestroyClient()
    def Script_NeteaseModhQD1m9QhClientDestroy(self):
        pass
