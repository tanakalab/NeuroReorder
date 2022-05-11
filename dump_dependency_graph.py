
import math
import argparse
import datetime
import time

import random

import networkx as nx
import matplotlib.pyplot as plt


#自前環境
from rulemodel import *
from DependencyGraphModel import *

parser = argparse.ArgumentParser()

parser.add_argument(
    "rules",
    type=str,
    help="読み込むルールファイルのパス. ClassBenchルール変換プログラムの6番を使用し,assign_evaluation_to_rulelist.pyで評価型を付与すること.")

parser.add_argument(
    "--figsize",
    type=int,
    default=100,
    help="")

#normal
#only_edge
parser.add_argument(
    "--mode",
    type=str,
    default="normal",
    help="")


if __name__ == "__main__":

    args = parser.parse_args()

    #ルールリストを形成
    rule_list = RuleList()

    with open(args.rules,mode="r") as rulelist_file:
        while rulelist_file:
            rule = rulelist_file.readline().split()
            #print(rule)
            if not rule:
                break
            rule_list.append(Rule(rule[0],rule[1]))


    graph = DependencyGraphModel(rule_list,graph_coloring=True)

    plt.figure(figsize=(args.figsize,args.figsize))

    #graph.show_graph()
    graph.plot_graph(save=True,file_name="Dump/" + args.rules.split('/')[-1],mode=args.mode)
