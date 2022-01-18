import math
import argparse
from rulemodel import *
import datetime
import networkx as nx
import matplotlib.pyplot as plt

#***********************************************
#*          グラフ構築と日景法実行クラス              *
#***********************************************
class HikageMethod:
    def __init__(self,rulelist):
        rule_list = rulelist


        #グラフ構築(ノード)
        Graph = nx.DiGraph()
        for i in range(len(rule_list)):
            Graph.add_node(str(i+1))

        edges = []
        for i in reversed(range(len(rule_list))):
            for j in reversed(range(0,i)):
                
                if rule_list[j].is_overlap(rule_list[i]):
                    if rule_list[j].is_dependent(rule_list[i]):
                        if rule_list[j].is_cover(rule_list[i]):
                            #print("ルール[%d]とルール[%d]は従属かつ被覆関係" % (i+1 , j+1))
                        
                            new_edge = (i+1,j+1)
                            edges.append(new_edge)
                        else:
                            #print("ルール[%d]とルール[%d]は従属関係" % (i+1 , j+1))
                            
                            new_edge = (i+1,j+1)
                            edges.append(new_edge)

                    elif rule_list[j].is_cover(rule_list[i]):
                        #print("ルール[%d]とルール[%d]は被覆関係" % (i+1 , j+1))
                        new_edge = (i+1,j+1)
                        edges.append(new_edge)
                    else:
                        #print("ルール[%d]とルール[%d]は重複関係" % (i+1 , j+1))
                        new_edge = (i+1,j+1)
                        edges.append(new_edge)

                        """
                        for x in edges:
                        if x[1] == new_edge[0]:
                        max = range(len(edges))
                        for k in max:
                        if edges[k][0] == x[0] and edges[k][1] == new_edge[1]:
                        edges.pop(k)
                        break
                        """
        for edge in edges:
            Graph.add_edge(edge[0],edge[1])
    
        Graph2 = nx.DiGraph()
        for i in range(len(rule_list)):
            Graph2.add_node(i+1)

        
        for i in range(len(edges)):
            Graph.remove_edge(edges[i][0],edges[i][1])
            if not nx.has_path(Graph,source=edges[i][0],target=edges[i][1]):
                Graph2.add_edge(edges[i][0],edges[i][1])
            Graph.add_edge(edges[i][0],edges[i][1])

        #print(edges)

        self.rule_list = rule_list
        self.graph = Graph2
    
            
    # souce -> 部分木の根
    def sum_of_weight_in_subgraph(self,src):

        sum_of_weight = 0
        keys = []
        dict = nx.shortest_path(self.graph,source=src)
        
        for key in dict.keys():
            sum_of_weight += self.rule_list[key-1]._weight
            keys.append(key)

        #if len(keys) <= 1:
        #    return False
        return (sum_of_weight,keys)

    def decide_choice(self,keys):
        _max = 0
        return_key = -1
        is_all_weight_is_zero = True
        for i in keys:
            ret = self.sum_of_weight_in_subgraph(i)
            #if ret == False and len(keys) <= 1:
            #    return False
            #print("%d-"%(ret[0]),end="")
            ave = ret[0] / len(ret[1])
            if ave > _max:
                _max = ave
                return_key = i
                is_all_weight_is_zero = False
                
            #print("[%d:%d]"%(i,ret[0]),end="")
        #print("")
        #キーの重みがすべて0の場合は先頭の要素を選択
        if is_all_weight_is_zero:
            return keys[0]
        return return_key

    
    def plot_graph(self,save=False):
        pos = nx.nx_pydot.pydot_layout(self.graph,prog='dot')
        nx.draw_networkx(self.graph,pos,node_color=["y"])
        if save:
            plt.savefig("figDump.png")
        
        #plt.show()
   

    def subgraph_nodesets(self):
        subgraph_nodesets = []
        evallist = list(self.graph.nodes)
        #print(evallist)
        while len(evallist) > 0:
            dumplist = []
            pre_evals = []
            pre_evals.append(evallist[0])
            pre_evals += list(nx.all_neighbors(self.graph,evallist[0]))
            #print(pre_evals)
            while(len(pre_evals) > 0):
                # 先頭を取り出して評価対象とし、評価済みリストへ格納
                target_id = pre_evals.pop(0)
                dumplist.append(target_id)
                # 頂点集合を導出
                vertexs = list(nx.all_neighbors(self.graph,target_id))
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
    def hikage_method(self):

        
        ret_rulelist = RuleList()
        sorted_list = []
        
        subgraph_nodesets = self.subgraph_nodesets()
        subgraph_nodesets_w = self.subgraph_nodesets()
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
                matchedlist = [i for i in subgraph_nodeset if len(list(self.graph.pred[i])) == 0]
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
                    self.graph.remove_node(matchedlist[minimum_index])
                    # 抽出リストから削除
                    del matchedlist[minimum_index]
                    del matchedlist_w[minimum_index]

            N.reverse()
            Ns.append(N)

        #print("N : ",end="")
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
            Ns[index_Ns] = Ns[index_Ns][:index_N]

            if len(Ns[index_Ns]) <= 0:
                del Ns[index_Ns]

            #print("現在の整列済みリスト [@@@@@]",end="")
            #print(sorted_list)
            #print("更新後のNs ========>>>>>>>>",end="")
            #print(Ns)


         
        
        sorted_list  = [sorted_list[i][0] for i in range(len(sorted_list))]
        sorted_list.reverse()
        print("整列済みリストの順番:",end="")
        print(sorted_list)
        for i in range(len(sorted_list)):
            ret_rulelist.append(self.rule_list[sorted_list[i]-1])

        #print(ret_rulelist)
        return ret_rulelist
