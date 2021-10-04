import math
import time


#  嘘は嘘であると
#  見抜けぬ人でないと
#  (このクラスを使うこと)は難しい
#　　　　＿＿_＿
#　　　／へへ　 ＼
#　　／／⌒⌒＼　 ＼
#　 / /　　　　ヽ　 ヽ
#　｜｜ヽ　／⌒ |　　|
#　 ﾚY-･／　-･- ヽ　 |
#　　| /　　　　 Ｖ) |
#　　|(＿つ　 ･　 丿ノ
#　　|＜三三＞)　/ /
#　　ヽ　ﾞﾞ　　／ﾚｿ
#　　　＼从ww／　｜
#　　　　/)￣　　∧
#　　　／ﾚヽ　 ／ |＼
#　　 ｜|　|　｜⌒ |｜



#***********************************************
#*                  ルールクラス                 *
#***********************************************
class Rule:

    #====================================
    #=              初期化               =
    #====================================
    # evaluate -> 評価値
    # bit_string -> ルールのbit列
    def __init__(self, evaluate, bit_string):
        self.evaluate = evaluate
        self.bit_string = bit_string
        self.count_mask = 0
        #Gymの環境で使うString型のbit列をint配列へ変換した要素の作成(マスクは2とする)
        self.bit_string_num = []
        for i in range(len(bit_string)):
            if bit_string[i] == "*":
                self.bit_string_num.append(2)
            elif bit_string[i] == "0":
                self.bit_string_num.append(0)
            else:
                self.bit_string_num.append(1)
        #重み(フィルタリング時に決定)
        self.weight = 0
        self.match_num = 0

            
            
    #====================================
    #=     合致するかどうか確認する関数      =
    #====================================
    # 引数 -> パケットのbit列 bit_string
    # 返り値 -> True or False
    def match(self,bit_string,renew_weight=False):
        assert len(self.bit_string) == len(bit_string),"入力されたパケットのbit列の長さがルールのbit列と異なります."
        for i in range(len(self.bit_string)):
            if self.bit_string[i] != "*":
                if self.bit_string[i] != bit_string[i]:
                    return False
        if renew_weight:
            self.weight += 1
        self.match_num += 1
        return True

    #====================================
    #=         重複を判定する関数          =
    #====================================
    # 引数 -> 対象ルール
    # 返り値 -> True or False
    def is_overlap(self,rule):
        #print("%s | %s" % (self.bit_string,rule.bit_string))
        assert len(self.bit_string) == len(rule.bit_string),"入力されたルールのbit列の長さが異なります."
        self.count_mask = 0
        for i in range(len(self.bit_string)):
            if self.bit_string[i] != "*" and rule.bit_string[i] != "*":
                if self.bit_string[i] != rule.bit_string[i]:
                    return False
            if self.bit_string[i] != "*" and rule.bit_string[i] == "*":
                self.count_mask += 1
        return True

    #====================================
    #=         被覆を判定する関数          =
    #====================================
    # 引数 -> 対象ルール
    # 返り値 -> True or False
    def is_cover(self,rule):
        #print("%s | %s" % (self.bit_string,rule.bit_string))
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
        #print(bit_string)
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
        #print(self.bit_string + "|" + rule.bit_string)
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
            #print(ret)
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




