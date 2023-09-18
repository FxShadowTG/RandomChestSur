# -*- coding: utf-8 -*-

import mod.client.extraClientApi as clientApi
import time
import subprocess
ClientSystem = clientApi.GetClientSystemCls()
factory = clientApi.GetEngineCompFactory()

class RandomChestModClientSystem(ClientSystem):
    def __init__(self, namespace, systemName):
        ClientSystem.__init__(self, namespace, systemName)
        print("客户端准备监听")
        self.ListenEvent()
        print("客户端监听完毕")

        self.levelId = clientApi.GetLevelId()
        #进度条最大秒数设置
        self.maxSeconds = 45.0
        #初始化为none，防止bug
        self.uiNode = None
        #排行榜表
        self.topDict = []
        #当前排行榜索引
        self.index = 0

        #数字转汉字映射表
        self.numToChineseDict = {1: "一",2: "二",3: "三",4: "四",5: "五"}
        #排名颜色映射表
        self.rankColorDict = {1: "§c",2: "§6",3: "§d",4: "§b",5: "§a"}

        #获取本地玩家的id
        self.localPlayerId = clientApi.GetLocalPlayerId()
        
        #播放排行榜
        compCreateGame = factory.CreateGame(self.levelId)
        compCreateGame.AddRepeatedTimer(10.0,self.PlayTopCycle)

    def ListenEvent(self):
        #监听UI脚本完成
        self.ListenForEvent(clientApi.GetEngineNamespace(), clientApi.GetEngineSystemName(), "UiInitFinished", self, self.OnUIInitFinished)
        #监听进度条事件
        self.ListenForEvent("RandomChestMod","RandomChestModServerSystem", "ProgressBarChangeEvent", self, self.OnProgressBarChangeEvent)
        #监听排行榜数据事件
        self.ListenForEvent("RandomChestMod","RandomChestModServerSystem", "TopEvent", self, self.OnTopEvent)
        #监听显示双倍分数图标事件
        self.ListenForEvent("RandomChestMod","RandomChestModServerSystem", "VisibleDoubleScoreEvent", self, self.OnVisibleDoubleScoreEvent)
        #监听分数事件
        self.ListenForEvent("RandomChestMod","RandomChestModServerSystem", "ScoreChangeEvent", self, self.OnScoreChangeEvent)
        #监听攻击力事件
        self.ListenForEvent("RandomChestMod","RandomChestModServerSystem", "AttackChangeEvent", self, self.OnAttackChangeEvent)
        #监听血量事件
        self.ListenForEvent("RandomChestMod","RandomChestModServerSystem", "HealthChangeEvent", self, self.OnHealthChangeEvent)

    #监听UI初始化
    def OnUIInitFinished(self,args):
        clientApi.RegisterUI("RandomChestMod","RandomChestModScreenNode", "RandomChestMod.uiScript.RandomChestModScreenNode.RandomChestModScreenNode", "ui0.main")
        #客户端UI并获取UI的实例
        self.uiNode = clientApi.CreateUI("RandomChestMod","RandomChestModScreenNode",{"isHud": 1})
        #显示网易商城UI入口
        compCreateNeteaseShop = factory.CreateNeteaseShop(self.levelId)
        compCreateNeteaseShop.ShowShopGate()

    def OnProgressBarChangeEvent(self,args):
        if self.uiNode != None:
            #转换为对应进度条的进度数
            second = self.ConvertSecondsToProgress(args,45.0)   #这里直接写死，因为有bug
            #调用UI更新进度条
            self.uiNode.UpdateProgressBar(second)
            #调用UI更新进度条下方的秒数
            self.uiNode.UpdateCountTime(args)

    #监听是否显示双倍图标logo
    def OnVisibleDoubleScoreEvent(self,args):
        if self.uiNode != None and self.localPlayerId in args:
            self.uiNode.SetDoubleScoreLogoVisible(True)

    #监听排行榜事件
    def OnTopEvent(self,playerList):
        #清除原有的排行榜数据
        self.topDict = []
        #入表
        self.topDict = playerList

    #转换对应进度条的进度数
    def ConvertSecondsToProgress(self,seconds,maxSeconds):
        converted_percentage = seconds / maxSeconds
        progress_percentage = min(converted_percentage, 1)
        return progress_percentage

    #每十秒换一个名字播放
    def PlayTopCycle(self):
        if self.topDict != None and len(self.topDict) > 0:
            #转汉字
            self.uiNode.UpdateTop(self.topDict[self.index],self.numToChineseDict[self.index+1],self.rankColorDict[self.index+1])
            if self.index < len(self.topDict) - 1:
                self.index = self.index + 1
            else:
                self.index = 0

    #监听分数值变化事件
    def OnScoreChangeEvent(self,args):
        if self.uiNode != None and args != None:
            self.uiNode.UpdateScore(args[self.localPlayerId])
            comp = factory.CreatePostProcess(self.levelId)
            comp.SetEnableGaussianBlur(False)

    #监听改变攻击力事件
    def OnAttackChangeEvent(self,args):
        if self.uiNode != None:
            self.uiNode.UpdateAttack(args[self.localPlayerId])

    #监听改变血量事件
    def OnHealthChangeEvent(self,args):
        if self.uiNode != None and args != None:
            self.uiNode.UpdateHealth(args["maxHealth"][self.localPlayerId],args["health"][self.localPlayerId])

        
    def UnListenEvent(self):
        self.UnListenForEvent(clientApi.GetEngineNamespace(), clientApi.GetEngineSystemName(), "UiInitFinished", self, self.OnUIInitFinished)
        self.UnListenForEvent("RandomChestMod","RandomChestModServerSystem", "ProgressBarChangeEvent", self, self.OnProgressBarChangeEvent)
        self.UnListenForEvent("RandomChestMod","RandomChestModServerSystem", "TopEvent", self, self.OnTopEvent)
        self.UnListenForEvent("RandomChestMod","RandomChestModServerSystem", "VisibleDoubleScoreEvent", self, self.OnVisibleDoubleScoreEvent)
        self.UnListenForEvent("RandomChestMod","RandomChestModServerSystem", "ScoreChangeEvent", self, self.OnScoreChangeEvent)
        self.UnListenForEvent("RandomChestMod","RandomChestModServerSystem", "AttackChangeEvent", self, self.OnAttackChangeEvent)
        
    
    def Destroy(self):
        self.UnListenEvent()
