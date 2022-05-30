import argparse
import random
parser = argparse.ArgumentParser()



parser.add_argument(
    "rule_file",
    type=str,
    help="読み込むルールファイルのパス."
)

parser.add_argument(
    "accept_percentage",
    type=int,
    help="許可の割合.0~100で指定."
)

if __name__ == "__main__":
    
    args = parser.parse_args()

    #ファイルオープン
    with open(args.rule_file,mode="r") as rulelist_file:
        with open("assigned_"+args.rule_file,"w",encoding="utf-8",newline="\n") as write_file:
            while rulelist_file:
                rule = "".join(rulelist_file.readline().split())
                print(rule)
                if not rule:
                    break
                if random.randrange(100) <= args.accept_percentage:
                    write_file.write("Accept\t"+rule+"\n")
                else:
                    write_file.write("Deny\t"+rule+"\n")

