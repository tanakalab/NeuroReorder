import numpy as np
import gym
import gym.spaces
import time

from rulemodel import *

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
    def __init__(self,rulelist,packetlist,max_steps,max_stay):
        # パラメータを設定
        self.base_rulelist = rulelist
        self.rulelist = rulelist
        self.packetlist = packetlist
        self.max_steps = max_steps
        self.max_stay = max_stay
        
        self.steps = 0
        self.stay_num = 0
        self.before_delay = 0
        self.delay = 0

        self.max_reward = -999999999
        self.episode_reward = 0

        #重みを計算しておく
        self.rulelist.compute_weight(self.packetlist)
        
        self.initial_delay = self.rulelist.filter(self.packetlist)[0]

        self.minimal_delay = self.initial_delay
        
        self.start_time = time.time()

        self.action_group = []
        
        #現在実装済みのアクションの数 (STAY、MOVEのふたつ)
        self.implemented_action_num = 2
        
        # ルーリストの大きさとビット長（環境）を決定
        self.rulelist_len = len(rulelist)
        self.bit_string_len = len(rulelist[0]) + 2


        # 行動空間を設定(0-STAY 1-MOVE)
        #self.action_space = gym.spaces.Discrete(2)

        #各次元の上限値
        # 1 -> アクション数
        # 2 -> ルール数 (アクション適用先のルール位置 , 一部アクションでは未使用)
        # 3 -> ルール数 (アクション適用先のルール位置2 (例：MOVE先))
        high = np.array(
            [
                self.implemented_action_num - 1,
                self.rulelist_len - 1,
                self.rulelist_len - 1,
            ],
            dtype=np.int16,)

        #行動空間の大きさ (NNの構築で使用)
        self.action_space_size = (self.implemented_action_num) * (self.rulelist_len) * (self.rulelist_len)



        
        self.action_space = gym.spaces.Box(
            low=0,
            high=high,
            shape=(3,),
            dtype=np.int16)
        
        
        # 状態空間を設定(リスト長 x ビット長+1(評価型を先頭に付与))
        # bit値 0->0  1->1  *->2
        # 評価型 D->0  P->1
        self.observation_space = gym.spaces.Box(
            low=0,
            high=3,
            shape=(self.rulelist_len,self.bit_string_len),
            dtype=np.int16)
        
    #====================================
    #=             環境初期化             =
    #====================================
    def _reset(self):
        self.steps = 0
        self.stay_num = 0
        self.episode_reward = 0
        #self.episode_reward = self.initial_delay
        self.action_group = []

        self.rulelist = RuleList()
        for i in range(len(self.base_rulelist)):
            self.rulelist.append(self.base_rulelist[i])
        #print(self.rulelist)
        self.before_delay = self.initial_delay
        
        return self._transform_rulelist_to_state()
        
        
    #====================================
    #=           1ステップの処理           =
    #====================================
    def _step(self,action):


        #変数初期化
        reward = 0
        done = False
        err_message = "Failed"
        self.steps += 1
        #print(action)

        # actionの値をタプル型へ変換
        typ = action % self.implemented_action_num
        action = action // self.implemented_action_num
        src = action % self.rulelist_len
        """
        expected_decline_src = self.rulelist.expected_decline_src()
        if len(expected_decline_src) <= 0:
            done = True
        else:
            src = expected_decline_src[src % len(expected_decline_src)]
        """
        action = action // self.rulelist_len
        dst = action

        #遅延現象が期待される移動先を出し、その中から選択
        
        expected_decline_list = self.rulelist.expected_decline_list(src)
        if len(expected_decline_list) <= 0:
            self.stay_num += 1
            dst = src
            #reward -= 1
        else:
            dst = expected_decline_list[action % len(expected_decline_list)]
        
        #if self.steps == 1:
        typ = 1
        
        act = (typ,src,dst)

        #print(expected_decline_src)
        #print(expected_decline_list)
        #print(act,end="")

        
        act_pass = False
        """
        for x in self.action_group:
            if src == x[0][1] and dst == x[0][2]:
                act_pass = True
                reward -= 0.001
                break
        """

        success = False
        
        #print(act)

        # action [i,j,k] アクションを実行
        # $=================$ アクション STAY $=================$
        # -> 何もせず待機（ただし報酬-1）
        if act[0] == 0:
            done = True
            #self.episode_reward -= self.max_steps / self.steps
            #reward -= 1
            #self.stay_num += 1
        # $---------------------------------------------------$

        # $=================$ アクション MOVE $=================$
        # -> ルールjをルールkの位置へ移動（失敗した場合は報酬-10して状態維持
        elif act[0] == 1:


            if not act_pass:
                
            
                # 同値はエラー
                if act[1] == act[2]:
                    pass
                    #reward -= 0.001
                
                # 大小関係を意識しつつMOVEを実行
                elif act[1] > act[2]:
                    success = self.rulelist.action_move(act[1],act[2])
                else:
                    success = self.rulelist.action_move(act[1],act[2])
                # 報酬計算
                if success:
                    #pass
                    self.stay_num = 0
                    reward += self.compute_reward()
                else:
                    pass
                    #reward -= 0.001
                #reward += self.compute_reward()
            else:
                pass
                #reward -= 0.001
            
            # $---------------------------------------------------$

        # 終了判定
        if self.stay_num >= self.max_stay:
            done = True
        if self.steps >= self.max_steps - 1:
            done = True

        #reward -= 1
        #reward += self.compute_reward()
        self.episode_reward += reward
        if success:
            arr = [act]
        else:
            arr = err_message
        self.action_group.append(arr)
        
        print("\n|%7d\t|%7d\t|%7.4f\t|%7.4f\t|<>|%7d\033[1A"%(self.steps,self.delay,reward,self.episode_reward,self.minimal_delay),end="")
            
        if done:
            #reward = 0
            delay = self.rulelist.filter(self.packetlist)[0]
            #delay = self.compute_reward()
            #reward += self.episode_reward
            #print(self.rulelist)

            #reward = -1 * (self.initial_delay - delay)
            #self.episode_reward += reward
            #print("\n|%7d\t|%7d\t|%7d\t%7d\033[1A"%(self.steps,delay,self.episode_reward,self.minimal_delay),end="")
            
            # 終了時に報酬の最高値を更新した場合、その際のルールリストを出力
            if delay < self.minimal_delay:
                #if self.episode_reward > self.max_reward:
                self.max_reward = self.episode_reward
                print("\n\nNEW_REWARD -->> %f"%(self.max_reward))
                if delay < self.minimal_delay:
                    self.minimal_delay = delay
                    print("NEW_MIN_DELAY -->> %d"%(self.minimal_delay))
                print("ACTION RECORD -> ",end="")
                print(self.action_group)

                #print(self.rulelist)
                print("遅延 => ",end="")
                print(self.rulelist.filter(self.packetlist)[0])
                self.dump(delay)
                

        else:
            self.episode_reward += reward

        #print(reward)
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
                element.append(-2)
            else:
                element.append(-1)
            #重みを追加
            element.append(self.rulelist[i].weight)

            #残りの要素を追加
            element.extend(self.rulelist[i].bit_string_num)

            state.append(element)

        return state


    
    #====================================
    #=         報酬を計算する関数          =
    #====================================
    # 報酬 -> アクション適用前後の遅延の差 - 各地点で得たマイナス報酬の総計
    def compute_reward(self):

        self.delay = self.rulelist.filter(self.packetlist)[0]
        ret = self.before_delay - self.delay
        self.before_delay = self.delay
        """
        if ret > 0:
            return 1
        elif ret < 0:
            return -200
        else:
            return -200
        """
        #return ret
        return ret


    def dump(self,delay):
        
        with open("Dump/Rule_"+str(self.start_time)+"_["+str(delay)+"]_"+str(time.time()),"w",encoding="utf-8",newline="\n") as write_file:
            
            for i in range(len(self.rulelist)):
                if self.rulelist[i].evaluate == "Accept":
                    write_file.write("Accept\t"+self.rulelist[i].bit_string+"\n")
                elif self.rulelist[i].evaluate == "Deny":
                    write_file.write("Deny\t"+self.rulelist[i].bit_string+"\n")

    
    #====================================
    #=             未使用関数             =
    #====================================
    

    def _render(self):
        pass

    
    def _close(self):
        pass
        
    def _seed(self):
        pass
