# メインとなる機械学習を行う処理

# ------------------------------------------------------------------
# -----                      ライブラリ定義                     -----
# ------------------------------------------------------------------
# 基本ライブラリ
import math
import argparse
import random
import os
# グラフライブラリとプロットライブラリ
import networkx as nx
import matplotlib.pyplot as plt

# 機械学習関連
import gym
from gym.envs.registration import register
from tensorflow import keras
from rl.agents.dqn import DQNAgent
from rl.policy import LinearAnnealedPolicy
from rl.policy import EpsGreedyQPolicy
from rl.memory import SequentialMemory

# 自前環境
from base_structure.rulemodel import *
from base_structure.base_structure import *
from base_structure.DependencyGraphModel import *
from envs.rulemodel_env import rulemodel_env
# ------------------------------------------------------------------


# ------------------------------------------------------------------
# -----                          引数                          -----
# ------------------------------------------------------------------
parser = argparse.ArgumentParser()

parser.add_argument(
    "rules",
    type=str,
    help="読み込むルールファイルのパス. ClassBenchルール変換プログラムの6番を使用し,assign_evaluation_to_rulelist.pyで評価型を付与すること.")
parser.add_argument(
    "--packets",
    type=str,
    default=None,
    help="読み込むパケットファイルのパス.ClassBenchルール変換プログラムの6番を使用すること.無指定の場合は一様分布(全ての場合のパケット1つずつ).")
parser.add_argument(
    "--experiment_title",
    type=str,
    default="EXPERIMENT",
    help="実験名.ファイルの出力名に使用.")
parser.add_argument(
    "--max_steps",
    type=int,
    default=500000,
    help="学習ステップ数.この回数行動したら学習終了.")

# ------------------------------------------------------------------

# ------------------------------------------------------------------
# -----                       main処理                         -----
# ------------------------------------------------------------------
if __name__ == "__main__":

    args = parser.parse_args()
    # ルールリストを形成
    rule_list = BS.create_rulelist(args.rules)
    # パケットリストを形成
    packet_list = BS.create_packetlist(args.packets,rule_list)

    # 学習ステップ数
    max_all_steps = args.max_steps

    # gymに環境を登録し、初期化変数を設定
    register(
        id='rulelistRecontrust-v0',
        entry_point='envs.rulemodel_env:rulemodel_env',
        kwargs={
            'rulelist':rule_list,
            'packetlist':packet_list,
            'experiment_title':args.experiment_title
        },
    )

    # 環境呼び出し
    env = gym.make('rulelistRecontrust-v0')

    # 環境初期化
    env.reset()

    # Kerasによるニューラルネットワークモデル作成

    nb_actions = env.action_space.n
    model = keras.models.Sequential([
        keras.layers.Flatten(input_shape=(1,) + env.observation_space.shape),
        keras.layers.Dropout(0.2),
        keras.layers.Dense(64,activation="relu",kernel_initializer=keras.initializers.TruncatedNormal(),kernel_regularizer=keras.regularizers.l2(0.001)),
        keras.layers.Dropout(0.5),
        keras.layers.Dense(64,activation="relu",kernel_initializer=keras.initializers.TruncatedNormal(),kernel_regularizer=keras.regularizers.l2(0.001)),
        keras.layers.Dropout(0.5),
        keras.layers.Dense(nb_actions,activation="softmax"),
    ])

    # モデル出力
    model.summary()


    # 実験ファイル保存用ディレクトリの作成・整理
    os.makedirs("Dump/"+args.experiment_title,exist_ok=True)


    # ------------------------- ここからKeras-RLの処理 ------------------------
    #経験蓄積メモリの定義
    memory = SequentialMemory(limit=500000, window_length=1,ignore_episode_boundaries=True)
    #ポリシの選択
    policy = LinearAnnealedPolicy(EpsGreedyQPolicy(),attr='eps',value_max=.9,value_min=.1,value_test=.05,nb_steps=max_all_steps/10*9)

    #Agent作成
    dqn = DQNAgent(
        model=model,
        nb_actions=nb_actions,
        memory=memory,
        gamma=.95,
        nb_steps_warmup=5000,
        batch_size=128,
        train_interval=5,
        target_model_update=5,
        policy=policy
    )
    #DQNAgentのコンパイル
    dqn.compile(keras.optimizers.Adam(lr=1e-8),metrics=['mae'])

    #学習開始
    history = dqn.fit(env,nb_steps=max_all_steps,visualize=False, verbose=1,log_interval=max_all_steps/10,nb_max_episode_steps=max_all_steps)

    #学習した重みを保存
    dqn.save_weights('nnw.hdf5',overwrite=True)

    #グラフ化
    plt.plot(history.history['nb_episode_steps'], label='nb_episode_steps',linewidth=1)
    plt.legend()
    plt.savefig("Dump/"+args.experiment_title+"/nb_episode_steps.png")
    plt.clf()
    plt.plot(history.history['episode_reward'], label='episode_reward',linewidth=1)
    plt.legend()
    plt.savefig("Dump/"+args.experiment_title+"/episode_reward.png")

    # ------------------------- ここまでKeras-RLの処理 ------------------------

# ------------------------------------------------------------------
