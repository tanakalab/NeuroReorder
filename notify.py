# 実行完了時にラインに通知する処理

#参考にしたサイト
#https://qiita.com/AoyaHashizu/items/13848b013daa18f6461b

# ------------------------------------------------------------------
# -----                      ライブラリ定義                     -----
# ------------------------------------------------------------------
# 基本ライブラリ
import requests
import argparse
import socket


parser = argparse.ArgumentParser()


parser.add_argument(
    "--experiment_title",
    type=str,
    default="EXPERIMENT",
    help="実験名.")
parser.add_argument(
    "--tag",
    type=str,
    default="end",
    help="実験の通知タイミングを表すタグ. start or end,")


def main():
    args = parser.parse_args()

    host_name = socket.gethostname()

    if args.tag == "start":
        tag_msg = "]を開始しました。"
    elif args.tag == "end":
        tag_msg =  "]が終了しました。"

    with open("notify_token",mode="r") as raw_tokenfile:
        token = raw_tokenfile.read()



    url = "https://notify-api.line.me/api/notify"
    headers = {"Authorization": f'Bearer {token}'}
    
    message = "実験機{"+ host_name +"}にて実験[" + args.experiment_title + tag_msg

    data = {'message' : message}
    r = requests.post(url,headers=headers,data=data)

if __name__ == '__main__':
    main()