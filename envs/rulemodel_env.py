import numpy as np
import gym
import gym.spaces

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

        self.max_reward = -999999999
        self.episode_reward = 0
        
        #現在実装済みのアクションの数 (STAY、MOVEのふたつ)
        self.implemented_action_num = 2
        
        # ルーリストの大きさとビット長（環境）を決定
        self.rulelist_len = len(rulelist)
        self.bit_string_len = len(rulelist[0]) + 1


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
        self.rulelist = self.base_rulelist
        
        self.before_delay = self.rulelist.filter(self.packetlist)[0]
        
        return self._transform_rulelist_to_state()
        
        
    #====================================
    #=           1ステップの処理           =
    #====================================
    def _step(self,action):


        #変数初期化
        reward = 0
        done = False
        #print(action)

        # actionの値をタプル型へ変換
        typ = action % self.implemented_action_num
        action = action // self.implemented_action_num
        src = action % self.rulelist_len
        action = action // self.rulelist_len
        dst = action

        act = (typ,src,dst)

        #print(act)

        # action [i,j,k] アクションを実行
        # $=================$ アクション STAY $=================$
        # -> 何もせず待機（ただし報酬-1）
        if act[0] == 0:
            done = True
            #reward -= 1
            #self.stay_num += 1
        # $---------------------------------------------------$

        # $=================$ アクション MOVE $=================$
        # -> ルールjをルールkの位置へ移動（失敗した場合は報酬-10して状態維持
        elif act[0] == 1:

            success = False
            # 同値はエラーとして罰を与える
            if act[1] == act[2]:
                reward -= 10
                
            # 大小関係を意識しつつMOVEを実行
            elif act[1] > act[2]:
                success = self.rulelist.action_move(act[1],act[2])
            else:
                success = self.rulelist.action_move(act[2],act[1])

            # 報酬計算
            
            if success:
                reward += self.compute_reward()
            else:
                reward -= 10
        # $---------------------------------------------------$

        reward -= 1


        # 終了判定
        if self.stay_num >= self.max_stay:
            done = True
        if self.steps >= self.max_steps:
            done = True
        
        self.steps += 1
        self.episode_reward += reward
        
        # 終了時に報酬の最高値を更新した場合、その際のルールリストを出力
        if done and self.episode_reward > self.max_reward:
            self.max_reward = self.episode_reward
            print("\nNEW_MAX_REWARD -->> %d"%(self.max_reward))
            print(self.rulelist)
            print("遅延 => ",end="")
            print(self.rulelist.filter(self.packetlist)[0])
        
        
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


    
    #====================================
    #=         報酬を計算する関数          =
    #====================================
    # 報酬 -> アクション適用前後の遅延の差 - 各地点で得たマイナス報酬の総計
    def compute_reward(self):

        delay = self.rulelist.filter(self.packetlist)[0]
        ret = self.before_delay - delay
        self.before_delay = delay
        
        return ret
    
    
    #====================================
    #=             未使用関数             =
    #====================================
    

    def _render(self):
        pass

    
    def _close(self):
        pass

    def _seed(self):
        pass
