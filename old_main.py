import math
import argparse
from rulemodel import *
import datetime

parser = argparse.ArgumentParser()

parser.add_argument(
    "rules",
    type=str,
    help="読み込むルールファイルのパス. ClassBenchルール変換プログラムの6番を使用し,assign_evaluation_to_rulelist.pyで評価型を付与すること.")
parser.add_argument(
    "--rules2",
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
            
    rule_list2 = RuleList()
    
    with open(args.rules2,mode="r") as rulelist_file:
        while rulelist_file:
            rule = rulelist_file.readline().split()
            #print(rule)
            if not rule:
                break
            rule_list2.append(Rule(rule[0],rule[1]))

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

    
    #フィルタリング
    print("Start packet filtering.")
    res1 = rule_list.filter(packet_list,True,True)
    print("遅延合計値 = [%d]\n\nAll Packet is successfully filtered." % res1[0])
    

    #リストをprintする場合はする
    if args.print_rulelist_detail:
        print(rule_list)

    #フィルタリング
    print("Start packet filtering.")
    res1 = rule_list.filter(packet_list,True,True)
    print("遅延合計値 = [%d]\n\nAll Packet is successfully filtered." % res1[0])

    #フィルタリング
    print("Start packet filtering.")
    res2 = rule_list2.filter(packet_list,True,True)
    print("遅延合計値 = [%d]\n\nAll Packet is successfully filtered." % res2[0])

    for i in range(len(res1[1])):
        if res1[1][i] != res2[1][i]:
            print("ERROR")
    
    #print(rule_list.expected_decline_src())
        
    """
    start = datetime.datetime.today()
    print("STARTED DEOVERLAP\t" + str(start))

    rule_list.deoverlap_all()
    
    #print(rule_list)

    res2 = rule_list.filter(packet_list,True)
    print("遅延合計値 = [%d]\n\nAll Packet is successfully filtered." % res2[0])
    print(len(rule_list))

    
    compliance_rate = 0
    for i in range(len(res1[1])):
        if res1[1][i] == res2[1][i]:
            compliance_rate += 1
        else:
            print("WARNING[" + str(i) + "]" + res1[1][i] + "|" + res2[1][i])
    compliance_rate = compliance_rate / len(res1[1]) * 100

    print("パケット適合率 :" + str(compliance_rate) + "%")
    print("START TIME (DEOVERLAP)\t" + str(start))
    print("ALL PROGRAM COMPLETED!\t" + str(datetime.datetime.today()))

    """

    """
    for i in range(len(rule_list)):
        for j in range(i+1,len(rule_list)):
            if rule_list[i].is_adjacent(rule_list[j]):
                print("%d %d IS ADJACENT." % (i,j))
            #else:
            #print("%d %d NOT ADJACENT." % (i,j))
    """
    """
    print("TEST MODE")
    for i in range(len(rule_list)):
        test_rule = Rule("Accept","0100100001110010011111000*******1001111001011101011001101010110*****************00000000001*****00000110***0**1*********")
        if rule_list[i].is_adjacent(test_rule):
            print("%d test_rule IS ADJACENT." % (i))
    """
