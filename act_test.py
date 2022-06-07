# 従属グラフに対して各アクションを適用するテスト

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

# ------------------------------------------------------------------
# -----                       main処理                         -----
# ------------------------------------------------------------------
if __name__ == "__main__":

    args = parser.parse_args()

    #ルールリストを形成
    rule_list = BS.create_rulelist(args.rules)
    packet_list = BS.create_packetlist(args.packets,rule_list)

    rule_list.compute_weight(packet_list)


    # グラフ構築のテスト

    graph = DependencyGraphModel(rule_list)

    while len(graph.removed_nodelist) < len(list(graph.graph.nodes)):


        chosen_algorithm = input("使用アルゴリズム(SGMの\"s\"または日景の\"h\"):")
        if chosen_algorithm == "s":
            graph.single__sub_graph_mergine()
        elif chosen_algorithm == "h":
            graph.single__hikage_method()

        print("SGMの整列済みリスト：",end="")
        print(graph.sgms_reordered_nodelist)
        print("Hikageの整列済みリスト：",end="")
        print(graph.hikages_reordered_nodelist)


    final_nodelist = graph.complete()
    #print(final_nodelist)
