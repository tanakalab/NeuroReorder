# ルール・ルールリストを定義するクラス

"""
  嘘は嘘であると
  見抜けぬ人でないと
  (このクラスを使うことは)難しい
　　　　＿＿_＿
　　　／へへ　 ＼
　　／／⌒⌒＼　 ＼
　 / /　　　　ヽ　 ヽ
　｜｜ヽ　／⌒ |　　|
　 ﾚY-･／　-･- ヽ　 |
　　| /　　　　 Ｖ) |
　　|(＿つ　 ･　 丿ノ
　　|＜三三＞)　/ /
　　ヽ　ﾞﾞ　　／ﾚｿ
　　　＼从ww／　｜
　　　　/)￣　　∧
　　　／ﾚヽ　 ／ |＼
　　 ｜|　|　｜⌒ |｜
"""

# ------------------------------------------------------------------
# -----                      ライブラリ定義                     -----
# ------------------------------------------------------------------
import math
import time

# ------------------------------------------------------------------
# -----                         ルール                         -----
# ------------------------------------------------------------------
class Rule:

    #====================================
    #=              初期化               =
    #====================================
    # evaluate -> 評価値
    # bit_string -> ルールのbit列
    def __init__(self, evaluate, bit_string):
        self.evaluate = evaluate
        self.bit_string = bit_string
        #Gymの環境で使うString型のbit列をint配列へ変換した要素の作成(マスクは2とする)
        self.bit_string_num = []
        for i in range(len(bit_string)):
            if bit_string[i] == "*":
                self.bit_string_num.append(2)
            elif bit_string[i] == "0":
                self.bit_string_num.append(0)
            else:
                self.bit_string_num.append(1)
        #重み
        self._weight = 0

    #====================================
    #=     合致するかどうか確認する関数      =
    #====================================
    # 引数 -> パケットのbit列 bit_string
    # 返り値 -> True or False
    def match(self,bit_string):
        assert len(self.bit_string) == len(bit_string),"入力されたパケットのbit列の長さがルールのbit列と異なります."

        for i in range(len(self.bit_string)):
            if self.bit_string[i] != "*":
                if self.bit_string[i] != bit_string[i]:
                    return False
        return True

    #====================================
    #=         重複を判定する関数          =
    #====================================
    # 引数 -> 対象ルール
    # 返り値 -> True or False
    def is_overlap(self,rule):
        assert len(self.bit_string) == len(rule.bit_string),"入力されたルールのbit列の長さが異なります."
        for i in range(len(self.bit_string)):
            if self.bit_string[i] != "*" and rule.bit_string[i] != "*":
                if self.bit_string[i] != rule.bit_string[i]:
                    return False
        return True

    #====================================
    #=         被覆を判定する関数          =
    #====================================
    # 引数 -> 対象ルール
    # 返り値 -> True or False
    def is_cover(self,rule):
        assert len(self.bit_string) == len(rule.bit_string),"入力されたルールのbit列の長さが異なります."
        if self.is_overlap(rule):
            for i in range(len(self.bit_string)):
                if self.bit_string[i] != rule.bit_string[i]:
                    if rule.bit_string[i] == "*":
                        return False
            return True

    #====================================
    #=         従属を判定する関数          =
    #====================================
    # 引数 -> 対象ルール
    # 返り値 -> True or False
    def is_dependent(self,rule):
        assert len(self.bit_string) == len(rule.bit_string),"入力されたルールのbit列の長さが異なります."
        if self.is_overlap(rule):
            if self.evaluate != rule.evaluate:
                return True
        return False

    #====================================
    #=          隣接を判定する関数         =
    #====================================
    # 引数 -> 対象ルール
    # 返り値 -> True or False
    # *隣接 -> ビット列のどこか1つだけがそれぞれ0と1を示し,他が同じビット列を示していて,評価型が同じ,すなわち結合可能なことを表す
    def is_adjacent(self,rule):
        assert len(self.bit_string) == len(rule.bit_string),"入力されたルールのbit列の長さが異なります."
        if self.evaluate == rule.evaluate:
            flag = False
            for i in range(len(self.bit_string)):
                if flag == False:
                    if self.bit_string[i] == "0" and rule.bit_string[i] == "1":
                        flag = True
                    elif self.bit_string[i] == "1" and rule.bit_string[i] == "0":
                        flag = True
                    elif self.bit_string[i] != rule.bit_string[i]:
                        return False
                else:
                    if self.bit_string[i] != rule.bit_string[i]:
                        return False
            if flag == True:
                return True
        return False

    #====================================
    #= ルールに合致するパケットを列挙する関数 =
    #==================================== (計算量2^xにつき非推奨)
    # 引数 -> 対象ルール bit_string
    #     -> 参照開始する箇所 ref_position
    # 返り値 -> 合致するパケットのリスト
    def match_packet_list(self,bit_string,ref_position):
        ret = []
        for i in range(ref_position,len(bit_string)):
            if bit_string[i] == "*":
                zero = list(bit_string)
                zero[i] = "0"
                ret_zero = self.match_packet_list("".join(zero),i)
                one = list(bit_string)
                one[i] = "1"
                ret_one = self.match_packet_list("".join(one),i)
                return ret_zero + ret_one
        ret.append(bit_string)
        return ret

    #====================================
    #= 重複するパケット集合を表すbit列を出力  =
    #====================================
    # 引数 -> 対象ルール rule
    # 返り値 -> 合致するパケットを表すbit列
    def match_packet_bit_string(self,rule):
        ret = ""
        for i in range(len(self.bit_string)):
            #両方のbitがマスクならそのまま足す
            if self.bit_string[i] == "*" and self.bit_string[i] == rule.bit_string[i]:
                ret += "*"
            #片方のbitだけがマスクならもう片方のbitを足す
            elif self.bit_string[i] == "*":
                ret += rule.bit_string[i]
            elif rule.bit_string[i] == "*":
                ret += self.bit_string[i]
            else: #両方共マスクじゃないなら,bitが異なることはない(異なるものがあると重複関係ではない)のでbitを足す
                ret += self.bit_string[i]
        return ret

    #====================================
    #=             長さ出力              =
    #====================================
    def __len__(self):
        return len(self.bit_string)

    #====================================
    #=             要素出力              =
    #====================================
    def __getitem__(self,key):
        return self.bit_string[key]

