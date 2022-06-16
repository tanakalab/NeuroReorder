# 強化学習の環境を定義するクラス
"""
なんかそういう
環境あるんですか？

　　　／￣￣￣＼
　　／　　　　　＼
　 /／|　　　　　 ヽ
　//　ヽ(、　　　　|
`/ｲヽ ／⌒＼　　　 |
　|･)　(･＞ ヽ　　 |
　|/　　　　 |　　 |
　(_へ)ヽ　　|／|　|
　 ﾚ亠ー､)　　 ノ　|
　 ヽ二／　／　 ヽノ_
／￣(wwww／　　/ |　 ＼
　　|￣|　　 ／　|
　　|／ヽ　 /⌒＼|　 /
⌒⌒ヽ ﾟ|＼∧　 ／⌒二)
∩∩ | ﾟ|　 ∧／　　ヽ
"""
# ------------------------------------------------------------------
# -----                      ライブラリ定義                     -----
# ------------------------------------------------------------------
import numpy as np
# 強化学習関連
import gym
import gym.spaces
# 自前クラス
from base_structure.rulemodel import *
from base_structure.base_structure import *
from base_structure.DependencyGraphModel import *



class rulemodel_env(gym.core.Env):
    #====================================
    #=            クラス初期化            =
    #====================================
    def __init__(self,rulelist,packetlist,experiment_title):
        # パラメータを設定
        self.rulelist = rulelist
        self.packetlist = packetlist
        self.init_graph = DependencyGraphModel(rulelist)
        self.calc_graph = None
        self.experiment_title = experiment_title

        self.dump_count = 1

        self.max_reward = -9999999999

        # ルールリストの重みを計算
        self.rulelist.compute_weight(self.packetlist)
        # 行動履歴を追うための記録リスト
        self.action_group = []

        #現在実装済みのアクションの数 (SGMと日景法の2つ)
        self.implemented_action_num = 2

        #行動空間の大きさを指定
        self.action_space = gym.spaces.Discrete(self.implemented_action_num)


        # 状態空間を指定
        # 1次元目　→　ノード番号のリスト
        #２次元目　→　各ノードの重み
        #３次元目　→　エッジリストの要素１つ目
        #４次元目　→　エッジリストの要素２つ目

        # 最大値→グラフのノード数かパケット集合の大きさのどちらか最大値
        self.observation_eachlength = max([len(list(self.init_graph.graph.nodes)),len(self.init_graph.graph.edges)])

        self.observation_space = gym.spaces.Box(
            low=0,
            high=max([len(list(self.init_graph.graph.nodes)),len(self.packetlist)]),
            shape=(4,self.observation_eachlength),
            dtype=np.int16)

    #====================================
    #=             環境初期化             =
    #====================================
    def reset(self):

        self.action_group = []
        # 従属グラフを初期化
        self.calc_graph =  DependencyGraphModel(self.rulelist)

        return self.transform_rulelist_to_state()

    #====================================
    #=           1ステップの処理           =
    #====================================
    def step(self,action):

        # 変数初期化
        done = False
        reward = 0

        # アクションの値によって使用する発見的解法を変更
        # 0 -> Sub Graph Merging
        if action == 0:
            chosed_nodes = self.calc_graph.single__sub_graph_mergine()
            self.action_group.append(("SGM",[chosed_nodes]))
        # 1 -> Hikage Method
        elif action == 1:
            chosed_nodes = self.calc_graph.single__hikage_method()
            self.action_group.append(("Hikage",chosed_nodes))

        # グラフからノードがなくなったら終了判定
        if len(self.calc_graph.removed_nodelist) >= len(list(self.calc_graph.graph.nodes)):
            done = True

        # 終了時処理
        if done:
            # 実行結果を連結し、ルールリストを構築
            reordered_rulelist = self.calc_graph.complete()

            # 報酬計算
            reward = (-1) * reordered_rulelist.filter(self.packetlist)[0]

            # 終了時に報酬の最高値を更新した場合、その際のルールリストを出力
            if reward > self.max_reward:
                self.max_reward = reward
                print("\n\nNEW_REWARD -->>\t %d"%(self.max_reward))
                self.dump(reordered_rulelist,reward)

        return self.transform_rulelist_to_state(),reward,done,{}


    #========================================
    #  現在のグラフを状態の構造へ変換する関数
    #========================================
    def transform_rulelist_to_state(self):

        # 除去後の現在のグラフを構築
        cutted_graph = self.init_graph.create_cutted_graph()

        cutted_graph_nodes = list(cutted_graph.nodes)
        cutted_graph_edges = list(cutted_graph.edges)

        node_list = [0] * self.observation_eachlength
        node_weight_list = [0] * self.observation_eachlength
        for i in range(len(cutted_graph_nodes)):
            # ノード一覧を構成
            node_list[i] = cutted_graph_nodes[i]
            #グラフノードの重みリストを構築
            node_weight_list[i] = self.rulelist[cutted_graph_nodes[i]-1]._weight

        #エッジリストを構築
        edge_list_from = [0] * self.observation_eachlength
        edge_list_to = [0] * self.observation_eachlength

        for i in range(len(list(cutted_graph.edges))):
            edge_list_from[i] = (cutted_graph_edges[i][0])
            edge_list_to[i] = (cutted_graph_edges[i][1])

        state = [node_list,node_weight_list,edge_list_from,edge_list_to]

        return state

    #====================================
    #=         報酬を計算する関数        =
    #====================================
    def compute_reward(self):
        # 重みによる報酬計算をする処理 (実装予定)
        return -1


    #======================================================
    #=        ルールリストと行動リストを出力する関数        =
    #======================================================
    def dump(self,rulelist,reward):
        # ルールリストを出力
        with open("Dump/"+self.experiment_title+"/Rule_{"+str(self.dump_count)+"}_["+str(reward)+"]","w",encoding="utf-8",newline="\n") as write_file:

            for i in range(len(rulelist)):
                if rulelist[i].evaluate == "Accept":
                    write_file.write("Accept\t"+rulelist[i].bit_string+"\n")
                elif rulelist[i].evaluate == "Deny":
                    write_file.write("Deny\t"+rulelist[i].bit_string+"\n")
        # 行動一覧を出力
        with open("Dump/"+self.experiment_title+"/Actions_{"+str(self.dump_count)+"}","w",encoding="utf-8",newline="\n") as write_file:
            for action in self.action_group:
                write_file.write(str(action[0]) + "\t" + " ".join(map(str,action[1])) + "\n")

        self.dump_count += 1

    #====================================
    #=             未使用関数             =
    #====================================


    def render(self):
        pass


    def close(self):
        pass

    def seed(self):
        pass
