from rulemodel import *

# メッセージ出力用クラス
# 出力されるメッセージをここにまとめただけ.
# 
class Print_Message:

    @staticmethod
    def print_menu(rulelist):
        print("=========================================================================")
        print("============================= Neuro Reorder =============================")
        print("=========================================================================")
        print("<> ルール数：%d <>"%(len(rulelist)))
        print("== :MENU: 対応する値を入力してください。 ==")
        print("== 1 -> (未実装)ルールリストを手動操作する")
        print("== 2 -> (未実装)学習を開始する")
        print("== 3 -> (未実装)このルールリストにパケットを流す")
        print("== q -> 終了")

    @staticmethod
    def print_error_unimplement():
        print("[ERROR]未実装です")
    @staticmethod
    def print_error_unexpect():
        print("[ERROR]予期しない入力です")
    
