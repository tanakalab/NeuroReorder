import math
import argparse
from rulemodel import *
import datetime
from print_message import *

parser = argparse.ArgumentParser()

parser.add_argument(
    "rules",
    type=str,
    help="読み込むルールファイルのパス. ClassBenchルール変換プログラムの6番を使用し,assign_evaluation_to_rulelist.pyで評価型を付与すること.(使用せずに評価型付与の番号で作れたならそれでヨシ)")

if __name__ == "__main__":

    args = parser.parse_args()
    # -- ルールリストを形成 --
    rule_list = RuleList()
    
    with open(args.rules,mode="r") as rulelist_file:
        while rulelist_file:
            rule = rulelist_file.readline().split()
            #print(rule)
            if not rule:
                break
            rule_list.append(Rule(rule[0],rule[1]))


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
