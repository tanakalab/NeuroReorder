# 2つのルールを入力してパケット分類テストを行う

# ------------------------------------------------------------------
# -----                      ライブラリ定義                     -----
# ------------------------------------------------------------------
import math
import argparse
import random
# グラフ関連
import networkx as nx
import matplotlib.pyplot as plt
# 自前環境
from base_structure.rulemodel import *
from base_structure.base_structure import *
from base_structure.DependencyGraphModel import *
from envs.rulemodel_env import rulemodel_env


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
    "--comparing_rules",
    type=str,
    help="比較対象となる読み込むルールファイルのパス. ClassBenchルール変換プログラムの6番を使用し,assign_evaluation_to_rulelist.pyで評価型を付与すること.")

# ------------------------------------------------------------------
# -----                       main処理                         -----
# ------------------------------------------------------------------
if __name__ == "__main__":

    args = parser.parse_args()

    #ルールリストを形成
    rule_list1 = BS.create_rulelist(args.rules)
    rule_list2 = None
    packet_list = BS.create_packetlist(args.packets,rule_list1)

    #フィルタリング
    res1 = None
    res2 = None

    print("Start packet filtering.")
    res1 = rule_list1.filter(packet_list,True)
    print("遅延合計値 = [%d]\n\nAll Packet is successfully filtered." % res1[0])
    if args.comparing_rules != None:
        rule_list2 = BS.create_rulelist(args.comparing_rules)
        print("Start packet filtering.")
        res2 = rule_list2.filter(packet_list,True)
        print("遅延合計値 = [%d]\n\nAll Packet is successfully filtered." % res2[0])
    else:
        exit()


    for i in range(len(res1[1])):
        if res1[1][i] != res2[1][i]:
            print("ポリシ違反があります.")
            exit()
    print("ポリシは正常です")
