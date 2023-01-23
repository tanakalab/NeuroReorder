# メインとなる機械学習を行う処理

# ------------------------------------------------------------------
# -----                      ライブラリ定義                     -----
# ------------------------------------------------------------------
# 基本ライブラリ
import math
import argparse
import random
import os
import glob
# グラフライブラリとプロットライブラリ
import networkx as nx
import matplotlib.pyplot as plt

# 機械学習関連
import gym
from gym.envs.registration import register
import tensorboard
from stable_baselines.common.vec_env import DummyVecEnv
from stable_baselines.common.vec_env import SubprocVecEnv
from stable_baselines import PPO2
from stable_baselines.common import set_global_seeds

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
parser.add_argument(
    "--additional_options",
    type=str,
    default="",
    help="追加の設定をアルファベット小文字で指定する.詳細はリポジトリ上のドキュメント参照.")
parser.add_argument(
    "--sample_number",
    type=int,
    default=None,
    help="サンプル番号.Excelに結果を書き込む場合は指定.")
parser.add_argument(
    "--num_env",
    type=int,
    default=1,
    help="マルチプロセッシングする際の環境の数.")


# ------------------------------------------------------------------

# ------------------------------------------------------------------
# -----                   追加設定を仕込む                      -----
# ------------------------------------------------------------------
# r が入っている -> 重み変動を考慮しない形式
ENV_ID = 'rulelistRecontrust-v0'

def make_env(env_id,rank,seed=0):
    def _init():
        env = gym.make(env_id)
        env.seed(seed + rank)
        return env
    set_global_seeds(seed)
    return _init

# ------------------------------------------------------------------
# -----                       main処理                         -----
# ------------------------------------------------------------------
def main():
    args = parser.parse_args()
    # ルールリストを形成
    rule_list = BS.create_rulelist(args.rules)
    # パケットリストを形成
    packet_list = BS.create_packetlist(args.packets,rule_list)

    # 学習ステップ数
    max_all_steps = args.max_steps


    # 追加オプションの初期設定
    additional_options = {
        "reward_formula":Reward_Formula.filter,     # 報酬設計
        "sample_number":args.sample_number          # Excelに書き込む際の位置(サンプル番号)
    }

    additional_options["reward_formula"] = Reward_Formula.init_weight if 'r' in args.additional_options else Reward_Formula.filter

    # gymに環境を登録し、初期化変数を設定
    register(
        id='rulelistRecontrust-v0',
        entry_point='envs.rulemodel_env:rulemodel_env',
        kwargs={
            'rulelist':rule_list,
            'packetlist':packet_list,
            'experiment_title':args.experiment_title,
            'additional_options':additional_options
        },
    )

    # 環境呼び出し
    env = gym.make('rulelistRecontrust-v0')

    # 実験結果まとめフォルダ作成
    os.makedirs('Dump/'+args.experiment_title,exist_ok=True)

    # tensorboard用ログフォルダ作成
    log_dir = 'Dump/'+args.experiment_title
    if args.sample_number != None:
        log_dir = 'Dump/sample' + str(args.sample_number)
        os.makedirs(log_dir,exist_ok=True)


    # 学習試行
    train_env = SubprocVecEnv([lambda: env for i in range(args.num_env)])
    model = PPO2('MlpLstmPolicy',train_env,verbose=1,tensorboard_log=log_dir,
    n_steps=8,
    nminibatches=12,
    learning_rate=0.00001,
    gamma=0.975)
    model.learn(total_timesteps = args.max_steps)
    train_env.close()


    # Excelに書き込み
    if args.sample_number == None:
        exit()

    position = 'B' + str(1+args.sample_number)
    # 出力されたファイル群から遅延の最小値を取得
    minimum_latency = min([x.split('/')[-1].split('\\')[-1].split('s')[0] for x in glob.glob("Dump/sample" + str(args.sample_number) + "/*sRULE")])


    ExcelController.write_result_to_excel(args.experiment_title,position,minimum_latency)
    print("EXCELにNeuroReorderサンプル"+str(args.sample_number)+"の結果値を書き込みました.")



    """
    # テスト試行
    test_env = DummyVecEnv([lambda: gym.make(ENV_ID)])    
    state = test_env.reset()
    while True:
        action,_ = model.predict(state,deterministic=True)
        state,rewards,done,info = test_env.step(action)
        if done:
            print("遅延：" + str(rewards))
            break
    test_env.close()
    """
if __name__ == "__main__":
    main()
