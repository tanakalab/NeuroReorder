# 基盤のデータ構造を初期化するメソッドとクラスをまとめている

# ------------------------------------------------------------------
# -----                          引数                          -----
# ------------------------------------------------------------------
from base_structure.rulemodel import *
from enum import Enum, auto

# ------------------------------------------------------------------
# -----           実装している手法を表現する列挙型              -----
# ------------------------------------------------------------------
class Implemented_Action(Enum):
    SGM = 0
    HikageMethod = 1
    #SimpleChoosing = 2

    def __len__(self):
        return len([*cls.__members__.values()])


# ------------------------------------------------------------------
# -----            追加オプションを表現する列挙型               -----
# ------------------------------------------------------------------
class Reward_Formula(Enum):
    filter = auto()
    init_weight = auto()





class BS:
    #=========================================
    # ファイル名からルールリストの構造を構築する
    #=========================================
    @staticmethod
    def create_rulelist(rulelist_filename):
        ret_rulelist = RuleList()

        with open(rulelist_filename,mode="r") as rulelist_file:
            while rulelist_file:
                rule = rulelist_file.readline().split()
                if not rule:
                    break
                ret_rulelist.append(Rule(rule[0],rule[1]))
        return ret_rulelist

    #===========================================
    # ファイル名からパケットリストの構造を構築する
    #===========================================
    @staticmethod
    def create_packetlist(packetlist_filename,rule_list):
        packet_list = []

        if packetlist_filename != None:
            with open(packetlist_filename,mode="r") as packetlist_file:
                while packetlist_file:
                    packet = "".join(packetlist_file.readline().split())
                    if not packet:
                        break
                    packet_list.append(packet)
        # 指定されていなければパケット集合を構成
        else:
            # ビット列が長すぎると生成が大変なため一定値で仕切る
            assert len(rule_list[0].bit_string) <= 10 , "パケット集合計算が困難な為停止します."
            assert rule_list != None , "ルールリストが入力されていません."

            max_num = 2**len(rule_list[0].bit_string)
            specifier = "0"+str(len(rule_list[0].bit_string))+"b"
            for i in range(max_num):
                packet_list.append(format(i,specifier))
        return packet_list

    #===========================================
    #      ファイル名から行動リストを構築する
    #===========================================
    @staticmethod
    def create_actionlist(actionlist_filename):
        action_list = []
        with open(actionlist_filename,mode="r") as actionlist_file:
            while actionlist_file:
                action = actionlist_file.readline().split()
                if not action:
                    break
                action_list.append((action[0],[int(x) for x in action[1:]]))


        return action_list