#***********************************************
#*              ルールリストクラス                *
#***********************************************
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
    #=     ルールを末尾へ追加する関数       =
    #====================================
    #ルールを追加する関数
    # 引数 -> ルール
    def append(self, rule):
        self.rule_list.append(rule)
        
    #====================================
    #=     各ルールの重みを計算する関数      =
    #====================================
    def compute_weight(self,packet_list):
        
        for i in self.rule_list:
            i.weight = 0

        
        #パケットの数だけループ
        for i in range(len(packet_list)):
            #ルールリストの先頭からマッチするか確認
            for j in range(len(self.rule_list)):
                if self.rule_list[j].match(packet_list[i],True):
                    break
        
            
        """
        for i in range(len(packet_list)):
            for j in range(len(self.rule_list)):
                self.rule_list[j].match(packet_list[i])
        """
                
    #====================================
    #=        パケット分類を行う関数        =
    #====================================
    # 返り値 -> 遅延の合計値
    def filter(self,packet_list,is_print_position=False,is_print_detail=False):
        #遅延の合計値
        delay_all = 0
        match_number = []
        match_default_rule_num = 0
        #誤爆率を算出するためのリスト
        match_list = []
        for i in range(len(self.rule_list)):
            match_number.append(0)
        
        #print文用の区切り値
        lap = 10**(len(str(len(packet_list))) - 2)

        for i in self.rule_list:
            i.match_num = 0

        #パケットの数だけループ
        for i in range(len(packet_list)):

            # lapの値で区切って経過出力
            #if i % lap == 0:
            #    print("%d / %d is filtered."% (i,len(packet_list)))
            

            #遅延
            delay = 0
            match_position = -1
            #ルールリストの先頭から
            for j in range(len(self.rule_list)):
                delay += 1
                #ルールに合致したら抜ける
                #print(rule_list[j].bit_string)
                #print(packet_list[i] + "\n")
                if self.rule_list[j].match(packet_list[i]):
                    match_position = j
                    break
                #j += 1
            if match_position != -1: #どこかに合致した場合
                match_number[j] += 1
                if is_print_position:
                    print("%s\tPacket[%d] is matched Rule[%d]. Delay = [%d]" % (self[match_position].evaluate,i,match_position,delay))
                    match_list.append(self[match_position].evaluate)
            else: #どこにも合致しなかった場合
                if is_print_position:
                    print("%s\tPacket[%d] is matched Default rule. Delay = [%d]" % ("Deny",i,delay))
                    match_list.append("Deny")
                match_default_rule_num += 1
            delay_all += delay
        if is_print_detail:
            print("合致パケットの分布:",match_number)
            print("デフォルトルール合致数:",match_default_rule_num)

        return (delay_all,match_list)

    #====================================
    #=           各種アクション           =
    #====================================
    
    # アクション Move
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
            self.rule_list.insert(destination,x)
        else:
            self.rule_list.insert(destination,x)
        return True

    # ******未実装******
    # アクション Split
    # 引数 -> rule_pos 分割するルールの添字番号
    #     -> split_pos 分割するマスク*の位置
    # 返り値 -> 成功したかどうか (True or False)
    # ルールのsplit_pos番目にあるマスクを2つに分け，2つのルールにする．
    def action_split(self,rule_pos,split_pos):
        return False

    # ******未実装******
    # アクション Join
    # 引数 -> rule_pos 結合するルール1つ目の添字番号
    # 返り値 -> 成功したかどうか (True or False)
    # rule_posとその一つ下のルールの内，結合可能なビットをマスクにしたルールを追加し，参照した2つのルールを削除する．
    def action_join(self,rule_pos):
        return False

    # ******未実装******
    # アクション Delete
    # 引数 -> rule_pos 削除するルールの添字番号
    # 返り値 -> 成功したかどうか (True or False)
    # 特定の条件に従うルールを削除する．従属関係を保つことが前提．
    def action_delete(self,rule_pos,split_pos):
        return False

    # ******未実装******
    # アクション Replace
    # 引数 -> rule_pos 置換するルール1つ目の添字番号
    #      -> length 部分リストの長さ(2以上)
    # 返り値 -> 成功したかどうか (True or False)
    # 部分リストをポリシを保つような別の部分リストへ置き換える．できるかこんなん？
    def action_replace(self,rule_pos,length):
        return False

    # 従属関係を除去する関数
    # 引数 -> rule1_pos rule2_pos ルールの添字番号(1は上位ルール,2は下位ルール) 
    # 返り値 -> なし
    # 重複／従属関係を除去する，
    # 重複パケットを表示 -> 下位ルールの重複部分を削除
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
    
    #====================================
    #=   一様分布の場合の遅延を計算する関数   =（未実装）
    #====================================
    def compute_delay_average(self):
        return        
    
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
                print("[%5d]<%6d> P %s" % (i,self.rule_list[i].match_num,self.rule_list[i].bit_string))
            elif self.rule_list[i].evaluate == "Deny":
                print("[%5d]<%6d> D %s" % (i,self.rule_list[i].match_num,self.rule_list[i].bit_string))

        print("[ ] Default Rule [ ]\n")
        overlap_score = 0
        super_score = 0
        for i in reversed(range(len(self.rule_list))):
            if self.is_print_match_packet:
                print("ルール[%d]に合致するパケット ->" % i , self.rule_list[i].match_packet_list(self.rule_list[i].bit_string,0))
            for j in reversed(range(0,i-1)):
                
                if self.rule_list[j].is_overlap(self.rule_list[i]):
                    count_mask = self.rule_list[j].count_mask
                    super_score += count_mask
                    overlap_score += 1
                    #print(self.rule_list[i].match_packet_bit_string(self.rule_list[j]))
                    if self.rule_list[j].is_dependent(self.rule_list[i]):
                        if self.rule_list[j].is_cover(self.rule_list[i]):
                            print("ルール[%d]とルール[%d]は従属かつ被覆関係\t%d" % (i , j,count_mask))
                        else:
                            print("ルール[%d]とルール[%d]は従属関係\t%d" % (i , j,count_mask))
                    elif self.rule_list[j].is_cover(self.rule_list[i]):
                        print("ルール[%d]とルール[%d]は被覆関係" % (i , j))
                    else:
                        print("ルール[%d]とルール[%d]は重複関係\t%d" % (i , j,count_mask))
        if overlap_score != 0:
            print("OVERLAP_SCORE = %d" % overlap_score)
            print("SUPER_SCORE = %d" % super_score)
            print("MEAN = %s" % (super_score / overlap_score))
        return ""

    #====================================
    #=       重複関係を全除去する関数       =
    #====================================

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
            #for i in target_list:
            #    print(i.bit_string + "\t" + i.evaluate)
            #print("------------------------------------------------------------------------------------------------------------------------------------------")

            print("*===============================================================*\t%d\t/\t%d*==============================================================*"%(i,len(self.rule_list)))
            #対象の箇所へappend
            evaluate = self.rule_list[i].evaluate
            del self.rule_list[i]
            for x in target_list:
                self.rule_list.insert(i,x)


    #====================================
    #= 移動可能なルール位置のリストを返す関数 =
    #====================================
    def movable_list(self,rule_num):
        movable_nums = []

        for i in reversed(range(0,rule_num)):
            if self.rule_list[rule_num].is_dependent(self.rule_list[i]):
                break
            movable_nums.append(i)
        
        rule_num_index = len(movable_nums)
        for i in range(rule_num + 1,len(self.rule_list)):
            if self.rule_list[rule_num].is_dependent(self.rule_list[i]):
                break
            movable_nums.append(i)


        return (movable_nums,rule_num_index)
    
    #====================================
    #= 遅延の減少が期待される位置のリストを返す =
    #====================================
    def expected_decline_list(self,rule_num):
        expected_decline_nums = []
        movable_list = self.movable_list(rule_num)
        movable_nums = movable_list[0]
        #print(movable_nums[movable_list[1]])
        #print("MOVEABLE_LIST ",end="")
        #print(movable_list)
        for i in range(movable_list[1]):
            #print("%d %d"%(movable_nums[i],rule_num))
            if self.rule_list[rule_num].match_num > self.rule_list[movable_nums[i]].match_num:
                expected_decline_nums.append(movable_nums[i])
            else:
                break
        
        for i in range(movable_list[1],len(movable_nums)):
            #print("%d %d"%(movable_nums[i],rule_num))

            if self.rule_list[rule_num].match_num < self.rule_list[movable_nums[i]].match_num:
                expected_decline_nums.append(movable_nums[i])
            else:
                break
           
        return expected_decline_nums

    #======================================
    #= 遅延の減少が期待されるsourceの一覧を返す =
    #======================================
    def expected_decline_src(self):
        expected_dec_src_list = []
        for i in range(len(self.rule_list)):
            if len(self.expected_decline_list(i)) > 0:
                #print("%d |"%(i),end="")
                #print(self.expected_decline_list(i))
                expected_dec_src_list.append(i)

        return expected_dec_src_list
