# -*- coding: utf-8 -*-

from mod.common.mod import Mod
import mod.server.extraServerApi as serverApi
import mod.client.extraClientApi as clientApi


@Mod.Binding(name="RandomChestMod", version="0.0.1")
class RandomChestMod(object):

    def __init__(self):
        pass

    @Mod.InitServer()
    def RandomChestModServerInit(self):
        serverApi.RegisterSystem("RandomChestMod","RandomChestModServerSystem","RandomChestMod.RandomChestModServerSystem.RandomChestModServerSystem")
        print("服务注册成功")

    @Mod.DestroyServer()
    def RandomChestModServerDestroy(self):
        print("服务销毁成功")

    @Mod.InitClient()
    def RandomChestModClientInit(self):
        clientApi.RegisterSystem("RandomChestMod","RandomChestModClientSystem","RandomChestMod.RandomChestModClientSystem.RandomChestModClientSystem")
        print("客户注册成功")

    @Mod.DestroyClient()
    def RandomChestModClientDestroy(self):
        print("客户销毁成功")


