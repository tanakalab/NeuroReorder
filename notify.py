# 実行完了時にラインに通知する処理

#参考にしたサイト
#https://qiita.com/AoyaHashizu/items/13848b013daa18f6461b

# ------------------------------------------------------------------
# -----                      ライブラリ定義                     -----
# ------------------------------------------------------------------
# 基本ライブラリ
import requests
import argparse


parser = argparse.ArgumentParser()


parser.add_argument(
    "--experiment_title",
    type=str,
    default="EXPERIMENT",
    help="実験名.")


def main():
    args = parser.parse_args()


    with open("notify_token",mode="r") as raw_tokenfile:
        token = raw_tokenfile.read()



    url = "https://notify-api.line.me/api/notify"
    headers = {"Authorization": f'Bearer {token}'}

    message = "実験[" + args.experiment_title + "]が終了しました。"

    data = {'message' : message}
    r = requests.post(url,headers=headers,data=data)

if __name__ == '__main__':
    main()
