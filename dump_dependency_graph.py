# 従属グラフを図にして出力する

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
    help="読み込むパケットファイルのパス. ")

parser.add_argument(
    "--figsize",
    type=int,
    default=100,
    help="")
parser.add_argument(
    "--dump_type",
    type=str,
    default="normal",
    help="normal -> 通常の出力．caption -> ゼミ資料などで小規模ルールの従属グラフを載せたい場合に向けた設定で出力")

# ------------------------------------------------------------------
# -----                       main処理                         -----
# ------------------------------------------------------------------
if __name__ == "__main__":

    args = parser.parse_args()

    #ルールリストを形成
    rule_list = BS.create_rulelist(args.rules)
    packet_list = BS.create_packetlist(args.packets,rule_list)

    graph = DependencyGraphModel(rule_list,packet_list)

    plt.figure(figsize=(args.figsize,args.figsize))

    graph.plot_graph(file_name="Dump/" + args.rules.split('/')[-1],dump_type=args.dump_type)
