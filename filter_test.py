
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
    "--comparing_rules",
    type=str,
    help="比較対象となる読み込むルールファイルのパス. ClassBenchルール変換プログラムの6番を使用し,assign_evaluation_to_rulelist.pyで評価型を付与すること.")

if __name__ == "__main__":

    args = parser.parse_args()

    #ルールリストを形成
    rule_list = RuleList()
    rule_list2 = RuleList()

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

    if args.comparing_rules != None:
        with open(args.comparing_rules,mode="r") as rulelist_file:
            while rulelist_file:
                rule = rulelist_file.readline().split()
                #print(rule)
                if not rule:
                    break
                rule_list2.append(Rule(rule[0],rule[1]))
    #フィルタリング
    res1 = None
    res2 = None


    print("Start packet filtering.")
    res1 = rule_list.filter(packet_list,False,True)
    print("遅延合計値 = [%d]\n\nAll Packet is successfully filtered." % res1[0])
    #print(res1[1])
    if args.comparing_rules != None:
        print("Start packet filtering.")
        res2 = rule_list2.filter(packet_list,False,True)
        print("遅延合計値 = [%d]\n\nAll Packet is successfully filtered." % res2[0])
        #print(res2[1])

    for i in range(len(res1[1])):
        if res1[1][i] != res2[1][i]:
            print("ポリシ違反があります.")
            exit()
    print("ポリシは正常です")
