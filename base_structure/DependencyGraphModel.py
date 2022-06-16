# 従属グラフ構築と各種並べ替え法に関する処理をまとめたクラス

# ------------------------------------------------------------------
# -----                      ライブラリ定義                     -----
# ------------------------------------------------------------------
import math
# グラフ関連
import networkx as nx
import matplotlib.pyplot as plt
# 自前環境
from base_structure.rulemodel import *


class DependencyGraphModel:

    #=========================================
    #                 初期化
    #=========================================
    def __init__(self,rulelist,packetlist=None):

        rule_list = rulelist
        packet_list = packetlist

        if not packetlist is None:
            rulelist.compute_weight(packetlist)

        # 各手法の整列済みリスト（ルール番号のリスト）
        self.sgms_reordered_nodelist = []
        self.hikages_reordered_nodelist = []


        # グラフ構築(ノード)
        Graph = nx.DiGraph()
        for i in range(len(rule_list)):
            Graph.add_node(str(i+1))
        # グラフ構築(エッジ)
        edges = []
        for i in reversed(range(len(rule_list))):
            for j in reversed(range(0,i)):
                # 重複があるならエッジを追加
                if rule_list[j].is_dependent(rule_list[i]):
                    #重複ビット集合を示すビット列
                    overlap_bit_string = rule_list[j].match_packet_bit_string(rule_list[i])
                    mask_num = overlap_bit_string.count("*")
                    color = "r"
                    if mask_num <=24:
                        color = "lightsalmon"
                    elif mask_num >=48:
                        color = "purple"

                    edges.append((i+1,j+1,color))
                    Graph.add_edge(i+1,j+1,color=color)

        # グラフ構築(重みを表現し推移辺を削除したグラフを改めて構築)
        Graph2 = nx.DiGraph()
        for i in range(len(rule_list)):
            if rule_list[i]._weight == 0:
                Graph2.add_node(i+1,color="black",size=1)
            else:
                Graph2.add_node(i+1,color="red",size=rule_list[i]._weight)

        for i in range(len(edges)):
            Graph.remove_edge(edges[i][0],edges[i][1])
            if not nx.has_path(Graph,source=edges[i][0],target=edges[i][1]):
                Graph2.add_edge(edges[i][0],edges[i][1],color=edges[i][2])
            Graph.add_edge(edges[i][0],edges[i][1],color=edges[i][2])

        self.rule_list = rule_list
        # 初期グラフ(これをコピーして計算する)
        self.graph = Graph2

        # 計算用グラフ(このグラフ構造のノードを取り除く)
        self.calculate_graph = self.copied_graph()

        # 手法を適用しグラフから除去したノードリスト
        self.removed_nodelist = []

    #=======================================================
    #                      グラフを出力
    #=======================================================
    def plot_graph(self,file_name="figDump"):
        # 色とノードサイズをグラフデータとして構築
        node_color = [node["color"] for node in self.graph.nodes.values()]
        edge_color = [edge["color"] for edge in self.graph.edges.values()]
        node_size = [node["size"]*10 for node in self.graph.nodes.values()]
        # グラフを描く
        pos = nx.nx_pydot.pydot_layout(self.graph,prog='dot')
        nx.draw_networkx(self.graph,pos,edge_color=edge_color,node_color=node_color,node_size=node_size,font_size=1)
        # 出力
        plt.savefig(file_name + ".png")


    #=======================================================
    #手法で既に取り除かれているノードを除外した従属グラフを返す
    #=======================================================
    def create_cutted_graph(self):
        graph = self.copied_graph()
        for element in self.removed_nodelist:
            graph.remove_node(element)

        return graph

    #==========================================================
    #ノードがなくなったときに実行、リストを連結して返り値として返す
    #==========================================================
    def complete(self):
        #日景法の整列済みリストは逆順になっているのでリバース
        self.hikages_reordered_nodelist.reverse()
        #リストを連結して新しいリストにする
        reordered_nodelist = self.sgms_reordered_nodelist + self.hikages_reordered_nodelist

        ret_rulelist = RuleList()
        for i in range(len(reordered_nodelist)):
            ret_rulelist.append(self.rule_list[reordered_nodelist[i]-1])

        return ret_rulelist

    #=========================================
    # 部分グラフの重み平均を導出（SGMのサブ関数）
    #=========================================
    # souce -> 部分木の根
    def sum_of_weight_in_subgraph(self,src):

        sum_of_weight = 0
        keys = []
        dict = nx.shortest_path(self.graph,source=src)

        for key in dict.keys():
            sum_of_weight += self.rule_list[key-1]._weight
            keys.append(key)

        return (sum_of_weight,keys)

    #=======================================================
    # Gの重み平均一覧から対象のGを選択しreturn（SGMのサブ関数）
    #=======================================================
    # debugをTrueにすると、各Gの重み平均と選択したGを出力
    def decide_choice(self,keys,debug=False):
        _max = 0
        return_key = -1
        is_all_weight_is_zero = True
        for i in keys:
            ret = self.sum_of_weight_in_subgraph(i)
            if debug:
                print("[%4f] "%(ret),end="")

            ave = ret[0] / len(ret[1])
            if ave > _max:
                _max = ave
                return_key = i
                is_all_weight_is_zero = False

        #キーの重みがすべて0の場合は先頭の要素を選択
        if is_all_weight_is_zero:
            if debug:
                print("-> [%4f] "%(keys[0]))
            return keys[0]
        if debug:
            print("-> [%4f] "%(return_key))
        return return_key


    #=======================================================
    #                   SGMを１回だけ実行
    #=======================================================
    def single__sub_graph_mergine(self):

        # グラフをコピー
        #copied_graph = self.copied_graph()
        #for element in self.removed_nodelist:
        #    copied_graph.remove_node(element)

        #print(copied_graph.edges())
        _next = list(self.calculate_graph.nodes)

        while True:
            choice = self.decide_choice(_next)

            #print(_next,end="")
            if choice == -1:
                for i in _next:
                    #print("\t[r[%d]]"%(choice-1))
                    self.sgms_reordered_nodelist.append(i)
                    self.removed_nodelist.append(i)
                    self.calculate_graph.remove_node(i)
                    return i
                #print("BREAK.")
                break

            #print(" -> ",end="")
            #print("{choice={%d}} -> "%(choice),end="")
            #print(list(nx.shortest_path(copied_graph,target=choice).keys()),end="")


            _next = list(self.calculate_graph.succ[choice])
            #print(_next,end="")
            if len(_next) <= 0:
                #print("\t|r[%d]|"%(choice))
                self.sgms_reordered_nodelist.append(choice)
                self.removed_nodelist.append(choice)
                self.calculate_graph.remove_node(choice)
                #_next = list(self.graph.nodes)
                return choice
            #print("")

        return


    # グラフをコピー
    def copied_graph(self):
        ret_graph = nx.DiGraph()
        for node in list(self.graph.nodes):
            ret_graph.add_node(node)


        for edge in list(self.graph.edges):
            ret_graph.add_edge(edge[0],edge[1])


        return ret_graph

    def subgraph_nodesets(self,graph):
        subgraph_nodesets = []
        evallist = list(graph.nodes)
        #print(evallist)
        while len(evallist) > 0:
            dumplist = []
            pre_evals = []
            pre_evals.append(evallist[0])
            pre_evals += list(nx.all_neighbors(graph,evallist[0]))
            #print(pre_evals)
            while(len(pre_evals) > 0):
                # 先頭を取り出して評価対象とし、評価済みリストへ格納
                target_id = pre_evals.pop(0)
                dumplist.append(target_id)
                # 頂点集合を導出
                vertexs = list(nx.all_neighbors(graph,target_id))
                #print(vertexs)
                # 評価済みの頂点は除外
                new_evals = [vertex for vertex in vertexs if not vertex in dumplist]
                dumplist += new_evals
                pre_evals += new_evals
                #print("PREEVAL",end="")
                #print(pre_evals)
            subgraph_nodesets.append(list(set(dumplist)))
            evallist = [element for element in evallist if not element in dumplist]
        return subgraph_nodesets


    # 日景法により並べ替える
    def single__hikage_method(self):


        ret_rulelist = RuleList()
        sorted_list = []

        # グラフをコピー
        copied_graph = self.copied_graph()


        subgraph_nodesets = self.subgraph_nodesets(copied_graph)
        subgraph_nodesets_w = self.subgraph_nodesets(copied_graph)
        for subgraph_nodeset in subgraph_nodesets_w:
            for i in range(len(subgraph_nodeset)):
                subgraph_nodeset[i] = self.rule_list[subgraph_nodeset[i]-1]._weight
        #print(subgraph_nodesets)
        #print(subgraph_nodesets_w)

        ### 連結成分内の順序を表すリストN(に重みを付加したタプル)の生成

        Ns = []
        for subgraph_nodeset,subgraph_nodeset_w in zip(subgraph_nodesets,subgraph_nodesets_w):
            #cachelist = subgraph_nodeset #頂点集合
            N = []
            while len(subgraph_nodeset) > 0:
                # 現時点で入次数が0なノード番号を抽出
                matchedlist = [i for i in subgraph_nodeset if len(list(copied_graph.pred[i])) == 0]
                #print(matchedlist)
                # 抽出したノード番号に対応する重みリスト
                matchedlist_w = [subgraph_nodeset_w[i] for i in range(len(subgraph_nodeset)) if subgraph_nodeset[i] in matchedlist]
                #print(matchedlist_w)

                while(len(matchedlist) > 0):
                    # 重みの最小値の位置を導出
                    minimum_index = matchedlist_w.index(min(matchedlist_w))
                    # 構築済みNに(ノード番号,重み)のタプルとして格納し、元の頂点集合から削除
                    N.append((matchedlist[minimum_index],matchedlist_w[minimum_index]))
                    subgraph_nodeset.remove(matchedlist[minimum_index])
                    # グラフからも削除
                    copied_graph.remove_node(matchedlist[minimum_index])
                    # 抽出リストから削除
                    del matchedlist[minimum_index]
                    del matchedlist_w[minimum_index]

            N.reverse()
            Ns.append(N)

        #print("N : ",end="")

        for element in self.removed_nodelist:
            for N in Ns:
                for node in N:
                    if node[0] == element:
                        N.remove(node)
                if len(N) == 0:
                    Ns.remove(N)

        #print("Ns = ",end="")
        #print(Ns)

        # すべてのNが空になる(空になったNをNsから削除することでNの要素数で判定できる)まで
        while(len(Ns) > 0):

            ### Wを計算する
            Ws = []
            for N in Ns:
                w = []
                for i in reversed(range(len(N))):
                    w.append(sum([N[j][1] for j in reversed(range(i,len(N)))]) / (len(N)-i))
                #print(w)
                w.reverse()
                Ws.append(w)

            #print("Ws = ",end="")
            #print(Ws)

            ### 整列済みリストへ挿入するリストの先端位置の決定

            # 重みの最小値リストを構築
            minimum_weights = [min(W) for W in Ws]
            #print(minimum_weights)

            #Ns全体で最小の重みの値
            whole_minimum_weight = min(minimum_weights)

            #添字番号を決定
            index_Ns = minimum_weights.index(whole_minimum_weight)
            index_N = Ws[index_Ns].index(whole_minimum_weight)


            ### 整列済みリストへ挿入し、該当個所をNsから削除

            addlist = Ns[index_Ns][index_N:]
            addlist.reverse()
            sorted_list += addlist

            #print(addlist)

            for element in addlist:
                #self.hikages_reordered_rulelist.append(self.rule_list[element[0]-1])
                self.hikages_reordered_nodelist.append(element[0])
                self.removed_nodelist.append(element[0])




            return [element[0] for element in addlist]
            #Ns[index_Ns] = Ns[index_Ns][:index_N]

            #if len(Ns[index_Ns]) <= 0:
            #    del Ns[index_Ns]

            #print("現在の整列済みリスト [@@@@@]",end="")
            #print(sorted_list)
            #print("更新後のNs ========>>>>>>>>",end="")
            #print(Ns)




        sorted_list  = [sorted_list[i][0] for i in range(len(sorted_list))]
        sorted_list.reverse()
        #print("整列済みリストの順番:",end="")
        #print(sorted_list)
        for i in range(len(sorted_list)):
            ret_rulelist.append(self.rule_list[sorted_list[i]-1])

        #print(ret_rulelist)
        return ret_rulelist