# ------------------------------------------------------------------
# -----                      ルールリスト                       -----
# ------------------------------------------------------------------
#              (並べ替えを主に扱う)
class RuleList:
    #====================================
    #=              初期化               =
    #====================================
    # rulelist -> ルールリスト
    # is_print_match_packet -> __str__で使用
    def __init__(self,is_print_match_packet=False):
        self.rule_list = []
        self.is_print_match_packet=is_print_match_packet

    #====================================
    #=        ルールを末尾へ追加         =
    #====================================
    #ルールを追加する関数
    # 引数 -> ルール
    def append(self, rule):
        self.rule_list.append(rule)

    #====================================
    #=       各ルールの重みを計算        =
    #====================================
    def compute_weight(self,packet_list):

        for i in self.rule_list:
            i._weight = 0

        for i in range(len(packet_list)):
            for j in range(len(self.rule_list)):
                if self.rule_list[j].match(packet_list[i]):
                    self.rule_list[j]._weight += 1
                    break

    #====================================
    #=         パケット分類を行う        =
    #====================================
    # is_print_detail -> 合致パケットの分布、デフォルトルール合致数、分類進捗を出力する
    # 返り値 -> 遅延の合計値
    def filter(self,packet_list,is_print_detail=False):
        #遅延の合計値
        delay_all = 0
        match_number = []
        match_default_rule_num = 0
        #誤爆率を算出するためのリスト
        match_list = []
        for i in range(len(self.rule_list)):
            match_number.append(0)

        #print文用の区切り値
        lap = 10**(len(str(len(packet_list))) - 1)

        #パケットの数だけループ
        for i in range(len(packet_list)):

            # lapの値で区切って経過出力
            if is_print_detail:
                if i % lap == 0:
                    print("%d / %d is filtered."% (i,len(packet_list)))

            #遅延
            delay = 0
            match_position = -1
            #ルールリストの先頭から
            for j in range(len(self.rule_list)):
                delay += 1
                #ルールに合致したら抜ける
                if self.rule_list[j].match(packet_list[i]):
                    match_position = j
                    break
            if match_position != -1: #どこかに合致した場合
                match_number[j] += 1
                match_list.append(self[match_position].evaluate)
            else: #どこにも合致しなかった場合
                match_list.append("Deny")
                match_default_rule_num += 1
            delay_all += delay
        if is_print_detail:
            print("合致パケットの分布:",match_number)
            print("デフォルトルール合致数:",match_default_rule_num)

        return (delay_all,match_list)

    #====================================
    #=        ルールの位置を移動         =
    #====================================
    # 引数 -> rule_pos 移動させるルールの添字番号
    #     -> destination 移動先の添字番号
    # 返り値 -> 成功したかどうか (True or False)
    # destinationにあるルールを押し下げ，その位置にルールを配置する．従属関係を保つことが前提．
    def action_move(self,rule_pos,destination):
        x = self.rule_list[rule_pos]

        for i in range(destination,rule_pos):
            #print("%d %d"%(destination,i))
            if self.rule_list[rule_pos].is_dependent(self.rule_list[i]):
                #print("従属関係が破壊されました")
                return False


        del self.rule_list[rule_pos]

        if rule_pos < destination:
            self.rule_list.insert(destination-1,x)
        else:
            self.rule_list.insert(destination,x)
        return True

    #====================================
    #=             長さ出力              =
    #====================================
    def __len__(self):
        return len(self.rule_list)

    #====================================
    #=             要素取得              =
    #====================================
    def __getitem__(self,key):
        return self.rule_list[key]

    #====================================
    #=       ルールリストのprint処理       =
    #====================================
    # is_print_match_packet -> 各ルールに合致するパケットのリストを出力するか(非推奨)
    def __str__(self):
        print("[ ][ ]ルールリスト[ ][ ]")
        for i in range(len(self.rule_list)):
            if self.rule_list[i].evaluate == "Accept":
                print("[%d] P %s" % (i+1,self.rule_list[i].bit_string))
            elif self.rule_list[i].evaluate == "Deny":
                print("[%d] D %s" % (i+1,self.rule_list[i].bit_string))

        print("[ ] Default Rule [ ]\n")
        for i in reversed(range(len(self.rule_list))):
            if self.is_print_match_packet:
                print("ルール[%d]に合致するパケット ->" % i , self.rule_list[i].match_packet_list(self.rule_list[i].bit_string,0))
            for j in reversed(range(0,i)):

                if self.rule_list[j].is_overlap(self.rule_list[i]):
                    #print(self.rule_list[i].match_packet_bit_string(self.rule_list[j]))
                    if self.rule_list[j].is_dependent(self.rule_list[i]):
                        if self.rule_list[j].is_cover(self.rule_list[i]):
                            print("ルール[%d]とルール[%d]は従属かつ被覆関係" % (i , j))
                        else:
                            print("ルール[%d]とルール[%d]は従属関係" % (i+1 , j+1))
                    elif self.rule_list[j].is_cover(self.rule_list[i]):
                        print("ルール[%d]とルール[%d]は被覆関係" % (i+1 , j+1))
                    else:
                        print("ルール[%d]とルール[%d]は重複関係" % (i+1 , j+1))
        return ""



    def deoverlap(self,rule1_pos,rule2_pos,target_list,overlap_rule_list):
        #重複しているパケットを構築
        overlap_bit_string = target_list[rule2_pos].match_packet_bit_string(overlap_rule_list[rule1_pos])
        cutted_rule_list = []
        evaluating_rule = target_list[rule2_pos].bit_string
        #print("EVALUATE_RULE IS [%s]" % evaluating_rule)
        #print("OVERLAP RULE IS [%s]" % overlap_bit_string)
        start = 0
        end = False
        no_mask = True
        ret = ""
        #分割したルールリストを作れるまでループ(ループ回数はビットマスクの数に等しいはず)
        while not end:
            previous_mask_pos = -1
            #print("EVAL RULE IS %s" % evaluating_rule)
            for i in range(start,len(overlap_rule_list[rule1_pos].bit_string)):
                #bitが異なる場合(重複パケット集合との比較なので，マスクと0 or 1になるはず)
                #print(overlap_bit_string + "\t" + evaluating_rule + "\t" + ret)
                if overlap_bit_string[i] != evaluating_rule[i]:
                    #1つ目のマスクの場合
                    if previous_mask_pos == -1:
                        if no_mask:
                            no_mask = False
                        previous_mask_pos = i
                        ret += "@"
                    else: #2つ目のマスクがあった場合
                        #1つ目のマスクがあった場所のbitを重複パケットと異なるものにする
                        if overlap_bit_string[previous_mask_pos] == "0":
                            ret = ret[:(self.bind(previous_mask_pos,len(overlap_bit_string)))] + "1" + ret[(self.bind(previous_mask_pos+1,len(overlap_bit_string))):]
                        else:
                            ret = ret[:(self.bind(previous_mask_pos,len(overlap_bit_string)))] + "0" + ret[(self.bind(previous_mask_pos+1,len(overlap_bit_string))):]
                        #残りを分割前ルールからそのまま写す
                        ret += evaluating_rule[i:]
                        #print("ONE \t " + ret)
                        #この状態のルールを分割ルールリストへ追加
                        cutted_rule_list.append(ret)
                        #1つ目のマスクがあった場所のbitを重複パケットと同じものにする
                        if overlap_bit_string[previous_mask_pos] == "0":
                            ret = ret[:(self.bind(previous_mask_pos,len(overlap_bit_string)))] + "0" + ret[(self.bind(previous_mask_pos+1,len(overlap_bit_string))):]
                        else:
                            ret = ret[:(self.bind(previous_mask_pos,len(overlap_bit_string)))] + "1" + ret[(self.bind(previous_mask_pos+1,len(overlap_bit_string))):]
                        #評価ルールを更新
                        #print("TWO \t" + ret)
                        evaluating_rule = ret
                        #2つ目のマスクを次の比較開始地点とする
                        start = i

                        ret = ret[:i]
                        #print("START IS %d" % i)
                        #forループを抜ける
                        break
                else: #bit列が同じ場合はそのまま写す
                    ret += overlap_bit_string[i]
                    #print("ADDED %s" % ret)
            else: #forループが正常終了したならwhileループを終える処理に入る
                end = True
            #print(cutted_rule_list)

            #forを正常に抜ける場合 -> マスクが1つしかないルールを評価していて終端に達した or マスクの無いルール -> 重みが0のルール
            #前者の場合1つ目のマスクがあった場所のbitを重複パケットと異なるものにする
            if end:
                if not no_mask:
                    #print("END OF LOOP %d" % previous_mask_pos)

                    #print(overlap_bit_string + "\t" + evaluating_rule + "\t" + ret)
                    if overlap_bit_string[previous_mask_pos] == "0":
                        ret = ret[:(self.bind(previous_mask_pos,len(overlap_bit_string)))] + "1" + ret[(self.bind(previous_mask_pos+1,len(overlap_bit_string))):]
                    else:
                        ret = ret[:(self.bind(previous_mask_pos,len(overlap_bit_string)))] + "0" + ret[(self.bind(previous_mask_pos+1,len(overlap_bit_string))):]
                    #この状態のルールを分割ルールリストへ追加
                    cutted_rule_list.append(ret)
                    #whileを抜ける
                    break
                #後者の場合は単純に削除できるので分割ルールリストは空のまま

        evaluate = target_list[rule2_pos].evaluate

        del target_list[rule2_pos]
        for x in cutted_rule_list:
            ins_rule = Rule(evaluate,x)
            for j in reversed(range(rule1_pos)):
                if overlap_rule_list[j].is_cover(ins_rule):
                    break
            else:
                target_list.insert(rule2_pos,ins_rule)

        #print(self)

        return target_list

    def bind(self,i,r):
        if i<0:
            #print("0")
            return 0
        elif r<i:
            #print(r)
            return r
        else:
            #print(i)
            return i


    def deoverlap_all(self):
        #逆順に調査
        for i in reversed(range(len(self.rule_list))):
            overlap_rule_list = []
            for j in reversed(range(0,i)):
                #重複していたらリストに追加
                if self[i].is_overlap(self[j]):
                    overlap_rule_list.append(self[j])
            #リストに含まれるルール集合を含まないようなルールを形成
            target_list = []
            target_list.append(self.rule_list[i])
            for j in reversed(range(len(overlap_rule_list))):
                for k in reversed(range(len(target_list))):
                    if target_list[k].is_overlap(overlap_rule_list[j]):
                        target_list = self.deoverlap(j,k,target_list,overlap_rule_list)
                        #print(len(target_list))
                print("*----------*%d/%d*----------[%d]*"%(j,len(overlap_rule_list),len(target_list)))
            #対象の箇所へappend
            evaluate = self.rule_list[i].evaluate
            del self.rule_list[i]
            for x in target_list:
                self.rule_list.insert(i,x)

        print(len(self.rule_list))