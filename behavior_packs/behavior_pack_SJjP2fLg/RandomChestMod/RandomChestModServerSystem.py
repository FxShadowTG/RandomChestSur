# -*- coding: utf-8 -*-

import mod.server.extraServerApi as serverApi
import random
import json
from math import floor
ServerSystem = serverApi.GetServerSystemCls()
factory = serverApi.GetEngineCompFactory()

class RandomChestModServerSystem(ServerSystem):
    def __init__(self, namespace, systemName):
        ServerSystem.__init__(self, namespace, systemName)
        print("服务器准备监听")
        self.ListenEvent()
        print("服务器监听完毕")

        self.levelId = serverApi.GetLevelId()
        self.compCreateCommand = factory.CreateCommand(self.levelId)

        #添加方块白名单（ServerBlockUseEvent）
        compCreateBlockUseEventWhiteList = factory.CreateBlockUseEventWhiteList(self.levelId)
        compCreateBlockUseEventWhiteList.AddBlockItemListenForUseEvent("minecraft:end_stone:*")
        compCreateBlockUseEventWhiteList.AddBlockItemListenForUseEvent("minecraft:grass:*")
        compCreateBlockUseEventWhiteList.AddBlockItemListenForUseEvent("minecraft:bell:*")

        #self.DEBUG开关
        self.DEBUG = False

        #pvp临时开关（由玩家决定），默认为True
        #解释：玩家输入"pvp 关"时，将关闭pvp15分钟，时间到后自动重新开启pvp
        self.pvp = True
        #pvp开关倒计时
        self.pvpCountdown = 0

        #后台白名单
        self.whiteList = ["残幻影","活宝宝宝呀"]

        #玩家列表
        self.playerList = []
        #双倍分数玩家列表
        self.playerDoubleScoreList = []
        #敲钟复制方块列表
        self.playerWealthBellList = []
        #玩家分数词典
        self.playerScoreDict = {}
        #玩家攻击力词典
        self.playerAttackDict = {}
        #倒计时数(暂定45.0)
        self.roomCountdown = 45.0
        #当前排行榜数据
        self.topDict = []
        #初始化世界
        self.InitWorldOptions()
        #定义宝箱刷新点
        self.aPos = (-9.5, 1, -9.5)
        self.bPos = (9.5, 1, 9.5)
        #定义宝箱名列表
        self.chestNameDict =    {"tpkth:common_chest_lv1": "§l§aLV.1§f - §f普通宝箱怪","tpkth:common_chest_lv2": "§l§aLV.2§f - §f普通宝箱怪",
                                "tpkth:common_chest_lv3": "§l§aLV.3§f - §f普通宝箱怪","tpkth:common_chest_lv4": "§l§aLV.4§f - §f普通宝箱怪",
                                "tpkth:common_chest_lv5": "§l§aLV.5§f - §f普通宝箱怪","tpkth:common_chest_lv6": "§l§aLV.6§f - §f普通宝箱怪",
                                "tpkth:common_chest_lv7": "§l§aLV.7§f - §f普通宝箱怪","tpkth:common_chest_lv8": "§l§aLV.8§f - §f普通宝箱怪",
                                "tpkth:common_chest_lv9": "§l§aLV.9§f - §f普通宝箱怪","tpkth:common_chest_lv10": "§l§aLV.10§f - §f普通宝箱怪",
                                "tpkth:coal_chest_lv11": "§l§aLV.11§f - §b碳物质宝箱怪","tpkth:coal_chest_lv12": "§l§aLV.12§f - §b碳物质宝箱怪",
                                "tpkth:coal_chest_lv13": "§l§aLV.13§f - §b碳物质宝箱怪","tpkth:coal_chest_lv14": "§l§aLV.14§f - §b碳物质宝箱怪",
                                "tpkth:coal_chest_lv15": "§l§aLV.15§f - §b碳物质宝箱怪","tpkth:coal_chest_lv16": "§l§aLV.16§f - §b碳物质宝箱怪",
                                "tpkth:coal_chest_lv17": "§l§aLV.17§f - §b碳物质宝箱怪","tpkth:coal_chest_lv18": "§l§aLV.18§f - §b碳物质宝箱怪",
                                "tpkth:coal_chest_lv19": "§l§aLV.19§f - §b碳物质宝箱怪","tpkth:coal_chest_lv20": "§l§aLV.20§f - §b碳物质宝箱怪",
                                "tpkth:mushroom_chest": "§l§aLV.35§f - §2蘑菇宝箱怪","tpkth:rainbow_chest": "§l§aLV.??§f - §c彩§e虹§b宝§a箱§d召§6唤§4物",

                                "tpkth:golden_chest_lv21": "§l§aLV.21§f - §e鎏金宝箱怪","tpkth:golden_chest_lv22": "§l§aLV.22§f - §e鎏金宝箱怪",
                                "tpkth:golden_chest_lv23": "§l§aLV.23§f - §e鎏金宝箱怪","tpkth:golden_chest_lv24": "§l§aLV.24§f - §e鎏金宝箱怪",
                                "tpkth:golden_chest_lv25": "§l§aLV.25§f - §e鎏金宝箱怪","tpkth:golden_chest_lv26": "§l§aLV.26§f - §e鎏金宝箱怪",
                                "tpkth:golden_chest_lv27": "§l§aLV.27§f - §e鎏金宝箱怪","tpkth:golden_chest_lv28": "§l§aLV.28§f - §e鎏金宝箱怪",
                                "tpkth:golden_chest_lv29": "§l§aLV.29§f - §e鎏金宝箱怪","tpkth:golden_chest_lv30": "§l§aLV.30§f - §e鎏金宝箱怪",
                                "tpkth:iron_chest_lv40": "§l§aLV.40§f - §d铁皮宝箱怪","tpkth:diamond_chest_lv50":"§l§aLV.50§f - §6钻石宝箱怪",
                                "tpkth:obsidian_chest_lv60":"§l§aLV.60§f - §0黑曜石宝箱怪","tpkth:emerald_chest_lv70":"§l§aLV.70§f - §a绿宝石宝箱怪",
                                "tpkth:night_chest_lv80":"§l§aLV.80§f - §c暗夜宝箱怪","tpkth:health_chest_lv20":"§l§aLV.20§f - §a生命宝箱怪",  #本行第二个元素开始为环境宝箱怪系列
                                "tpkth:lava_chest_lv40":"§l§aLV.40§f - §c熔岩宝箱怪","tpkth:jungle_chest_lv30":"§l§aLV.30§f - §2丛林宝箱怪",
                                "tpkth:ocean_chest_lv40":"§l§aLV.40§f - §b海洋宝箱怪"}
        
        #特殊领域宝箱列表（此处的宝箱不会加入刷新列表）
        self.chestEnvDict = {"tpkth:mummy_chest": "§l§aLV.50§f - §f木乃伊宝箱怪","tpkth:evil_chest": "§l§aLV.70§f - §d邪恶宝箱怪",}

        #定义宝箱分数列表
        self.chestScoreDict =    {"tpkth:common_chest_lv1": "1","tpkth:common_chest_lv2": "1",
                                "tpkth:common_chest_lv3": "1","tpkth:common_chest_lv4": "1",
                                "tpkth:common_chest_lv5": "1","tpkth:common_chest_lv6": "1",
                                "tpkth:common_chest_lv7": "1","tpkth:common_chest_lv8": "1",
                                "tpkth:common_chest_lv9": "1","tpkth:common_chest_lv10": "1",
                                "tpkth:coal_chest_lv11": "2","tpkth:coal_chest_lv12": "2",
                                "tpkth:coal_chest_lv13": "2","tpkth:coal_chest_lv14": "2",
                                "tpkth:coal_chest_lv15": "2","tpkth:coal_chest_lv16": "2",
                                "tpkth:coal_chest_lv17": "2","tpkth:coal_chest_lv18": "2",
                                "tpkth:coal_chest_lv19": "2","tpkth:coal_chest_lv20": "2",
                                "tpkth:golden_chest_lv21": "3","tpkth:golden_chest_lv22": "3",
                                "tpkth:golden_chest_lv23": "3","tpkth:golden_chest_lv24": "3",
                                "tpkth:golden_chest_lv25": "3","tpkth:golden_chest_lv26": "3",
                                "tpkth:golden_chest_lv27": "3","tpkth:golden_chest_lv28": "3",
                                "tpkth:golden_chest_lv29": "3","tpkth:golden_chest_lv30": "3",
                                "tpkth:iron_chest_lv40": "4","tpkth:diamond_chest_lv50":"5",
                                "tpkth:obsidian_chest_lv60":"6","tpkth:emerald_chest_lv70":"7",
                                "tpkth:night_chest_lv80":"8","tpkth:health_chest_lv20":"4",#本行第二个元素开始为环境宝箱怪系列
                                "tpkth:lava_chest_lv40":"4","tpkth:jungle_chest_lv30":"4",
                                "tpkth:ocean_chest_lv40":"4","tpkth:mushroom_chest": "4",
                                "tpkth:mummy_chest": "4","tpkth:evil_chest": "4",
                                "tpkth:rainbow_chest": "16"}  
        #定义随机方块列表
        self.randomBlockList = ["acacia_button","acacia_door","acacia_fence_gate","acacia_pressure_plate","acacia_stairs","acacia_standing_sign","acacia_trapdoor","acacia_wall_sign","activator_rail","air","allow","amethyst_block","amethyst_cluster","ancient_debris","andesite_stairs","anvil","azalea","azalea_leaves","azalea_leaves_flowered","bamboo","bamboo_mosaic_double_slab","bamboo_sapling","barrel","barrier","basalt","beacon","bed","bedrock","bee_nest","beehive","beetroot","bell","big_dripleaf","birch_button","birch_door","birch_fence_gate","birch_pressure_plate","birch_stairs","birch_standing_sign","birch_trapdoor","birch_wall_sign","black_candle","black_candle_cake","black_glazed_terracotta","black_stained_glass_pane","blackstone","blackstone_double_slab","blackstone_slab","blackstone_stairs","blackstone_wall","blast_furnace","blue_candle","blue_candle_cake","blue_glazed_terracotta","blue_ice","blue_stained_glass_pane","bone_block","bookshelf","border_block","brewing_stand","brick_block","brick_stairs","brown_candle","brown_candle_cake","brown_glazed_terracotta","brown_mushroom","brown_mushroom_block","brown_stained_glass_pane","bubble_column","budding_amethyst","cactus","cake","calcite","campfire","candle","candle_cake","carrots","cartography_table","carved_pumpkin","cauldron","cave_vines","cave_vines_body_with_berries","cave_vines_head_with_berries","chain","chain_command_block","chest","chiseled_deepslate","chiseled_nether_bricks","chiseled_polished_blackstone","chorus_flower","chorus_plant","clay","coal_block","coal_ore","cobbled_deepslate","cobbled_deepslate_double_slab","cobbled_deepslate_slab","cobbled_deepslate_stairs","cobbled_deepslate_wall","cobblestone","cobblestone_wall","cocoa","command_block","composter","conduit","copper_block","copper_ore","coral_block","coral_fan","coral_fan_dead","coral_fan_hang","coral_fan_hang2","coral_fan_hang3","cracked_deepslate_bricks","cracked_deepslate_tiles","cracked_nether_bricks","cracked_polished_blackstone_bricks","crafting_table","crimson_button","crimson_door","crimson_double_slab","crimson_fence","crimson_fence_gate","crimson_fungus","crimson_hyphae","crimson_nylium","crimson_planks","crimson_pressure_plate","crimson_roots","crimson_slab","crimson_stairs","crimson_standing_sign","crimson_stem","crimson_trapdoor","crimson_wall_sign","crying_obsidian","cut_copper","cut_copper_slab","cut_copper_stairs","cyan_candle","cyan_candle_cake","cyan_glazed_terracotta","cyan_stained_glass_pane","dark_oak_button","dark_oak_door","dark_oak_fence_gate","dark_oak_hanging_sign","dark_oak_pressure_plate","dark_oak_stairs","dark_oak_trapdoor","dark_prismarine_stairs","darkoak_standing_sign","darkoak_wall_sign","daylight_detector","daylight_detector_inverted","deadbush","deepslate","deepslate_brick_double_slab","deepslate_brick_slab","deepslate_brick_stairs","deepslate_brick_wall","deepslate_bricks","deepslate_coal_ore","deepslate_copper_ore","deepslate_diamond_ore","deepslate_emerald_ore","deepslate_gold_ore","deepslate_iron_ore","deepslate_lapis_ore","deepslate_redstone_ore","deepslate_tile_double_slab","deepslate_tile_slab","deepslate_tile_stairs","deepslate_tile_wall","deepslate_tiles","deny","detector_rail","diamond_block","diamond_ore","diorite_stairs","dirt","dirt_with_roots","dispenser","double_cut_copper_slab","double_plant","double_stone_block_slab","double_stone_block_slab2","double_stone_block_slab4","double_wooden_slab","dragon_egg","dried_kelp_block","dripstone_block","dropper","emerald_block","emerald_ore","enchanting_table","end_brick_stairs","end_bricks","end_portal","end_portal_frame","end_rod","end_stone","ender_chest","exposed_copper","exposed_cut_copper","exposed_cut_copper_slab","exposed_cut_copper_stairs","exposed_double_cut_copper_slab","farmland","fence_gate","fire","fletching_table","flower_pot","flowering_azalea","flowing_lava","flowing_water","frame","frosted_ice","furnace","gilded_blackstone","glass","glass_pane","glow_frame","glow_lichen","glowstone","gold_block","gold_ore","golden_rail","granite_stairs","grass","grass_path","gravel","gray_candle","gray_candle_cake","gray_glazed_terracotta","gray_stained_glass_pane","green_candle","green_candle_cake","green_glazed_terracotta","green_stained_glass_pane","grindstone","hanging_roots","hardened_clay","hay_block","heavy_weighted_pressure_plate","honey_block","honeycomb_block","hopper","ice","infested_deepslate","iron_bars","iron_block","iron_door","iron_ore","iron_trapdoor","jukebox","jungle_button","jungle_door","jungle_fence_gate","jungle_pressure_plate","jungle_stairs","jungle_standing_sign","jungle_trapdoor","jungle_wall_sign","kelp","ladder","lantern","lapis_block","lapis_ore","large_amethyst_bud","lava","leaves","leaves2","lectern","lever","light_block","light_blue_candle","light_blue_candle_cake","light_blue_concrete_powder","light_blue_glazed_terracotta","light_blue_shulker_box","light_blue_stained_glass","light_blue_stained_glass_pane","light_gray_candle","light_gray_candle_cake","light_gray_concrete_powder","light_gray_shulker_box","light_gray_stained_glass","light_gray_stained_glass_pane","light_weighted_pressure_plate","lightning_rod","lime_candle","lime_candle_cake","lime_glazed_terracotta","lime_stained_glass_pane","lit_blast_furnace","lit_deepslate_redstone_ore","lit_furnace","lit_pumpkin","lit_redstone_lamp","lit_redstone_ore","lit_smoker","lodestone","loom","magenta_candle","magenta_candle_cake","magenta_glazed_terracotta","magenta_stained_glass_pane","magma","medium_amethyst_bud","melon_block","melon_stem","mob_spawner","monster_egg","moss_block","moss_carpet","mossy_cobblestone","mossy_cobblestone_stairs","mossy_stone_brick_stairs","mycelium","nether_brick","nether_brick_fence","nether_brick_stairs","nether_gold_ore","nether_sprouts","nether_wart","nether_wart_block","netherite_block","netherrack","normal_stone_stairs","noteblock","oak_stairs","observer","obsidian","orange_candle","orange_candle_cake","orange_glazed_terracotta","orange_stained_glass_pane","oxidized_copper","oxidized_cut_copper","oxidized_cut_copper_slab","oxidized_cut_copper_stairs","oxidized_double_cut_copper_slab","packed_ice","pink_candle","pink_candle_cake","pink_glazed_terracotta","pink_stained_glass_pane","piston","planks","podzol","pointed_dripstone","polished_andesite_stairs","polished_basalt","polished_blackstone","polished_blackstone_brick_double_slab","polished_blackstone_brick_slab","polished_blackstone_brick_stairs","polished_blackstone_brick_wall","polished_blackstone_bricks","polished_blackstone_button","polished_blackstone_double_slab","polished_blackstone_pressure_plate","polished_blackstone_slab","polished_blackstone_stairs","polished_blackstone_wall","polished_deepslate","polished_deepslate_double_slab","polished_deepslate_slab","polished_deepslate_stairs","polished_deepslate_wall","polished_diorite_stairs","polished_granite_stairs","portal","potatoes","powder_snow","powered_comparator","powered_repeater","prismarine","prismarine_bricks_stairs","prismarine_stairs","pumpkin","pumpkin_stem","purple_candle","purple_candle_cake","purple_glazed_terracotta","purple_stained_glass_pane","purpur_block","purpur_stairs","quartz_block","quartz_bricks","quartz_ore","quartz_stairs","rail","raw_copper_block","raw_gold_block","raw_iron_block","red_candle","red_candle_cake","red_flower","red_glazed_terracotta","red_mushroom","red_mushroom_block","red_nether_brick","red_nether_brick_stairs","red_sandstone","red_sandstone_stairs","red_stained_glass_pane","redstone_block","redstone_lamp","redstone_ore","redstone_torch","redstone_wire","reeds","repeating_command_block","respawn_anchor","sand","sandstone","sandstone_stairs","sapling","scaffolding","sea_pickle","seagrass","shroomlight","silver_glazed_terracotta","skull","slime","small_amethyst_bud","small_dripleaf_block","smithing_table","smoker","smooth_basalt","smooth_quartz_stairs","smooth_red_sandstone_stairs","smooth_sandstone_stairs","smooth_stone","snow","snow_layer","soul_campfire","soul_fire","soul_lantern","soul_sand","soul_soil","soul_torch","sponge","spore_blossom","spruce_button","spruce_door","spruce_fence_gate","spruce_pressure_plate","spruce_stairs","spruce_standing_sign","spruce_trapdoor","spruce_wall_sign","standing_banner","standing_sign","sticky_piston","stone","stone_brick_stairs","stone_button","stone_pressure_plate","stone_stairs","stonebrick","stonecutter_block","stripped_acacia_log","stripped_bamboo_block","stripped_birch_log","stripped_crimson_hyphae","stripped_crimson_stem","stripped_dark_oak_log","stripped_jungle_log","stripped_oak_log","stripped_spruce_log","stripped_warped_hyphae","stripped_warped_stem","structure_block","structure_void","sweet_berry_bush","tallgrass","target","tinted_glass","tnt","torch","trapdoor","trapped_chest","tripwire_hook","tuff","turtle_egg","twisting_vines","undyed_shulker_box","unlit_redstone_torch","unpowered_comparator","unpowered_repeater","vine","wall_banner","wall_sign","warped_button","warped_door","warped_double_slab","warped_fence","warped_fence_gate","warped_fungus","warped_hyphae","warped_nylium","warped_planks","warped_pressure_plate","warped_roots","warped_slab","warped_stairs","warped_standing_sign","warped_stem","warped_trapdoor","warped_wall_sign","warped_wart_block","water","waterlily","waxed_copper","waxed_cut_copper","waxed_cut_copper_slab","waxed_cut_copper_stairs","waxed_double_cut_copper_slab","waxed_exposed_copper","waxed_exposed_cut_copper","waxed_exposed_cut_copper_slab","waxed_exposed_cut_copper_stairs","waxed_exposed_double_cut_copper_slab","waxed_oxidized_copper","waxed_oxidized_cut_copper","waxed_oxidized_cut_copper_slab","waxed_oxidized_cut_copper_stairs","waxed_oxidized_double_cut_copper_slab","waxed_weathered_copper","waxed_weathered_cut_copper","waxed_weathered_cut_copper_slab","waxed_weathered_cut_copper_stairs","waxed_weathered_double_cut_copper_slab","weathered_copper","weathered_cut_copper","weathered_cut_copper_slab","weathered_cut_copper_stairs","weathered_double_cut_copper_slab","web","weeping_vines","wheat","white_candle","white_candle_cake","white_glazed_terracotta","white_stained_glass_pane","wither_rose","wood","wooden_button","wooden_door","wooden_pressure_plate","wooden_slab","yellow_candle","yellow_candle_cake","yellow_flower","yellow_glazed_terracotta","yellow_stained_glass_pane"]

        #方块过滤表
        self.blockFilterList = ["minecraft:end_stone","minecraft:grass","minecraft:bell","tpkth:coalchangeblock"]
        # #发货映射表(取消通过映射表发货，因为正式环境有奇怪的bug)
        # self.sendGoodsRelationDict = {
        #     "buySmallChest": self.buySmallChest,
        #     "buyBigChest": self.buyBigChest,
        #     "buyStaffChest": self.buyStaffChest,
        #     "buyScoreMachine": self.buyScoreMachine,
        #     "buyCommonBit": self.buyCommonBit,
        #     "buyAlloyBit": self.buyAlloyBit,
        # }
        
    #更改世界的属性值
    def InitWorldOptions(self):
        #修改伤害CD为最低帧数
        self.compCreateGame = factory.CreateGame(self.levelId)
        self.compCreateGame.SetHurtCD(5)
        #设置实体上限
        serverApi.SetEntityLimit(300)
        #设置游戏难度
        self.compCreateGame.SetGameDifficulty(3)
        #设置游戏规则
        gameRuleDict ={
        'option_info': {
            'pvp': True, #玩家伤害
            'show_coordinates': True, #显示坐标
            'fire_spreads': True, #火焰蔓延
            'tnt_explodes': True, #tnt爆炸
            'mob_loot': True, #生物战利品
            'natural_regeneration': True, #自然生命恢复
            'tile_drops': True, #方块掉落
            'immediate_respawn':False #立即重生
            },
        'cheat_info': {
            'enable': False, #是否开启作弊
            'mob_griefing': True, #生物破坏方块
            'keep_inventory': True, #保留物品栏
            'weather_cycle': True, #天气更替
            'mob_spawn': True, #生物生成
            'entities_drop_loot': True, #实体掉落
            'daylight_cycle': True, #开启昼夜交替
            'command_blocks_enabled': True, #启用方块命令
            }
        }
        self.compCreateGame.SetGameRulesInfoServer(gameRuleDict)

        #禁止物品
        if not self.DEBUG:
            compCreateItemBanned = factory.CreateItemBanned(self.levelId)
            compCreateItemBanned.AddBannedItem("minecraft:bedrock")
            compCreateItemBanned.AddBannedItem("minecraft:deny")
            compCreateItemBanned.AddBannedItem("minecraft:allow")
            compCreateItemBanned.AddBannedItem("tpkth:baseChestPointBlock")
            compCreateItemBanned.AddBannedItem("tpkth:baseHornChestPointBlock")
            compCreateItemBanned.AddBannedItem("tpkth:baseHornChestPointBlock2")
            compCreateItemBanned.AddBannedItem("tpkth:baseHornChestPointBlock3")
            compCreateItemBanned.AddBannedItem("tpkth:baseHornChestPointBlock4")
            compCreateItemBanned.AddBannedItem("tpkth:baseLineChestPointBlock")
            compCreateItemBanned.AddBannedItem("tpkth:baseLineChestPointBlock2")
            compCreateItemBanned.AddBannedItem("tpkth:baseLineChestPointBlock3")
            compCreateItemBanned.AddBannedItem("tpkth:baseLineChestPointBlock4")
            compCreateItemBanned.AddBannedItem("tpkth:chestPointBlock")

        #开始计时
        self.compCreateGame.AddRepeatedTimer(1.0,self.Countdown)
        #开始deop
        self.compCreateGame.AddRepeatedTimer(1.0,self.Deop)

        #开始给周围宝箱命名
        self.compCreateGame.AddRepeatedTimer(1.0,self.NameAroundChest)
        #轮询更新 C/S UI
        self.compCreateGame.AddRepeatedTimer(1.0,self.NotifyClientForUpdateUICycle)

    #开始监听
    def ListenEvent(self):
        self.ListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(), "AddServerPlayerEvent", self, self.OnAddServerPlayerEvent)
        self.ListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(), "PlayerAttackEntityEvent", self, self.OnPlayerAttackEntityEvent)
        self.ListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(), "MobDieEvent", self, self.OnMobDieEvent)
        self.ListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(), "PlayerIntendLeaveServerEvent", self, self.OnPlayerIntendLeaveServerEvent)
        self.ListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(), "PlayerAttackEntityEvent", self, self.OnPlayerAttackEntityEvent)
        self.ListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(), "ActuallyHurtServerEvent", self, self.OnActuallyHurtServerEvent)
        self.ListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(), "ServerBlockUseEvent", self, self.OnServerBlockUseEvent)
        self.ListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(), "lobbyGoodBuySucServerEvent", self, self.OnlobbyGoodBuySucServerEvent)
        self.ListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(), "DestroyBlockEvent", self, self.OnDestroyBlockEvent)
        self.ListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(), "ServerChatEvent", self, self.OnServerChatEvent)
        self.ListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(), "GameTypeChangedServerEvent", self, self.OnGameTypeChangedServerEvent)
    
    #退出监听
    def UnListenEvent(self):
        self.UnListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(), "AddServerPlayerEvent", self, self.OnAddServerPlayerEvent)
        self.UnListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(), "PlayerAttackEntityEvent", self, self.OnPlayerAttackEntityEvent)
        self.UnListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(), "MobDieEvent", self, self.OnMobDieEvent)
        self.UnListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(), "PlayerIntendLeaveServerEvent", self, self.OnPlayerIntendLeaveServerEvent)
        self.UnListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(), "PlayerAttackEntityEvent", self, self.OnPlayerAttackEntityEvent)
        self.UnListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(), "ActuallyHurtServerEvent", self, self.OnActuallyHurtServerEvent)
        self.UnListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(), "ServerBlockUseEvent", self, self.OnServerBlockUseEvent)
        self.UnListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(), "lobbyGoodBuySucServerEvent", self, self.OnlobbyGoodBuySucServerEvent)
        self.UnListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(), "DestroyBlockEvent", self, self.OnDestroyBlockEvent)
        self.UnListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(), "ServerChatEvent", self, self.OnServerChatEvent)
        self.UnListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(), "GameTypeChangedServerEvent", self, self.OnGameTypeChangedServerEvent)
        
    def Destroy(self):
        self.UnListenEvent()

    #防作弊
    def Deop(self):
        #清除所有人的op
        if not self.DEBUG:
            self.compCreateCommand.SetCommand("/deop @a")

    #玩家进入联机大厅时
    def OnlobbyGoodBuySucServerEvent(self,args):
        print("lobbyGoodBuySucServerEvent:")
        print(args)
        #如果玩家购买商品(eid: 玩家实体id，buyItem: 商品ID)
        if args["eid"] != None and args["buyItem"] != False:
            print("玩家购买商品")
            self.ActionUserItem(args["eid"])
        #如果为进入大厅
        elif args["eid"] != None and args["buyItem"] == False:
            #初始化装备
            eid = args["eid"]
            #获取玩家云分数并自动更新
            self.GetPlayerScore(eid)
            #获取最新排行榜
            self.GetTop()
            #获取玩家是否有双倍分数仪并自动添加
            self.GetStorageScoreMachine(eid)
            #获取玩家是否有财富之钟并自动添加
            self.GetStorageBell(eid)
            #获取玩家是否有普通钻头并自动添加和标记
            self.GetStorageBit(eid,"commonBit")
            #获取玩家是否有合金钻头并自动添加和标记
            self.GetStorageBit(eid,"alloyBit")

    #模式改变时（反作弊）
    def OnGameTypeChangedServerEvent(self,args):
        print(args)
        playerId = args["playerId"]
        compCreateName = factory.CreateName(playerId)
        name = compCreateName.GetName()

        #改模式并踢掉
        if args["newGameType"] == 1 and name not in self.whiteList:
            self.compCreateCommand.SetCommand("/gamemode 0 " + name)
            self.compCreateCommand.SetCommand("/kick " + name)
            print("有玩家改模式并且被踢掉")

    #给周围宝箱命名
    def NameAroundChest(self):
        for playerId in self.playerList:
            entityList = self.compCreateGame.GetEntitiesAround(playerId, 50, None)
        for entityId in entityList:
        #设置宝箱名字
            compCreateEngineType = factory.CreateEngineType(entityId)
            entityName = compCreateEngineType.GetEngineTypeStr()
            if entityName in self.chestNameDict:
                compCreateName = factory.CreateName(entityId)
                name = self.chestNameDict[entityName]
                compCreateName.SetName(name)
            elif entityName in self.chestEnvDict:
                compCreateName = factory.CreateName(entityId)
                name = self.chestEnvDict[entityName]
                compCreateName.SetName(name)
    #当玩家聊天时
    def OnServerChatEvent(self,args):
        username = args["username"]
        playerId = args["playerId"]
        message = args["message"]
        #作者后台命令
        if username in self.whiteList and message[0] == "#":
            message = message.replace("#", "")
            self.compCreateCommand.SetCommand("/" + message,playerId)
            args["cancel"]
            return
        if message == "pvp 关" and self.pvp == True:
            self.pvp = False

            pvpDict ={
            'option_info': {
                'pvp': self.pvp
                },
            }
            self.compCreateGame.SetGameRulesInfoServer(pvpDict)
            self.compCreateGame.SetNotifyMsg("pvp已被关闭,15分钟后自动恢复", serverApi.GenerateColor('GREEN'))
            #开始pvp重新开启的倒计时
            self.pvpCountdown = 900
            self.PVPTimer = self.compCreateGame.AddRepeatedTimer(1.0,self.PVPCountdown)
        elif  message == "难度 简单":
            self.compCreateGame.SetGameDifficulty(1)
            self.compCreateGame.SetNotifyMsg("难度已被设置为 简单", serverApi.GenerateColor('GREEN'))
        elif  message == "难度 普通":
            self.compCreateGame.SetGameDifficulty(2)
            self.compCreateGame.SetNotifyMsg("难度已被设置为 普通", serverApi.GenerateColor('GREEN'))
        elif  message == "难度 困难":
            self.compCreateGame.SetGameDifficulty(3)
            self.compCreateGame.SetNotifyMsg("难度已被设置为 困难", serverApi.GenerateColor('GREEN'))
            
    def PVPCountdown(self):
        if self.pvpCountdown > 0:
            self.pvpCountdown = self.pvpCountdown - 1
        else:
            self.pvpCountdown = 0
            #重新开启pvp
            self.pvp = True
            self.compCreateGame.CancelTimer(self.PVPTimer)

            pvpDict ={
            'option_info': {
                'pvp': self.pvp
                },
            }
            self.compCreateGame.SetGameRulesInfoServer(pvpDict)
            self.compCreateGame.SetNotifyMsg("pvp已自动开启", serverApi.GenerateColor('RED'))

    #将玩家加入进在线玩家列表
    def OnAddServerPlayerEvent(self,args):
        print(args)
        playerId = args["id"]
        self.playerList.append(playerId)

        #作者后台设定
        compCreateName = factory.CreateName(playerId)
        name = compCreateName.GetName()
        if name in self.whiteList:
            self.compCreateCommand.SetCommand("/say §a有帅哥进入了房间",playerId)

        #设置默认模式
        #设置生存模式为默认游戏模式
        self.compCreateGame.SetDefaultGameType(0)
        #设置为生存模式
        compCreatePlayer = factory.CreatePlayer(playerId)
        compCreatePlayer.SetPlayerGameType(serverApi.GetMinecraftEnum().GameType.Survival)
        #设置暂定默认值
        self.playerScoreDict[playerId] = -1
        self.playerAttackDict[playerId] = -1

        if self.DEBUG:
            #获取玩家云分数并自动更新
            self.GetPlayerScore(playerId)
            #获取最新排行榜
            self.GetTop()
            #获取玩家是否有双倍分数仪并自动添加
            self.GetStorageScoreMachine(playerId)
            #获取玩家是否有财富之钟并自动添加
            self.GetStorageBell(playerId)
            #获取玩家是否有普通钻头并自动添加和标记
            self.GetStorageBit(playerId,"commonBit")
            #获取玩家是否有合金钻头并自动添加和标记
            self.GetStorageBit(playerId,"alloyBit")

    #玩家退出前执行的操作
    def OnPlayerIntendLeaveServerEvent(self,args):
        playerId = args["playerId"]
        #上传云分数数据
        self.UpLoadPlayerScore(playerId)

         #删除玩家列表
        if playerId in self.playerList:
            self.playerList.remove(playerId)

        #删除该玩家分数词典
        if playerId in self.playerScoreDict:
            del self.playerScoreDict[playerId]

        #删除该玩家攻击力词典
        if playerId in self.playerAttackDict:
            del self.playerAttackDict[playerId]

        #删除玩家双倍分数列表
        if playerId in self.playerDoubleScoreList:
            self.playerDoubleScoreList.remove(playerId)
            
        #删除玩家财富之钟列表
        if playerId in self.playerWealthBellList:
            self.playerWealthBellList.remove(playerId)

    #查询并执行发货指令
    def ActionUserItem(self,playerId):
        #查询未发货的订单
        compCreateHttp = factory.CreateHttp(self.levelId)
        uid = compCreateHttp.GetPlayerUid(playerId)
        def cb(data):
            if data:
                ordersDict = data["entity"]["orders"]
                for order in ordersDict:
                    print("order:",order)
                    #根据订单请求实现发货
                    if order["cmd"] == "buySmallChest":
                        self.buySmallChest(playerId)
                    elif order["cmd"] == "buyBigChest":
                        self.buyBigChest(playerId)
                    elif order["cmd"] == "buyStaffChest":
                        self.buyStaffChest(playerId)
                    elif order["cmd"] == "buyScoreMachine":
                        self.buyBigChest(playerId)
                    elif order["cmd"] == "buyCommonBit":
                        self.buyCommonBit(playerId)
                    elif order["cmd"] == "buyAlloyBit":
                        self.buyAlloyBit(playerId)
                    elif order["cmd"] == "buyWealthBell":
                        self.buyWealthBell(playerId)
                    elif order["cmd"] == "buyFreeChest":
                        self.buyFreeChest(playerId)
                    #标记已发货（不管是否成功都直接标记为已发货）
                    self.TagUserItem(playerId,order["order_id"])
            else:
                print ("查询订单失败")
        compCreateHttp.QueryLobbyUserItem(cb, uid)

    #标记已发货
    def TagUserItem(self,playerId,orderId):
        compCreateHttp = factory.CreateHttp(self.levelId)
        uid = compCreateHttp.GetPlayerUid(playerId)
        def cb(data):
            if data:
                print("标记已发货成功")
            else:
                print ("标记已发货失败")
        def getter():
            return [
                {
                    "key": "orders",
                    "value": orderId
                }
            ]
        compCreateHttp.LobbySetStorageAndUserItem(cb, uid, orderId, getter)

    #实现指令: 免费宝箱
    def buyFreeChest(self,playerId):
        print("有玩家实现了指令: 免费宝箱")
        compCreateItem = factory.CreateItem(playerId)
        itemDict = {'itemName': 'tpkth:commonChestCall','count': 1,}
        compCreateItem.SpawnItemToPlayerInv(itemDict, playerId)

    #实现指令: 购买-宝箱魔盒（小）
    def buySmallChest(self,playerId):
        print("有玩家实现了指令: 宝箱魔盒小")
        compCreateItem = factory.CreateItem(playerId)
        itemDict = {'itemName': 'tpkth:coalChestCall','count': 4,}
        compCreateItem.SpawnItemToPlayerInv(itemDict, playerId)

    #实现指令: 购买-宝箱魔盒（大）
    def buyBigChest(self,playerId):
        print("有玩家实现了指令: 宝箱魔盒大")
        compCreateItem = factory.CreateItem(playerId)
        itemDict = {'itemName': 'tpkth:healthChestCall','count': 2,}
        compCreateItem.SpawnItemToPlayerInv(itemDict, playerId)
        itemDict = {'itemName': 'tpkth:oceanChestCall','count': 2,}
        compCreateItem.SpawnItemToPlayerInv(itemDict, playerId)
        itemDict = {'itemName': 'tpkth:goldenChestCall','count': 2,}
        compCreateItem.SpawnItemToPlayerInv(itemDict, playerId)

    #实现指令: 魔杖礼盒
    def buyStaffChest(self,playerId):
        print("有玩家实现了指令: 魔杖礼盒")
        compCreateItem = factory.CreateItem(playerId)
        itemDict = {'itemName': 'tpkth:enderStaff','count': 1,}
        compCreateItem.SpawnItemToPlayerInv(itemDict, playerId)
        itemDict = {'itemName': 'tpkth:mushroomStaff','count': 1,}
        compCreateItem.SpawnItemToPlayerInv(itemDict, playerId)
        itemDict = {'itemName': 'tpkth:leafStaff','count': 1,}
        compCreateItem.SpawnItemToPlayerInv(itemDict, playerId)

    #实现指令: 普通钻头
    def buyCommonBit(self,playerId):
        print("有玩家实现了指令: 普通钻头")
        compCreateItem = factory.CreateItem(playerId)
        itemDict = {'itemName': 'tpkth:commonBit','count': 1,}
        compCreateItem.SpawnItemToPlayerInv(itemDict, playerId)

    #实现指令: 合金钻头
    def buyAlloyBit(self,playerId):
        print("有玩家实现了指令: 合金钻头")
        compCreateItem = factory.CreateItem(playerId)
        itemDict = {'itemName': 'tpkth:AlloyBit','count': 1,}
        compCreateItem.SpawnItemToPlayerInv(itemDict, playerId)

    #实现指令: 双倍分数仪
    def buyScoreMachine(self,playerId):
        print("有玩家实现了指令: 双倍分数仪")
        #存储进云数据
        self.StorageUserItem(playerId,"scoreMachine")
        #加入双倍分数列表
        self.playerDoubleScoreList.append(playerId)

    #实现指令: 财富之钟
    def buyWealthBell(self,playerId):
        print("有玩家实现了指令: 财富之钟")
        #存储进云数据
        self.StorageUserItem(playerId,"bell")
        #加入双倍分数列表
        self.playerWealthBellList.append(playerId)

    #宝箱刷新计时器
    def Countdown(self):
        #如果倒计时大于0则减数，否则触发刷新事件
        if self.roomCountdown > 0:
            self.roomCountdown = self.roomCountdown - 1
        else:
            self.ActionRefreshChest()
            self.roomCountdown = 45.0

    #清除宝箱
    def ClearChest(self):
        #获取所有实体
        entityDicts = serverApi.GetEngineActor()
        #检测所有宝箱是否有"random"标签，有则清除
        for entityId in entityDicts:
            compCreateTag = factory.CreateTag(entityId)
            result = compCreateTag.EntityHasTag("random")
            if result == True:
                self.DestroyEntity(entityId)

    #清除冗余
    def ClearRubbish(self):
        #清除宝箱指定位置的方块
        self.compCreateCommand.SetCommand("/fill 7 1 7 11 3 11 air 0")
        self.compCreateCommand.SetCommand("/fill -8 1 -8 -12 3 -12 air 0")
        #清除随机方块位置的掉落物
        self.compCreateCommand.SetCommand("/kill @e[x=-10,y=1,z=9,r=5,type=item]")
        #清除出生点方块
        self.compCreateCommand.SetCommand("/fill 1 1 1 -1 3 -1 air 0")

    #刷新宝箱
    def ActionRefreshChest(self):
        #清除之前的宝箱和冗余
        self.ClearChest()
        self.ClearRubbish()
        #随机抽取新方块
        block = self.RandomBlock()
        #填充方块
        self.compCreateCommand.SetCommand("/fill -8 1 7 -12 4 11 " + block)
        #随机抽取新宝箱
        randomEntityId1, randomEntityName1 = self.RandomChest()
        randomEntityId2, randomEntityName2 = self.RandomChest()
        #设置宝箱名字
        entityId1 = self.CreateEngineEntityByTypeStr(randomEntityId1, self.aPos, (0, 0), 0)
        entityId2 = self.CreateEngineEntityByTypeStr(randomEntityId2,  self.bPos, (0, 0), 0)
        #给新宝箱贴标签
        compCreateTag = factory.CreateTag(entityId1)
        compCreateTag.AddEntityTag("random")
        compCreateTag = factory.CreateTag(entityId2)
        compCreateTag.AddEntityTag("random")
        #设置宝箱名字
        compCreateName = factory.CreateName(entityId1)
        compCreateName.SetName(randomEntityName1)
        compCreateName = factory.CreateName(entityId2)
        compCreateName.SetName(randomEntityName2)

    #实现宝箱权重（越往后的被抽取到的概率越低）
    def Weighted_choice(self,choices, weights):
        total_weight = sum(weights)
        threshold = random.uniform(0, total_weight)
        cumulative_weight = 0
        for choice, weight in zip(choices, weights):
            cumulative_weight += weight
            if cumulative_weight >= threshold:
                return choice

    #随机抽取新方块
    def RandomBlock(self):
        block = random.choice(self.randomBlockList)
        return block

    #随机抽取新宝箱
    def RandomChest(self):
        keys = list(self.chestNameDict.keys())
        weights = range(len(keys), 0, -1)
        randomKey = self.Weighted_choice(keys, weights)
        randomValue = self.chestNameDict[randomKey]
        return randomKey,randomValue
    
    #从云获取最高的三条数据（每次获取并自动通知客户端）
    def GetTop(self):
        print("GetTop...")
        compCreateHttp = factory.CreateHttp(self.levelId)

        def cb(data):
            print("gettopdata::")
            print(data)
            if data:
                newData = data["entity"]["data"]
                print(newData)
                #通知all客户端UI更新排行榜
                #替换当前排行榜数据
                print("self.playerList:")
                print(self.playerList)
                self.topDict = newData
                print ("get top ok")
            else:
                print ("get top failed")
        # 获取money从大到小排序第1到第3的数据
        # 这个函数就算是本地也有回调数据，只不过是None（也可能是没有配置排序key的原因）
        compCreateHttp.LobbyGetStorageBySort(cb, "new_score", False, 0, 5)

        #本地数据模拟
        if self.DEBUG:
            data = {'message': 'GetTop', 'code': 0, 'details': '', 'entity': {'data': [{'version': 1, 'uid': '123', 'nickname': "fx", 'value': 666},{'version': 1, 'uid': '456', 'nickname': "hbbb", 'value': 555},{'version': 1, 'uid': '456', 'nickname': "duke", 'value': 444},{'version': 1, 'uid': '456', 'nickname': "lightAndDark", 'value': 333},{'version': 1, 'uid': '788', 'nickname': "ghost", 'value': 222}]}}
            cb(data)

    #从云获取玩家分数
    def GetPlayerScore(self,playerId):
        print("checking")
        compCreateHttp = factory.CreateHttp(self.levelId)
        uid = compCreateHttp.GetPlayerUid(playerId)

        def cb(data):
            if data:
                print(data)
                # 更新本地数据
                newData = { i["key"]: i["value"] for i in data["entity"]["data"] }
                self.playerScoreDict[playerId] = newData["new_score"]
                print("get score succeeded from cloud")
            else:
                print("get score failed from cloud")
        keys = ["new_score"]
        compCreateHttp.LobbyGetStorage(cb, uid, keys)

        #本地数据模拟
        if self.DEBUG:
            data = {'message': 'GetPlayerScore', 'code': 0, 'details': '', 'entity': {'data': [{'version': 2, 'key': 'new_score', 'value': 100}]}}
            cb(data)

    #获取用户钻头并添加进背包且标记
    def GetStorageBit(self,playerId,bitName):
        print("GetStorageBit...")
        compCreateHttp = factory.CreateHttp(self.levelId)
        uid = compCreateHttp.GetPlayerUid(playerId)
        #定义空数组准备收集记录
        newDataVal = []
        def cb(data):
            print(data)
            if data:
                newData = { i["key"]: i["value"] for i in data["entity"]["data"] }
                if newData != None and newData[bitName] != None:
                    newDataVal = json.loads(newData[bitName])
                    #如果已在本图发放过直接不发
                    print("newDataVal?478")
                    print(newDataVal)
                    if newDataVal["levelId"] == self.levelId and newDataVal["tag"] == True:
                        return
                    elif (newDataVal["levelId"] == self.levelId and newDataVal["tag"] != True) or (not any(item["levelId"] == self.levelId for item in newDataVal)):
                        #发放并自动标记
                        compCreateItem = factory.CreateItem(playerId)
                        itemDict = {'itemName': 'tpkth:' + bitName,'count': 1}
                        compCreateItem.SpawnItemToPlayerInv(itemDict, playerId)
                        print(bitName + ": delivered and succeeded")
                    print("GetStorageBit succeeded")
            else:
                print("GetStorageBit failed")

        def getter():
            getterVal =   {
                        "levelId": self.levelId,
                        "tag": True
                    }
            #增加记录并塞回去返回
            newDataVal.append(getterVal)
            valJSON = json.dumps(getterVal)
            return [
                {
                    "key": bitName,
                    "value": valJSON
                }
            ]
        compCreateHttp.LobbySetStorageAndUserItem(cb, uid, None, getter)

        #本地数据模拟
        if self.DEBUG:
            mockData = [
                {
                    "levelId": self.levelId,
                    "tag": True
                },
                {
                    "levelId": "123",
                    "tag": True
                },
                {
                    "levelId": "456",
                    "tag": True
                },
            ]
            mockJSON = json.dumps(mockData)
            data = {'message': 'GetStorageBit', 'code': 0, 'details': '', 'entity': {'data': [{'version': 2, 'key': bitName, 'value': mockJSON}]}}
            cb(data)

    #获取用户财富之钟并添加进列表
    def GetStorageBell(self,playerId):
        print("GetStorageBell...")
        compCreateHttp = factory.CreateHttp(self.levelId)
        uid = compCreateHttp.GetPlayerUid(playerId)
        def cb(data):
            print(data)
            if data:
                newData = { i["key"]: i["value"] for i in data["entity"]["data"] }
                if newData == None:
                    print("get bell failed because the data's no relative data about bell")
                    return
                if newData != None and newData["bell"] != None and newData["bell"] == True:
                    self.playerWealthBellList.append(playerId)
                    print("get bell succeeded")
            else:
                print("get bell failed")
        keys = ["bell"]
        compCreateHttp.LobbyGetStorage(cb, uid, keys)

        #本地数据模拟
        if self.DEBUG:
            data = {'message': 'GetStorageBell', 'code': 0, 'details': '', 'entity': {'data': [{'version': 2, 'key': 'bell', 'value': True}]}}
            cb(data)

    #获取用户分数仪并添加进列表
    def GetStorageScoreMachine(self,playerId):
        print("GetStorageScoreMachine...")
        compCreateHttp = factory.CreateHttp(self.levelId)
        uid = compCreateHttp.GetPlayerUid(playerId)

        def cb(data):
            print(data)
            if data:
                newData = { i["key"]: i["value"] for i in data["entity"]["data"] }
                print("newdata??")
                print(newData)
                if newData["scoreMachine"] != None and newData["scoreMachine"] == True:
                    self.playerDoubleScoreList.append(playerId)
                    print("get scoreMachine succeeded")
            else:
                print("get data failed")
        keys = ["scoreMachine"]
        compCreateHttp.LobbyGetStorage(cb, uid, keys)

        #本地数据模拟
        if self.DEBUG:
            data = {'message': 'GetStorageScoreMachine', 'code': 0, 'details': '', 'entity': {'data': [{'version': 2, 'key': 'scoreMachine', 'value': True}]}}
            cb(data)

    #存储用户云增益(key: itemName; vlaue: True/False)
    def StorageUserItem(self,playerId,itemName):
        print("StorageUserItem...")
        #创建链接
        compCreateHttp = factory.CreateHttp(self.levelId)
        #获取玩家uid
        uid = compCreateHttp.GetPlayerUid(playerId)
        def callback(data):
            if data:
                #更新本地数据
                newData = { i["key"]: i["value"] for i in data["entity"]["data"] }
                self.playerDoubleScoreList.append(newData[itemName])
                print("save cloud buff succeeded")
            else:
                print("set data failed")
        def getter():
            return [
                {
                    "key": itemName,
                    "value": True
                }
            ]
        compCreateHttp.LobbySetStorageAndUserItem(callback, uid, None, getter)

    #上传玩家云分数
    def UpLoadPlayerScore(self,playerId):
        print("UpLoadPlayerScore...")
        #创建链接
        compCreateHttp = factory.CreateHttp(self.levelId)
        uid = compCreateHttp.GetPlayerUid(playerId)

        def callback(data):
            if data:
                print("update player score succeeded")
            else:
                print("update player score failed")
        def getter():
            #如果 < 0 的话不支持上传
            if self.playerScoreDict[playerId] < 0:
                return
            else:
                return [
                    {
                        "key": "new_score",
                        "value": self.playerScoreDict[playerId]
                    }
                ]
        compCreateHttp.LobbySetStorageAndUserItem(callback, uid, None, getter)

    def NotifyClientForUpdateUICycle(self):
        for playerId in self.playerScoreDict:
            #改变名字分数
            compCreateName = factory.CreateName(playerId)
            compCreateName.SetPlayerPrefixAndSuffixName("",serverApi.GenerateColor('RED')," - 分数: " + str(self.playerScoreDict[playerId]),serverApi.GenerateColor('GRAY'))
            #通知客户端展示新进度条
            self.NotifyToMultiClients(self.playerList,"ProgressBarChangeEvent", self.roomCountdown)
            #通知客户端UI更新分数值
            self.NotifyToClient(playerId,"ScoreChangeEvent", self.playerScoreDict[playerId])
            #更新玩家攻击力（传分数自动换算攻击力）
            if self.playerScoreDict[playerId] != -1:
                self.playerAttackDict[playerId] = self.playerScoreDict[playerId] / 15
            if playerId in self.playerAttackDict:
                #通知客户端UI更新伤害值
                self.NotifyToClient(playerId,"AttackChangeEvent", self.playerAttackDict[playerId])
            if playerId in self.playerDoubleScoreList:
                #通知客户端UI更新图标
                self.NotifyToClient(playerId,"VisibleDoubleScoreEvent", True)
            #通知客户端UI更新排行榜
            self.NotifyToMultiClients(self.playerList,"TopEvent", self.topDict)

    #玩家点击方块时
    def OnServerBlockUseEvent(self,args):
        #方块过滤列表（如果不在此过滤表内的方块则直接return）
        if args["blockName"] not in self.blockFilterList:
            return
        playerId = args["playerId"]
        #判断是否为财富之钟的玩家
        if playerId in self.playerWealthBellList and args["blockName"] == "minecraft:bell":
            compCreatePos = factory.CreatePos(playerId)
            playerIdPos = compCreatePos.GetFootPos()

            playerIdPosX = round(floor((playerIdPos[0])),0)
            playerIdPosY = round(floor((playerIdPos[1])),0)
            playerIdPosZ = round(floor((playerIdPos[2])),0)

            newPlayerPos = (playerIdPosX,playerIdPosY,playerIdPosZ)

            compCreateBlockInfo = factory.CreateBlockInfo(self.levelId)
            blockDict = compCreateBlockInfo.GetBlockNew(newPlayerPos, args["dimensionId"])
            itemDict = {
                'itemName': blockDict['name'],
                'count': 1,
                'auxValue': blockDict['aux'],
            }

            compCreatePlayer = factory.CreatePlayer(playerId)
            isSneaking = compCreatePlayer.isSneaking()

            if isSneaking == True:
                itemDict['count'] = 5
                compCreateCommand = factory.CreateCommand(self.levelId)
                compCreateCommand.SetCommand("/playsound note.chime @s",playerId)
                compCreateCommand.SetCommand("/playsound note.chime @s 0",playerId)
                compCreateCommand.SetCommand("/playsound note.chime @s 1",playerId)
                compCreateCommand.SetCommand("/playsound note.chime @s 2",playerId)
                compCreateCommand.SetCommand("/playsound note.chime @s 3",playerId)

            self.CreateEngineItemEntity(itemDict, args["dimensionId"], (args["x"],args["y"],args["z"]))

        compCreateItem = factory.CreateItem(playerId)
        itemDict = compCreateItem.GetPlayerItem(serverApi.GetMinecraftEnum().ItemPosType.CARRIED)
        #判断是否为碳转换器
        if itemDict != None and itemDict["newItemName"] != None and args["blockName"] == "tpkth:coalchangeblock":
            #判断是否脚下为碳转换器
            compCreatePos = factory.CreatePos(playerId)
            playerIdPos = compCreatePos.GetFootPos()
            playerIdPosX = round(floor((playerIdPos[0])),0)
            playerIdPosY = round(floor((playerIdPos[1])),0)
            playerIdPosZ = round(floor((playerIdPos[2])),0)
            newPlayerPos = (playerIdPosX,playerIdPosY,playerIdPosZ)
            compCreateBlockInfo = factory.CreateBlockInfo(self.levelId)
            blockDict = compCreateBlockInfo.GetBlockNew(newPlayerPos, args["dimensionId"])
            if blockDict["name"] != "tpkth:coalchangeblock":
                return
            else:
                #减少手上物品的数量
                if itemDict["count"] > 0:
                    itemDict["count"] = itemDict["count"] - 1
                    compCreateItem.SpawnItemToPlayerCarried(itemDict, playerId)

                #发放
                itemDict = {
                    'itemName': 'minecraft:coal',
                    'count': 1,
                }
                compCreateItem.SpawnItemToPlayerInv(itemDict, playerId)

                #随机bgm
                number = random.choice([1,2,3])
                if number == 1:
                    self.compCreateCommand.SetCommand("/playsound note.bass @s",playerId)
                elif number == 2:
                    self.compCreateCommand.SetCommand("/playsound note.snare @s",playerId)
                elif number == 3:
                    self.compCreateCommand.SetCommand("/playsound note.harp @s",playerId)
                return

        #判断是否为特定武器并执行操作
        isAppointWeapon = False
        #末影人之杖（只有末地石方块有效）
        if itemDict != None and itemDict["newItemName"] == "tpkth:enderstaff" and args["blockName"] == "minecraft:end_stone":
            #获取当前世界的维度
            compCreateDimension = factory.CreateDimension(playerId)
            dimension = compCreateDimension.GetEntityDimensionId()
            #生成末影人
            self.CreateEngineEntityByTypeStr('minecraft:enderman', (args["x"], args["y"]+1, args["z"]), (0, 0), dimension)
            isAppointWeapon = True
        #生命树之杖（只有草地方块有效）
        elif itemDict != None and itemDict["newItemName"] == "tpkth:leafstaff" and args["blockName"] == "minecraft:grass":
            #生成随机树苗
            state = random.choice([0,1,2,3,4,5,6])
            self.compCreateCommand.SetCommand("/setblock {0} {1} {2} sapling {3}".format(args["x"], args["y"]+1, args["z"], state),args["playerId"])
            isAppointWeapon = True
        #蘑菇牛之杖（只有草地方块有效）
        elif itemDict != None and itemDict["newItemName"] == "tpkth:mushroomstaff" and args["blockName"] == "minecraft:grass":
            #获取当前世界的维度
            compCreateDimension = factory.CreateDimension(playerId)
            dimension = compCreateDimension.GetEntityDimensionId()
            #生成蘑菇牛
            self.CreateEngineEntityByTypeStr('minecraft:mooshroom', (args["x"], args["y"]+1, args["z"]), (0, 0), dimension)
            isAppointWeapon = True

        #如果是特定武器就减少耐久
        if isAppointWeapon: 
            if itemDict["durability"] > 1:
                #减少玩家主手武器耐久
                itemDict["durability"] = itemDict["durability"] - 1
                compCreateItem.SpawnItemToPlayerCarried(itemDict, playerId)
            else:
                itemDict = {
                    'itemName': 'minecraft:air',
                }
                compCreateItem.SpawnItemToPlayerCarried(itemDict, playerId)

    #玩家攻击实体时
    def OnPlayerAttackEntityEvent(self,args):
        #获取玩家id
        playerId = args["playerId"]
        #获取受击者id
        victimId = args["victimId"]

        #检查是否为特定武器
        compCreateItem = factory.CreateItem(playerId)
        itemDict = compCreateItem.GetPlayerItem(serverApi.GetMinecraftEnum().ItemPosType.CARRIED)

        #烈焰剑
        if itemDict != None and itemDict["newItemName"] == "tpkth:firesword":
            #点燃实体
            compCreateAttr = factory.CreateAttr(victimId)
            compCreateAttr.SetEntityOnFire(2, 2)

        #发光鱿鱼剑
        elif itemDict != None and itemDict["newItemName"] == "tpkth:lightsquidsword":
            #给自己增加5秒夜视
            compCreateEffect = factory.CreateEffect(playerId)
            compCreateEffect.AddEffectToEntity("night_vision", 5, 0, False)

        #毒刃
        elif itemDict != None and itemDict["newItemName"] == "tpkth:poisonsword":
            #给对手挂上毒
            compCreateEffect = factory.CreateEffect(victimId)
            compCreateEffect.AddEffectToEntity("poison", 2, 5, False)

        #彩虹激光刃
        elif itemDict != None and itemDict["newItemName"] == "tpkth:rainbowrasersword":
            #加速时间流逝
            self.compCreateCommand.SetCommand("/time add 50",playerId)

        #获取类系
        compCreateAttr = factory.CreateAttr(victimId)
        familyList = compCreateAttr.GetTypeFamily()
        #如果为npc则通知客户端触发相应声音
        if "npc" in familyList:
            #播放音效
            self.compCreateCommand.SetCommand("/playsound random.anvil_land @p ~~~ 1 3",playerId)

    #实体被玩家杀死事件
    def OnMobDieEvent(self,args):
        entityId = args["id"]
        playerId = args["attacker"]
        #获取实体名字
        compCreateEngineType = factory.CreateEngineType(entityId)
        entityName = compCreateEngineType.GetEngineTypeStr()
        #如果死的不是宝箱就return
        if entityName not in self.chestNameDict:
            return
        #在宝箱分数表获取分数值
        score = self.chestScoreDict[entityName]
        #检查玩家是否在双倍分数表内
        if playerId in self.playerDoubleScoreList:
            #是的话双倍分数
            score = int(score) * 2
        #更新玩家当前分数
        self.playerScoreDict[playerId] = self.playerScoreDict[playerId] + int(score)

    #实体受伤前事件
    def OnActuallyHurtServerEvent(self,args):
        #校验是否为玩家
        playerId = args["srcId"]
        compCreateEngineType = factory.CreateEngineType(playerId)
        entityType = compCreateEngineType.GetEngineType()
        EntityTypeEnum = serverApi.GetMinecraftEnum().EntityType
        damage = args["damage"]
        if entityType & entityType == EntityTypeEnum.Player:
            #是的话修改伤害值
            args["damage"] = damage + self.playerAttackDict[playerId]
    
    #当玩家已经破坏了方块
    def OnDestroyBlockEvent(self,args):
        playerId = args["playerId"]
        #检查是否为钻头
        compCreateItem = factory.CreateItem(playerId)
        itemDict = compCreateItem.GetPlayerItem(serverApi.GetMinecraftEnum().ItemPosType.CARRIED)
        #普通钻头
        if itemDict != None and itemDict["newItemName"] == "tpkth:commonbit" and args["dimensionId"] == 0:
            #判断是否在随机方块挖掘范围内
            if args["x"] in (-8,-9,-10,-11,-12) and args["y"] in (1,2,3,4) and args["z"] in (7,8,9,10,11):
                #10%几率一键挖掘刷新区的所有方块
                number = random.choice([1,2,3,4,5,6,7,8,9,10])
                if number == 1:
                    self.compCreateCommand.SetCommand("/fill -8 1 7 -12 4 11 air 0 destroy")
        #合金钻头
        elif itemDict != None and itemDict["newItemName"] == "tpkth:alloybit" and args["dimensionId"] == 0:
            #判断是否在随机方块挖掘范围内
            if args["x"] in (-8,-9,-10,-11,-12) and args["y"] in (1,2,3,4) and args["z"] in (7,8,9,10,11):
                #一键挖掘刷新区的所有方块
                self.compCreateCommand.SetCommand("/fill -8 1 7 -12 4 11 air 0 destroy")