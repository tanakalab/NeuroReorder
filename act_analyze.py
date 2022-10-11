# 出力したアクションリストを分析する

# ------------------------------------------------------------------
# -----                      ライブラリ定義                     -----
# ------------------------------------------------------------------
import math
import argparse
import random
import numpy as np
# グラフ関連
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.animation as animation

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
    "--actions",
    type=str,
    help="run_neuroreorder.pyで生成した行動リストのファイルパス．"
)
parser.add_argument(
    "--packets",
    type=str,
    default=None,
    help="読み込むパケットファイルのパス.ClassBenchルール変換プログラムの6番を使用すること.無指定の場合は一様分布(全ての場合のパケット1つずつ).")
parser.add_argument(
    "--dump_movie",
    type=bool,
    default=False,
    help="行動履歴を動画として出力する場合はTrueにする．")


#=======================================================
#              グラフ画像を返す(動画作成用)
#=======================================================

def init_func():
    pass

def update(i,graph_title,action_list,node_initial_pos,graph):

    ax.cla()
    ax.set_xlim(xlim[0], xlim[1])
    ax.set_ylim(ylim[0], ylim[1])
    ax.axis('off')

    for j in range(i):
        graph.graph.remove_nodes_from(action_list[j][1])


    node_color = [node["color"] for node in graph.graph.nodes.values()]
    edge_color = [edge["color"] for edge in graph.graph.edges.values()]


    #node_initial_pos = nx.nx_pydot.pydot_layout(graph.graph,prog='dot')
    nx.draw_networkx(graph.graph,pos=node_initial_pos,edge_color=edge_color,node_color=node_color,font_size=1)
    plt.title(graph_title + "action_num=" + str(i))


# ------------------------------------------------------------------
# -----                       main処理                         -----
# ------------------------------------------------------------------
if __name__ == "__main__":

    args = parser.parse_args()

    #ルールリストを形成
    rule_list = BS.create_rulelist(args.rules)
    packet_list = BS.create_packetlist(args.packets,rule_list)
    rule_list.compute_weight(packet_list)

    if args.actions != None:
        action_list = BS.create_actionlist(args.actions)

    # グラフ構築のテスト

    graph = DependencyGraphModel(rule_list)

    fig, ax = plt.subplots(1, 1, figsize=(30, 30))
    pos = nx.nx_pydot.pydot_layout(graph.graph,prog='dot')
    # フレームの軸を固定
    array_pos = np.array(list(pos.values()))
    max_xy, min_xy = np.max(array_pos, axis=0), np.min(array_pos, axis=0)
    range_x, range_y = max_xy[0] - min_xy[0], max_xy[1] - min_xy[1]
    xlim = [min_xy[0] - range_x*0.05, max_xy[0] + range_x*0.05]
    ylim = [min_xy[1] - range_y*0.05, max_xy[1] + range_y*0.05]


    if args.actions == None:
        while len(graph.removed_nodelist) < len(list(graph.graph.nodes)):
            chosen_algorithm = input("使用アルゴリズム(SGMの\"s\"または日景の\"h\"):")
            if chosen_algorithm == "s":
                print(graph.single__sub_graph_mergine())
            elif chosen_algorithm == "h":
                print(graph.single__hikage_method())
            elif chosen_algorithm == "w":
                graph.simple_weight_choose()

            graph.show()
            #print("Ns = ",end="")
            #print(graph.Ns)
            """
            subgraph_nodesets = graph.subgraph_nodesets(graph.calculate_graph)
            subgraph_nodesets_w = graph.subgraph_nodesets(graph.calculate_graph)
            for subgraph_nodeset in subgraph_nodesets_w:
                for i in range(len(subgraph_nodeset)):
                    subgraph_nodeset[i] = graph.rule_list[subgraph_nodeset[i]-1]._weight
            print(graph.alignment_subgraph_nodesets(subgraph_nodesets,subgraph_nodesets_w,graph.calculate_graph))
            """
            #print("\t",end="")
            #print(graph.nodepositions_inNs.items())
        graph.complete()
        exit()

    else:

        print("SGM    Percentage : %8f"%(len([sgm[0] for sgm in action_list if sgm[0] == "SGM"])/ len(action_list)))
        print("Hikage Percentage : %8f"%(len([sgm[0] for sgm in action_list if sgm[0] == "Hikage"])/ len(action_list)))
        print("SWC    Percentage : %8f"%(len([sgm[0] for sgm in action_list if sgm[0] == "SWC"])/ len(action_list)))


        


        if not args.dump_movie:
            exit()

        print("START MP4 CREATE")

        ani = animation.FuncAnimation(fig,update,init_func=init_func,fargs = ("GRAPH",action_list,pos,graph),interval=300,frames=len(action_list))
        ani.save("Dump/Process.mp4",writer='ffmpeg')
