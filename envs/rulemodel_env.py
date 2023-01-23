import numpy as np
import glob
import gym
import gym.spaces

from base_structure.rulemodel import *

#なんかそういう
#環境あるんですか？
#
#　　　／￣￣￣＼
#　　／　　　　　＼
#　 /／|　　　　　 ヽ
#　//　ヽ(、　　　　|
#`/ｲヽ ／⌒＼　　　 |
#　|･)　(･＞ ヽ　　 |
#　|/　　　　 |　　 |
#　(_へ)ヽ　　|／|　|
#　 ﾚ亠ー､)　　 ノ　|
#　 ヽ二／　／　 ヽノ_
#／￣(wwww／　　/ |　 ＼
#　　|￣|　　 ／　|
#　　|／ヽ　 /⌒＼|　 /
#⌒⌒ヽ ﾟ|＼∧　 ／⌒二)
#∩∩ | ﾟ|　 ∧／　　ヽ


#
# -- 強化学習の環境を定義するクラス --
#
class rulemodel_env(gym.core.Env):
    #====================================
    #=            クラス初期化            =
    #====================================
    def __init__(self,rulelist,packetlist,experiment_title,additional_options):
        # パラメータを設定
        self.base_rulelist = rulelist
        self.rulelist = None
        self.packetlist = packetlist
        self.max_steps = 20000
        #self.max_stay = max_stay
        self.experiment_title = experiment_title
        self.steps = 0
        self.stay_num = 0
        self.before_delay = 0

        self.max_reward = -999999999
        self.episode_reward = -999999999

        self.prev_act = -1
        self.same_action_count = 0

        self.initial_reward = self.base_rulelist.filter(self.packetlist)[0] * -1

        # ルーリストの大きさとビット長（環境）を決定
        self.rulelist_len = len(rulelist)
        self.bit_string_len = len(rulelist[0]) + 1


        # 行動空間を設定(ルール数)
        self.action_space = gym.spaces.Discrete(self.rulelist_len)

        # 状態空間を設定(リスト長 x ビット長+1(評価型を先頭に付与))
        # bit値 0->0  1->1  *->2
        # 評価型 D->0  P->1
        self.observation_space = gym.spaces.Box(
            low=0,
            high=3,
            shape=(self.rulelist_len,self.bit_string_len),
            dtype=np.int16)


    def createRuleList(self):
        self.rulelist = RuleList()
        for i in range(len(self.base_rulelist)):
            self.rulelist.append(Rule(self.base_rulelist[i].evaluate,self.base_rulelist[i].bit_string))


    #====================================
    #=             環境初期化             =
    #====================================
    def _reset(self):
        self.steps = 0
        self.stay_num = 0
        self.episode_reward = -999999999
        self.createRuleList()

        self.same_action_count = 0
        self.prev_act = -1

        self.episode_reward = self.initial_reward

        return self._transform_rulelist_to_state()


    #====================================
    #=           1ステップの処理           =
    #====================================
    def _step(self,action):


        #変数初期化
        reward = 0
        done = False
        act = action - 1
        success = False

        #print(self.prev_act,act,self.same_action_count)

        if act == -1:
            done = True
            success = True
        elif act == self.prev_act:
            self.same_action_count += 1
            if self.same_action_count >= 3:
                done = True

        else:
            self.prev_act = act

            success = self.rulelist.action_moveOne(act,True)
            # 報酬計算
            if success:
                self.steps += 1

                #print(self.rulelist)
            else:
                done = True


        #print(act)


        # 終了判定
        if self.steps >= self.max_steps:
            done = True

        # 終了時に報酬の最高値を更新した場合、その際のルールリストを出力
        if done :
            if success and self.steps > 0 and self.same_action_count < 3:
                latency = self.compute_reward()
                reward = self.compute_reward() - self.initial_reward
                if reward > self.max_reward:
                    self.max_reward = reward
                    print("LATENCY = " + str(latency))
                    self.dump(self.rulelist,latency)

        return self._transform_rulelist_to_state(),reward,done,{}


    #====================================
    #= ルールリストを状態の構造へ変換する関数 =
    #====================================
    def _transform_rulelist_to_state(self):
        state = []            

        for i in range(len(self.rulelist)):
            element = []
            #先頭に評価型を数値として追加
            if self.rulelist[i].evaluate == "Accept":
                element.append(1)
            else:
                element.append(0)

            #残りの要素を追加
            element.extend(self.rulelist[i].bit_string_num)

            state.append(element)

        return state

    def dump(self,rulelist,reward):
        
        # 現在の最小値より大きい場合は出力しない(並列処理中に各プロセス間で最小値を共有できないのでフォルダ検索して確認)
        print([int(x.split('/')[-1].split('\\')[-1].split('s')[0]) for x in glob.glob("Dump/" + self.experiment_title + "/*sRULE")])
        exist_latency_list = [int(x.split('/')[-1].split('\\')[-1].split('s')[0]) for x in glob.glob("Dump/" + self.experiment_title + "/*sRULE")]
        if len(exist_latency_list) > 0:
            if -reward >= min(exist_latency_list):
                return

        print("\n\nNEW_REWARD -->>\t %d"%(-reward))

        with open("Dump/"+self.experiment_title+"/" + str(-reward) + "sRULE","w",encoding="utf-8",newline="\n") as write_file:

            for i in range(len(rulelist)):
                if rulelist[i].evaluate == "Accept":
                    write_file.write("Accept\t"+rulelist[i].bit_string+"\n")
                elif rulelist[i].evaluate == "Deny":
                    write_file.write("Deny\t"+rulelist[i].bit_string+"\n")

    #====================================
    #=         報酬を計算する関数          =
    #====================================
    # 報酬 -> アクション適用前後の遅延の差 - 各地点で得たマイナス報酬の総計
    def compute_reward(self):

        delay = self.rulelist.filter(self.packetlist)[0]
        ret = self.before_delay - delay
        self.before_delay = delay

        return delay * -1


    #====================================
    #=             未使用関数             =
    #====================================


    def _render(self):
        pass


    def _close(self):
        pass

    def _seed(self):
        pass