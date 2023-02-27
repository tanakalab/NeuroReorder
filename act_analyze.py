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
    "--figsize",
    type=int,
    default=100,
    help="図のサイズ.")
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

    node_size = [node["size"]*10 for node in graph.graph.nodes.values()]

    nx.draw_networkx(graph.graph,pos=node_initial_pos,node_color="white",node_size=node_size,width=0.25,arrowsize=3,edgecolors="black",with_labels=False)
    
    if action_list[i][0] == "SWC":
        plt.title("CRS")
    else:
        plt.title(action_list[i][0])


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
    pos = nx.nx_pydot.pydot_layout(graph.graph,prog='dot')
    
    fig, ax = plt.subplots(1, 1, figsize=(args.figsize, args.figsize))
    # フレームの軸を固定
    array_pos = np.array(list(pos.values()))
    max_xy, min_xy = np.max(array_pos, axis=0), np.min(array_pos, axis=0)
    range_x, range_y = max_xy[0] - min_xy[0], max_xy[1] - min_xy[1]
    xlim = [min_xy[0] - range_x*0.05, max_xy[0] + range_x*0.05]
    ylim = [min_xy[1] - range_y*0.05, max_xy[1] + range_y*0.05]
    

    if args.actions == None:    
        plt.figure(figsize=(1,1))
        while len(graph.removed_nodelist) < len(list(graph.graph.nodes)):
            chosen_algorithm = input("使用アルゴリズム(SGMの\"s\"または日景の\"h\"):")
            if chosen_algorithm == "s":
                print(graph.single__sub_graph_mergine())
            elif chosen_algorithm == "h":
                print(graph.single__hikage_method())
            elif chosen_algorithm == "w":
                print(graph.simple_weight_choose())
            elif chosen_algorithm == "r":
                print(graph.single__reversing_sub_graph_mergine())

            graph.show()
            
        graph.complete()
        exit()

    else:
        
        print("SGM    Percentage : %8f"%(len([sgm[0] for sgm in action_list if sgm[0] == "SGM"])/ len(action_list)))
        print("Hikage Percentage : %8f"%(len([sgm[0] for sgm in action_list if sgm[0] == "Hikage"])/ len(action_list)))
        print("SWC    Percentage : %8f"%(len([sgm[0] for sgm in action_list if sgm[0] == "SWC"])/ len(action_list)))
        print("AuxHKG Percentage : %8f"%(len([sgm[0] for sgm in action_list if sgm[0] == "AuxHKG"])/ len(action_list)))
        print("RSGM   Percentage : %8f"%(len([sgm[0] for sgm in action_list if sgm[0] == "RSGM"])/ len(action_list)))

        if not args.dump_movie:
            exit()

        print("START MP4 CREATE")
        """
        # 1フレームごとにepsを出したりしたい場合はここからコメントアウト

        plt.figure(figsize=(args.figsize,args.figsize))

        # 実験結果まとめフォルダ作成
        os.makedirs('Dump/ActProceeds',exist_ok=True)
        for i in range(len(action_list)):
            plt.cla()
            plt.xlim(xlim[0],xlim[1])
            plt.ylim(ylim[0],ylim[1])
            plt.gca().spines['right'].set_visible(False)
            plt.gca().spines['left'].set_visible(False)
            plt.gca().spines['top'].set_visible(False)
            plt.gca().spines['bottom'].set_visible(False)
            plt.subplots_adjust(left=0, right=1, bottom=0, top=1)
            for j in range(i):
                graph.graph.remove_nodes_from(action_list[j][1])

            node_size = [node["size"]*10 for node in graph.graph.nodes.values()]            
            nx.draw_networkx(graph.graph,pos=pos,node_color="white",node_size=node_size,width=0.25,arrowsize=3,edgecolors="black",with_labels=False)
            plt.title(action_list[i][0])
            plt.savefig("Dump/ActProceeds/" +  '{:0=10}'.format(i) + ".eps")
        # ここまで
        """

        # 動画で出したい場合はここからコメントアウト
        ani = animation.FuncAnimation(fig,update,init_func=init_func,fargs = ("GRAPH",action_list,pos,graph),interval=50,frames=len(action_list))
        ani.save("Dump/Process.mp4",writer='ffmpeg')
        # ここまで