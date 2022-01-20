
import math
import argparse
import datetime
import time

import random

import networkx as nx
import matplotlib.pyplot as plt
"""
#gym関連
import gym
from gym.envs.registration import register
from tensorflow import keras
from rl.agents.dqn import DQNAgent
from rl.agents.sarsa import SARSAAgent
from rl.policy import LinearAnnealedPolicy
from rl.policy import EpsGreedyQPolicy
from rl.policy import BoltzmannQPolicy
from rl.memory import SequentialMemory
"""

#自前環境
from rulemodel import *
from DependencyGraphModel import *
from envs.rulemodel_env import rulemodel_env

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
    "--print_rulelist_detail",
    type=bool,
    default=False,
    help="ルールリストを出力するかどうか.")
parser.add_argument(
    "--dumpfig",
    type=bool,
    default=False,
    help="従属グラフを見たい場合はTrueにするとプロットする.")

parser.add_argument(
    "--algo",
    type=str,
    default="DQN",
    help="使用アルゴリズム.DQNまたはSARSA.")


if __name__ == "__main__":

    args = parser.parse_args()

    max_all_steps = 1000000
    max_steps = 2000
    
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
            
    #リストをprintする場合はする
    if args.print_rulelist_detail:
        print(rule_list)

    #フィルタリング
    
    #print("Start packet filtering.")
    #res1 = rule_list.filter(packet_list,False,False)
    #print("遅延合計値 = [%d]\n\nAll Packet is successfully filtered." % res1[0])
    #print(res1[1])
    
    rule_list.compute_weight(packet_list)
    """
    for i in rule_list:
        print("%d,"%(i._weight),end="")
    print("")
    """
    # グラフ構築のテスト

    for rule in rule_list:
        print(rule._weight)
    
    graph = DependencyGraphModel(rule_list)

    #print(graph.subgraph_nodesets())

    copied_graph = graph.copied_graph()

    pos = nx.nx_pydot.pydot_layout(copied_graph,prog='dot')
    nx.draw_networkx(copied_graph,pos,node_color=["y"])
    #plt.show()

    while len(graph.removed_nodelist) < len(list(graph.graph.nodes)):
        graph.show_graph()


        chosen_algorithm = random.randint(0,1) #input("使用アルゴリズム(SGMの\"s\"または日景の\"h\"):")
        if chosen_algorithm == 0:
            graph.single__sub_graph_mergine()
        elif chosen_algorithm == 1:
            graph.single__hikage_method()
        
        print("SGMの整列済みリスト：",end="")
        print(graph.sgms_reordered_nodelist)
        print("Hikageの整列済みリスト：",end="")
        print(graph.hikages_reordered_nodelist)
        
        
    final_nodelist = graph.complete()
    print(final_nodelist)
        
    #print(graph.sgms_reordered_rulelist)        
    #print(graph.hikages_reordered_nodelist)
    
    #print("Start packet filtering.")
    #res2 = graph.sgms_reordered_rulelist.filter(packet_list,False,False)
    #print("遅延合計値 = [%d]\n\nAll Packet is successfully filtered." % res2[0])
    #print(res2[1])

    
    #for i in range(len(res1[1])):
    #    if res1[1][i] != res2[1][i]:
    #        print("ERROR %d"%i)
    """
    with open("Dump/DumpRule","w",encoding="utf-8",newline="\n") as write_file:
        for i in range(len(rule_list2)):
            if rule_list2[i].evaluate == "Accept":
                write_file.write("Accept\t"+rule_list2[i].bit_string+"\n")
            elif rule_list2[i].evaluate == "Deny":
                write_file.write("Deny\t"+rule_list2[i].bit_string+"\n")
    """

