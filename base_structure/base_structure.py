# 基盤のデータ構造を初期化するメソッドとクラスをまとめている

# ------------------------------------------------------------------
# -----                          引数                          -----
# ------------------------------------------------------------------
from base_structure.rulemodel import *
from enum import Enum, auto
import os
import openpyxl

# ------------------------------------------------------------------
# -----           実装している手法を表現する列挙型              -----
# ------------------------------------------------------------------
class Implemented_Action(Enum):
    SGM = 0
    Hikage = 1
    SimpleWeightChoose = 2
    RSGM = 3
    #AuxiliaryHikage = 3

    def __len__(self):
        return len([*cls.__members__.values()])


# ------------------------------------------------------------------
# -----            追加オプションを表現する列挙型               -----
# ------------------------------------------------------------------
class Reward_Formula(Enum):
    filter = auto()
    init_weight = auto()

# ------------------------------------------------------------------
# -----            Excelファイルへの入出力を管理               -----
# ------------------------------------------------------------------
class ExcelController:
    
    filepath1 = 'Dump/'
    filepath2 = '/latency_summary.xlsx'
    
    @staticmethod
    def init_excel():
        wb = openpyxl.Workbook()
        sheet = wb.worksheets[0]

        # 初期遅延と機械学習は固定
        sheet['A1'] = "Initial"
        sheet['B1'] = "NeuroReorder"
        # その他 発見的解法
        for i in range(len(Implemented_Action)):
            sheet[chr(ord('C') + i) + '1'] = Implemented_Action._member_names_[i]
        return wb

    @staticmethod
    def load_wb(experiment_title):
            if os.path.exists(ExcelController.filepath1+experiment_title+ExcelController.filepath2):
                return openpyxl.load_workbook(ExcelController.filepath1+experiment_title+ExcelController.filepath2)
            else:
                return ExcelController.init_excel()



    @staticmethod
    def write_result_to_excel(experiment_title,position,value):    
        # ファイルロード(ない場合は初期化)
        wb = ExcelController.load_wb(experiment_title)

        # 対応するセルに書き込み
        sheet = wb.worksheets[0]
        sheet[position] = value

        # セーブ・クローズ
        wb.save(ExcelController.filepath1+experiment_title+ExcelController.filepath2)
        wb.close()

    @staticmethod 
    def is_value_in_excelfile(experiment_title,position):
        wb = ExcelController.load_wb(experiment_title)
        sheet = wb.worksheets[0]

        return sheet[position].value is not None











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
