import sys,json,os
import requests

class UpdateError(Exception):
    pass

def update(ver):
    sys.stdout.write("オンラインパッケージリストの読み込み: ")
    url = f"https://teamtlink.github.io/op-package/{ver}/package.json"
    pkgo = requests.get(url)
    if str(pkgo.status_code)[0] != "2":
        raise UpdateError(f"オンラインパッケージリストにアクセスできませんでした。\n{url} にアクセスできる事を確認してください。")
    else:
        sys.stdout.write("\rオンラインパッケージリストの読み込み: 完了\n")
    pkgo = pkgo.json()
    sys.stdout.write("ローカルパッケージリストの読み込み: ")
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"package.json")) as f:
        pkgl = json.load(f)
    sys.stdout.write("\rローカルパッケージリストの読み込み: 完了\n\n")
    pkgs = []
    for p in pkgl:
        if pkgl[p]["version"] < pkgo[p]["version"]:
            pkgs.append(pkgo[p])
    print(f"以下の{len(pkgs)}個のパッケージを更新できます。まとめて更新したくない場合は、[op pkg install パッケージ名]でパッケージを更新してください。\n {' '.join([p['name']+'-v'+str(p['version']) for p in pkgs])}\n")
    ind = input("更新しますか[Y/n]: ")
    if ind not in ["Y","y"]:
        print("\n更新を中断しました。")
        return
    for p in pkgs:
        dataz = requests.get(p["sources"],stream=True)
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),f"packages\\{p['name']}.zip"),"wb") as f:
            for d in dataz.iter_content(chunk_size=1024):
                f.write(d)
                f.flush()

update(0.1)
