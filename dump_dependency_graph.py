
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
    "--packets",
    type=str,
    help="読み込むパケットファイルのパス. ")

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
    #パケットリストを形成
    packet_list = []
    if args.packets != None:
        with open(args.packets,mode="r") as packetlist_file:
            while packetlist_file:
                packet = "".join(packetlist_file.readline().split())
                #print(packet)
                if not packet:
                    break
                packet_list.append(packet)
    else:
        max_num = 2**len(rule_list[0].bit_string)
        specifier = "0"+str(len(rule_list[0].bit_string))+"b"
        for i in range(max_num):
            packet_list.append(format(i,specifier))


    graph = DependencyGraphModel(rule_list,packet_list)


    #graph.graph.remove_nodes_from([424,2,3,5,430,7,94,215,371,594,8,9,12,15,16,421,195,524,17,568,19,28,20,23,25,411,26,27])

    plt.figure(figsize=(args.figsize,args.figsize))

    #graph.show_graph()
    graph.plot_graph(save=True,file_name="Dump/" + args.rules.split('/')[-1],mode=args.mode)
