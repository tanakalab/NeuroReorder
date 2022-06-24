# 概要
ClassBenchで生成したルールリストとパケット集合を入力し、機械学習によりルール順序を最適化する。

# ライブラリバージョン
特定のバージョンが必要だと思われるものは**太字**にしています

## 基礎
- Python3.8以上
- graphviz
- pip

## ライブラリ
- tensorflow-cpu 2.5.0 (または tensorflow-gpu 2.7.0)
- tensorboard 2.7.0
- keras 2.4.3
- keras-rl2 1.0.5
- **gym 0.18.3**
- numpy 1.19.5
- matplotlib 3.3.4
- networkx 2.6.3

その他必要なライブラリを言われた場合は適時入れること。たしかpydotとかpillowとか言われた気がする。

# 実験手順
## 1サンプルに対して試行する場合
### (1) 実験サンプルの用意
ルールリストとパケット集合を用意する。田中研のClassBench生成プログラム(以下リンク)の5番`ZOMList.sh`でビット列を生成し、ルールリストファイルに対して`assign_evaluation_to_rulelist.py`を実行して評価型をランダム付与する。使い方は末尾の**各実行ファイルの使い方**を参照。

https://github.com/tanakalab/ClassBench

### (2) 実験実行
メインとなる実験の実行スクリプト`run_neuroreorder.py`を実行する。使い方は末尾の**各実行ファイルの使い方**を参照。

## 複数サンプルをまとめて実行する場合
### (1) 実験サンプルの用意 (準備中)
`****.sh`でClassBenchプログラムを複数回叩き、サンプル集合として1フォルダにまとめることができるので、これを使う。

### (2) 実験実行
`experiment.sh`で(1)で生成したフォルダを指定すると、その中にあるサンプルについて順番に学習を実行する。

LINE notifyでアクセストークンを発行することで、自身のLINEアカウントに実験完了した通知を送れる。(後述)

# 実験により出力されるデータ
実験によって出力されるデータは`Dump/[実験名]`に置かれる。
#### Rule_{番号}_{数値}
報酬の最大値を更新したときのルールリスト。番号は更新した順番、数値は報酬の値。
#### Actions_{番号}
報酬の最大値を更新したときの行動履歴。番号は *Rule_{番号}_{数値}* の番号と対応している。
#### nnw.hdf5
学習終了時のニューラルネットワーク。
#### episode_reward.png
報酬の遷移を示したグラフ。
#### nb_episode_steps.png
各エピソードにおける行動回数の遷移を示したグラフ。（ほぼ意味なし）

# 各実行ファイルの概要と使い方
引数に何をとればよいかについては、各ファイルのヘルプを開いてください。例えば `python3 run_neuroreorder.py --help`など。

## run_neuroreorder.py
メインとなる学習実験をする。引数は、ルールファイル、パケットファイル、実験名、最大ステップ数。

## assign_evaluation_to_rulelist.py
ClassBenchで生成したルールリストに評価型を付与する。引数は、ルールファイル、評価型(AcceptとDeny)の比率(0~100)。

## dump_dependency_graph.py
従属グラフを出力する。引数は、ルールファイル、パケットファイル、図の大きさ、出力モード、拡張子(pngまたはeps)。
#### 出力モードについて
重みをノードの大きさで表現する`normal`と、ゼミ資料などで従属グラフの構造を明瞭にするときなどに向けた`caption`の2つを実装済み。
##### 例
以下のようなルールリストを示しているファイルがあったとき、各モードでの出力結果について示す。

    Deny	*001
    Deny	*000
    Accept	101*
    Accept	001*
    Deny  1*10
    Deny  *101
    Accept	0*0*
    Deny	**11
    Accept	*11*
    Accept	110*
    Accept	1100

###### normal
![normal](https://user-images.githubusercontent.com/88485523/175473963-6699ea47-c6ce-4be6-a58e-a139f3c594ea.png)
###### caption
![caption](https://user-images.githubusercontent.com/88485523/175473958-cda41bc1-07d4-4eeb-b804-144dbfc783d1.png)

## filter_test.py
ルールリスト2つとパケット集合を入力し、2つのルール間に(パケット集合で確認できる範囲で)ポリシ違反がないかチェックする。引数は、ルールファイル、パケットファイル、(比較対象の)ルールファイル。

新しく実装したアルゴリズムがポリシ違反を起こしていないかのチェックに使用する想定。

## act_test.py
ルールリスト(並べ替え前)、行動履歴、パケット集合を入力し、行動履歴を基に従属グラフからノードを取り除く過程を動画(mp4)として出力する。引数は、並べ替え前のルールファイル、行動履歴ファイル、パケットファイル。

行動履歴を出力しない場合は行動を自分で選択する方式となる(準備中)


## notify.py
これを実行すると、ファイル`notify_token`に書いてあるアクセストークンに対応したLINEアカウントに`実験[実験名]が終了しました`というメッセージを飛ばす。引数は、実験名。

このリポジトリ内には`notify_token`は置いていないが、代わりに例として`notify_token-example`を置いている。これの名前を`notify_token`に変更し、中身を自身のLINEアカウントを基に生成したアクセストークンに書き換えること。アクセストークンの取得方法は各自でググってください。
