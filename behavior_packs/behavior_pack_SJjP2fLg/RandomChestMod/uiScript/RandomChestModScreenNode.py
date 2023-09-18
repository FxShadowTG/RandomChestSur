# -*- coding: utf-8 -*-
import mod.client.extraClientApi as clientApi
ViewBinder = clientApi.GetViewBinderCls()
ViewRequest = clientApi.GetViewViewRequestCls()
ScreenNode = clientApi.GetScreenNodeCls()
factory = clientApi.GetEngineCompFactory()

class RandomChestModScreenNode(ScreenNode):
    def __init__(self, namespace, name, param):
        ScreenNode.__init__(self, namespace, name, param)
        print("客户端UI init...")

        self.levelId = clientApi.GetLevelId()

    #创建UI
    def Create(self):
        self.baseUIControl = self.GetBaseUIControl("/panel")
        self.baseUIControl.SetVisible(True, True)

        self.progressBarControl = self.baseUIControl.GetChildByName("progress_bar").asProgressBar()
        self.countdownTimeControl = self.baseUIControl.GetChildByName("progress_bar/countdownTime").asLabel()
        self.scoreControl = self.baseUIControl.GetChildByName("scoreLogo/score").asLabel()
        self.doubleScoreLogoControl = self.baseUIControl.GetChildByName("scoreLogo/doubleScoreLogo").asImage()
        self.attackControl = self.baseUIControl.GetChildByName("attackLogo/attack").asLabel()
        self.healthControl = self.baseUIControl.GetChildByName("healthLogo/health").asLabel()

        #较特殊，这里可改可不改
        self.GetBaseUIControl("/panel/topButton").asButton().AddTouchEventParams()
        self.GetBaseUIControl("/panel/topButton").asButton().SetButtonTouchDownCallback(self.topButtonClick)
        self.topNameControl = self.GetBaseUIControl("/panel/topButton/topName").asLabel()
        #默认显示排行榜
        self.topNameControl.SetVisible(True,True)
        #默认隐藏双倍分数图标
        self.doubleScoreLogoControl.SetVisible(False,False)
        print("Create OK")

    #今日最佳按钮回调
    def topButtonClick(self,args):
        #隐藏或显示文字
        result = self.topNameControl.GetVisible()
        if result == False:
            self.topNameControl.SetVisible(True)
        else :
            self.topNameControl.SetVisible(False)
        # compCreateGame = factory.CreateGame(self.levelId)
        # width, height = compCreateGame.GetScreenSize()
        # print("{},{}".format(width,height))
        # ret = self.baseUIControl.SetFullPosition(axis="x", paramDict={"followType":"y", "absoluteValue":0})
        # ret = self.baseUIControl.SetFullPosition(axis="y", paramDict={"followType":"x", "absoluteValue":height})

    #设置双倍分数logo是否显示
    def SetDoubleScoreLogoVisible(self,bool):
        self.doubleScoreLogoControl.SetVisible(bool,bool)

    #改变进度条的进度（只需要提供1-45的数字，本函数自动转换为小数点）
    def UpdateProgressBar(self,second):
        self.progressBarControl.SetValue(second)
        comp = clientApi.GetEngineCompFactory().CreateGame(self.levelId)

    #改变排行榜数据（只支持前五）
    def UpdateTop(self,player,rank,color):
        # self.topNameControl.SetText("第" + rank + ": " + player["nickname"] + "\n" + "分数: " + str(player["value"]))
        self.topNameControl.SetText("{0}第{1}: {2}\n§f分数: {3}".format(color,rank,player["nickname"],str(player["value"])))

    #改变进度条下方的剩余秒数
    def UpdateCountTime(self,second):
        self.countdownTimeControl.SetText("刷新 : " + str(int(second)))

    #改变分数
    def UpdateScore(self,score):
        self.scoreControl.SetText(str(int(score)) + " : 我的分数")

    #改变攻击力
    def UpdateAttack(self,attack):
        self.attackControl.SetText("+ " + str(int(attack)))

    #改变血量
    def UpdateHealth(self,maxHealth,health):
        self.healthControl.SetText("+ " + str(int(maxHealth)) + " (" + str(int(health)) + ")")

    def Destroy(self):
        pass

    def OnActive(self):
        """
        @description UI重新回到栈顶时调用
        """
        pass

    def OnDeactive(self):
        """
        @description 栈顶UI有其他UI入栈时调用
        """
        pass
