import math
import argparse
from rulemodel import *
import datetime
import networkx as nx
import matplotlib.pyplot as plt

#***********************************************
#*          グラフ構築とSGM実行クラス              *
#***********************************************
class SGM:
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
    


    def sub_graph_mergine(self):
        ret_rulelist = RuleList()
        _next = list(self.graph.nodes)
        
        while len(list(self.graph.nodes)) > 0:
            choice = self.decide_choice(_next)
            
            #print(_next,end="")
            if choice == -1:
                for i in _next:
                    ret_rulelist.append(self.rule_list[i-1])
                #print("BREAK.")
                break
            
            #print(" -> ",end="")
            #print("{={%d}=} -> "%(choice),end="")
            _next = list(self.graph.succ[choice])
            #print(_next,end="")
            if len(_next) <= 0:
                ret_rulelist.append(self.rule_list[choice-1])
                #print("\t|r[%d]|"%(choice-1),end="")
                self.graph.remove_node(choice)
                _next = list(self.graph.nodes)
            #print("")

        return ret_rulelist
                
                
    
