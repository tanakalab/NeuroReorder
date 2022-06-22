#!/bin/bash

# $1 -> 実験タイトル(実験サンプルをまとめたフォルダの名前)
# $2 -> サンプル数
# $3 -> 最大ステップ数

echo "Datas/$1/ 内の$2サンプルについて実験します."

mkdir Dump/$1

counter=1

while [ $counter -le $2 ]
do
	echo "サンプル $counter 処理開始"
	python3 dump_dependency_graph.py Datas/$1/Rule/sample$counter --packets=Datas/$1/Packet/sample$counter --figsize=50
	python3 run_neuroreorder.py Datas/$1/Rule/sample$counter --packets=Datas/$1/Packet/sample$counter --experiment_title=sample$counter --max_steps=$3
	mv Dump/sample$counter Dump/$1/
	mv Dump/sample$counter.png Dump/$1/sample$counter/dependency_graph.png
	echo "サンプル $counter 処理終了"
	counter=`expr $counter + 1`
done
python3 notify.py --experiment_title=$1