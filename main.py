import math
import argparse
import datetime
import time

#自前環境
from rulemodel import *
from print_message import *
from envs.rulemodel_env import rulemodel_env

#gym関連
import gym
from gym.envs.registration import register
from tensorflow import keras
from rl.agents.dqn import DQNAgent
from rl.agents.sarsa import SARSAAgent
from rl.policy import LinearAnnealedPolicy
from rl.policy import EpsGreedyQPolicy
from rl.policy import BoltzmannQPolicy
from rl.memory import SequentialMemory

#グラフ出力
import matplotlib.pyplot as plt



parser = argparse.ArgumentParser()

parser.add_argument(
    "rules",
    type=str,
    help="読み込むルールファイルのパス. ClassBenchルール変換プログラムの6番を使用し,assign_evaluation_to_rulelist.pyで評価型を付与すること.(使用せずに評価型付与の番号で作れたならそれでヨシ)")

parser.add_argument(
    "--packets",
    type=str,
    default=None,
    help="読み込むパケットファイルのパス.ClassBenchルール変換プログラムの6番を使用すること.無指定の場合は一様分布(全ての場合のパケット1つずつ).")

parser.add_argument(
    "--algo",
    type=str,
    default="DQN",
    help="使用アルゴリズム.DQNまたはSARSA.")


#うるせぇアルパカぶつけるぞ 
#Δ~~~~Δ 
#ξ ･ェ･ ξ 
#ξ　~　ξ 
#ξ　　 ξ 
#ξ　　　“~～~～〇 
#ξ　　　　　　 ξ 
#ξ　ξ　ξ~～~ξ　ξ 
#　ξ_ξξ_ξ　ξ_ξξ_ξ 
#　　ヽ(´･ω･)ﾉ 
#　　　 |　 / 
#　　　 UU"


#
# -- メイン処理 --
#
if __name__ == "__main__":

    args = parser.parse_args()
    # -- ルールリストを形成 --
    rule_list = RuleList()

    max_all_steps = 1000000
    max_steps = 2000
    
    
    with open(args.rules,mode="r") as rulelist_file:
        while rulelist_file:
            rule = rulelist_file.readline().split()
            #print(rule)
            if not rule:
                break
            rule_list.append(Rule(rule[0],rule[1]))

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

    rule_list.compute_weight(packet_list)

    

    #================================================================
    #=                       機械学習をする部分                        =
    #================================================================
    #参考にしたサイト : https://qiita.com/mahoutsukaino-deshi/items/54a30218a57c88798c17
    
    start_time = time.time()
    #gymに環境を登録し、初期化変数を設定
    register(
        id='rulelistRecontrust-v0',
        entry_point='envs.rulemodel_env:rulemodel_env',
        kwargs={
            'rulelist':rule_list,
            'packetlist':packet_list,
            'max_steps':max_steps,
            'max_stay':10
        },
    )

    #環境呼び出し
    env = gym.make('rulelistRecontrust-v0')

    #環境初期化
    env._reset()

    #Kerasによるニューラルネットワークモデル作成
    nb_actions = env.action_space_size
    print(nb_actions)
    model = keras.models.Sequential([
        keras.layers.Flatten(input_shape=(1,) + env.observation_space.shape),
        keras.layers.Dense(256,activation="elu"),
        keras.layers.Dense(256,activation="elu"),
        keras.layers.Dense(256,activation="elu"),
        keras.layers.Dense(256,activation="elu"),
        keras.layers.Dense(256,activation="elu"),
        keras.layers.Dense(nb_actions,activation="softmax"),
    ])

    model.summary()
    #経験蓄積メモリの定義
    memory = SequentialMemory(limit=50000, window_length=1,ignore_episode_boundaries=True)
    #ポリシの選択
    #policy = EpsGreedyQPolicy(eps=0.05)
    #policy = BoltzmannQPolicy(tau=1.,clip=(-500.,500.))
    policy = LinearAnnealedPolicy(EpsGreedyQPolicy(),attr='eps',value_max=.9,value_min=.1,value_test=.05,nb_steps=max_all_steps/4*3)
    #Agent作成

    dqn = None
    
    if args.algo == "DQN":
        dqn = DQNAgent(
            model=model,
            nb_actions=nb_actions,
            memory=memory,
            gamma=.95,
            nb_steps_warmup=100,
            batch_size=16,
            train_interval=5,
            target_model_update=5,
            policy=policy
        )
    elif args.algo == "SARSA":
        dqn = SARSAAgent(
            model=model,
            nb_actions=nb_actions,
            gamma=.95,
            nb_steps_warmup=100,
            train_interval=5,
            policy=policy
        )
    #DQNAgentのコンパイル
    dqn.compile(keras.optimizers.Adam(lr=1e-8),metrics=['mae'])

    
    #学習開始
    history = dqn.fit(env,nb_steps=max_all_steps,visualize=False, verbose=1,log_interval=max_all_steps/10,nb_max_episode_steps=max_steps)

    #学習した重みを保存
    dqn.save_weights('result.hdf5',overwrite=True)


    #グラフ化
    plt.plot(history.history['nb_episode_steps'], label='nb_episode_steps',linewidth=1)
    plt.legend()
    plt.savefig("Dump/"+str(start_time)+"_nb_episode_steps.png")
    plt.clf()
    #plt.show()
    plt.plot(history.history['episode_reward'], label='episode_reward',linewidth=1)
    plt.legend()
    plt.savefig("Dump/"+str(start_time)+"_episode_reward.png")
    #plt.show()

    
    """
    #==============ランダムなアクションを環境に適用するテスト==============
    for i in range(100):
        #ランダムなアクションを呼び出し
        action = env.action_space.sample()

        #1ステップ実行してパラメータを取得
        observation, reward, done, _ = env._step(action)

        #アクションと報酬を出力
        print(action,end="")
        print(reward)
    #===============================================================
    """

    
    """
    # -- メニュー表示 -- 
    Print_Message.print_menu(rule_list)

    except_input = False

    
    # -- メニュー項目選択 --
    while(not except_input):
        x = input(" >> ")

        if x == "1":
            Print_Message.print_error_unimplement()
        elif x == "2":
            Print_Message.print_error_unimplement()
        elif x == "3":
            Print_Message.print_error_unimplement()
        elif x == "q":
            print("終了します")
            exit()
        else:
            Print_Message.print_error_unexpect()
    """
