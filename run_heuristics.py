# 各発見的解法単体で並べ替えする関数(excelに実験結果を入れる用)

# ------------------------------------------------------------------
# -----                      ライブラリ定義                     -----
# ------------------------------------------------------------------
# 基本ライブラリ
import math
import argparse
import random
import os
# グラフライブラリとプロットライブラリ
import networkx as nx
import matplotlib.pyplot as plt

# 実験結果書き込み用excelライブラリ
import openpyxl

# 自前環境
from base_structure.rulemodel import *
from base_structure.base_structure import *
from base_structure.DependencyGraphModel import *
from envs.rulemodel_env import rulemodel_env
# ------------------------------------------------------------------


# ------------------------------------------------------------------
# -----                          引数                          -----
# ------------------------------------------------------------------
parser = argparse.ArgumentParser()

parser.add_argument(
    "rules",
    type=str,
    help="読み込むルールファイルのパス. ClassBenchルール変換プログラムの6番を使用し,assign_evaluation_to_rulelist.pyで評価型を付与すること.")
parser.add_argument(
    "--packets",
    type=str,
    default=None,
    help="読み込むパケットファイルのパス.ClassBenchルール変換プログラムの6番を使用すること.無指定の場合は一様分布(全ての場合のパケット1つずつ).")
parser.add_argument(
    "heuristics",
    type=str,
    help="選択する発見的解法.\"SGM\"または\"Hikage\"と入力.")
parser.add_argument(
    "--experiment_title",
    type=str,
    default=None,
    help="実験名.Excelに結果を書き込む場合は指定.")
parser.add_argument(
    "--sample_number",
    type=int,
    default=None,
    help="サンプル番号.Excelに結果を書き込む場合は指定.")


# ------------------------------------------------------------------

# ------------------------------------------------------------------
# -----                       main処理                         -----
# ------------------------------------------------------------------
if __name__ == "__main__":

    args = parser.parse_args()
    # ルールリストを形成
    rule_list = BS.create_rulelist(args.rules)
    # パケットリストを形成
    packet_list = BS.create_packetlist(args.packets,rule_list)

    rule_list.compute_weight(packet_list)
    
    graph = DependencyGraphModel(rule_list)



    action_group = []
    # 発見的解法を実行
    while len(graph.removed_nodelist) < len(list(graph.graph.nodes)):
        if args.heuristics == "SGM":
            chosed_nodes = graph.single__sub_graph_mergine()
            action_group.append(("SGM",[chosed_nodes]))
        elif args.heuristics == "Hikage":
            chosed_nodes = graph.single__hikage_method()
            action_group.append(("Hikage",chosed_nodes))
        else:
            AssertionError("発見的解法指定エラー")




    # 並べ替え後ルールリスト
    reordered_rulelist = graph.complete()
    # 遅延を導出
    reordered_latency = reordered_rulelist.filter(packet_list)[0]
    # experiment_titleまたはsample_numberどちらかが指定されていない場合は書き込まない



    if args.experiment_title == None:
        print("遅延："+str(reordered_latency))
        exit()

    if args.heuristics in ["SGM","Hikage"]:
        with open("Dump/"+args.experiment_title+"/" + args.heuristics + "sACTIONLIST","w",encoding="utf-8",newline="\n") as write_file:
            for action in action_group:
                write_file.write(str(action[0]) + "\t" + " ".join(map(str,action[1])) + "\n")


    if args.sample_number == None:
        print("遅延："+str(reordered_latency))
        exit()



    # 対応するセルに書き込み
    position = chr(ord('C')+getattr(Implemented_Action,args.heuristics).value) + str(1+args.sample_number)
    if not ExcelController.is_value_in_excelfile(args.experiment_title,position):
        ExcelController.write_result_to_excel(args.experiment_title,position,reordered_latency)
        print("EXCELに"+args.heuristics+"サンプル"+str(args.sample_number)+"の結果値を書き込みました.")
    
    # 元遅延の値が空なら遅延を計算して書き込む
    position = 'A' + str(1+args.sample_number)
    if not ExcelController.is_value_in_excelfile(args.experiment_title,position):
       ExcelController.write_result_to_excel(args.experiment_title,position,rule_list.filter(packet_list)[0])
       print("EXCELにサンプル"+str(args.sample_number)+"の遅延初期値を書き込みました.")
