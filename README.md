# 概要
ClassBenchで生成したルールリストとパケット集合を入力し、機械学習によりルール順序を最適化する。

**このリポジトリは、ベースとなる機械学習アルゴリズムとして「Stable-baselines」を利用しています。**

# ライブラリバージョン
特定のバージョンを必須とするものは**太字**にしています

## 基礎
- **Python3.7系列**
- graphviz
- pip
- (MPI)
- cuda
- cudnn
cudaとcudnnは要求されるバージョンを見て、入れるか確認する。
どうしても入らない場合は下記ライブラリにおいて、tensorflow-cpuを代わりに利用するのも視野に入れる。

### MPIについて
stable-baselinesは、一部アルゴリズムで、並列処理を行う機構としてMPIを採用している。
#### Windowsの場合
MSMPI v10以上を導入する。

#### Linuxの場合
実験PC（adi）はMPIがうまく入らなかったのでMPIを入れていない。が、一部アルゴリズムが利用できないだけなので、基本的には無問題な模様。

もしそれらアルゴリズムを試すのならば、
https://qiita.com/lilyclef/items/f800cfc98811e2d0bda6
などを参考にしてOpenMPIを入れる。

## ライブラリ
- **tensorflow 1.14.0**
- tensorboard (tensorflow 1.14.0を入れた時のバージョンでOK)
- stable-baselines[mpi] (MPIが入らない場合はstable-baselinesにする)
- **gym 0.19.0**
- pyqt5
- pyglet
- numpy
- matplotlib
- networkx
- openpyxl

その他必要なライブラリを言われた場合は適時入れること。たしかpydotとかpillowとか言われた気がする。

# 実験手順
## 1サンプルに対して試行する場合
### (1) 実験サンプルの用意
ルールリストとパケット集合を用意する。田中研のClassBench生成プログラム(以下リンク)の5番`ZOMList.sh`でビット列を生成し、ルールリストファイルに対して`assign_evaluation_to_rulelist.py`を実行して評価型をランダム付与する。使い方は末尾の**各実行ファイルの使い方**を参照。

https://github.com/tanakalab/ClassBench

### (2) 実験実行
メインとなる実験の実行スクリプト`run_neuroreorder.py`を実行する。使い方は末尾の**各実行ファイルの使い方**を参照。

## 複数サンプルをまとめて実行する場合
### (1) 実験サンプルの用意
`create_sample.sh`でClassBenchプログラムを複数回叩き、サンプル集合として1フォルダにまとめることができるので、これを使う。

### (2) 実験実行
`experiment.sh`で(1)で生成したフォルダを指定すると、その中にあるサンプルについて順番に学習を実行する。

LINE notifyでアクセストークンを発行することで、自身のLINEアカウントに実験完了した通知を送れる。(後述)

# 実験により出力されるデータ
実験によって出力されるデータは`Dump/[実験名]`に置かれる。
#### {数値}sRULE
報酬の最大値を更新したときのルールリスト。数値は報酬の値。
#### {数値}sACTIONLIST
報酬の最大値を更新したときの行動履歴。番号は *{数値}sRULE* の番号と対応している。

# 各実行ファイルの概要と使い方
引数に何をとればよいかについては、各ファイルのヘルプを開いてください。例えば `python3 run_neuroreorder.py --help`など。

## run_neuroreorder.py
メインとなる学習実験をする。引数は、ルールファイル、パケットファイル、実験名、最大ステップ数、追加オプション、並列する環境の数。
    
    python3 run_neuroreorder.py Datas/TestData/Rule/sample1 --packets=Datas/TestData/Packet/sample1 --experiment_title=Test --max_steps=1000000 --num_env=12

### 追加オプションについて
対応する小文字をここに追加することで、一部の設定を変更できます。変更できる内容は以下。
#### 報酬計算方式
`r`を指定すると、初期設定である「フィルタリングを実行し遅延の値をそのまま報酬にする」方式から、「最初にフィルタリングして決定した各ルールの重みと並べ替え後の位置の積の和を報酬とする」方式に変更する。つまり、実質的に重み変動を考慮しない方式へ変更する。1エピソード毎のフィルタリング実行回数が減少するので実行速度は向上するが、学習精度が低下する。

    --additional_options = r



## assign_evaluation_to_rulelist.py
ClassBenchで生成したルールリストに評価型を付与する。引数は、ルールファイル、評価型(AcceptとDeny)の比率(0~100)。

## run_heuristics.py
既存の発見的解法で並べ替えを実行する。遅延の比較対象となる実験結果を用意するプログラム。引数は、ルールファイル、パケットファイル、発見的解法の名称（SGMまたはHikage）、実験名、サンプル番号。
後者の2つの引数を指定しない場合は、並べ替えと遅延計算で終了する。逆に指定した場合は、対応する実験結果フォルダ内にExcelファイルを構築し、その中に並べ替え結果を格納する。並べ替え前の遅延が計算されていない場合はそれも計算して格納する。
    
    python3 run_heuristics.py Datas/TestData/Rule/sample1 --packets=Datas/TestData/Packet/sample1 SGM

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

## act_analyze.py
ルールリスト(並べ替え前)、行動履歴、パケット集合を入力し、行動履歴を基に従属グラフからノードを取り除く過程を動画(mp4)として出力する。引数は、並べ替え前のルールファイル、行動履歴ファイル、パケットファイル。

行動履歴を出力しない場合は行動を自分で選択する方式となる(準備中)


## notify.py
これを実行すると、ファイル`notify_token`に書いてあるアクセストークンに対応したLINEアカウントに`実験[実験名]が開始(終了)しました`というメッセージを飛ばす。引数は、実験名、フラグ（開始or終了）。
実験用のシェルスクリプトから叩くことを想定している。

このリポジトリ内には`notify_token`は置いていないが、代わりに例として`notify_token-example`を置いている。これの名前を`notify_token`に変更し、中身を自身のLINEアカウントを基に生成したアクセストークンに書き換えること。アクセストークンの取得方法は各自でググってください。
