#!/bin/bash

# $1 -> 実験タイトル(実験サンプルをまとめたフォルダの名前)
# $2 -> サンプル数
# $3 -> シード名称
# $4 -> ルール数


# ClassBenchファイルがあるかチェック
ZOMLISTFILE="ClassBench/ZOMList.sh"
if [ ! -e $ZOMLISTFILE ];then
    echo "ERROR : ClassBenchファイルが存在しません."
    exit 1
fi

# 引数が正常かチェック
if [ $# != 4 ]; then
    echo "ERROR : 引数が異常です."
    exit 1
fi

echo "Datas/$1 に$2個の$3(ルール数:$4)サンプルを生成し,格納します."


mkdir Datas/$1
mkdir Datas/$1/Rule
mkdir Datas/$1/Packet
# 許可の比率
accept_ratio=50
# パケット倍率
packet_ratio=10
cd ClassBench

counter=1
while [ $counter -le $2 ]
do
    sh ZOMList.sh SA DA SP DP PROT FLAG $4 $3 $packet_ratio KARIRULE KARIPACKET
    python3 ../assign_evaluation_to_rulelist.py KARIRULE $accept_ratio
    mv assigned_KARIRULE ../Datas/$1/Rule/sample$counter
    mv KARIPACKET ../Datas/$1/Packet/sample$counter
    rm KARIRULE
	counter=`expr $counter + 1`
done

echo "生成は正常に終了しました."