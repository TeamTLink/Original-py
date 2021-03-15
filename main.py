import sys,requests,configparser,json,os,zipfile

version = 0.1

config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(os.path.abspath(__file__)),"config.ini"),encoding="utf-8")

class UpdateError(Exception):
    pass

def update():
    global version,config
    sys.stdout.write("ローカルパッケージリストの読み込み: ")
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),config["path"]["package_list"])) as f:
        pkgl = json.load(f)
    sys.stdout.write("\rローカルパッケージリストの読み込み: 完了\n")
    sys.stdout.write("オンラインパッケージリストの読み込み: ")
    url = f"https://teamtlink.github.io/op-package/{version}/package.json"
    pkgo = requests.get(url)
    if str(pkgo.status_code)[0] != "2":
        raise UpdateError(f"オンラインパッケージリストにアクセスできませんでした。\n{url} にアクセスできる事を確認してください。")
    pkgo = pkgo.json()
    sys.stdout.write("\rオンラインパッケージリストの読み込み: 完了\n\n")
    pkgs = []
    for p in pkgl:
        if pkgl[p]["version"] < pkgo[p]["version"]:
            pkgs.append(pkgo[p])
    if len(pkgs) == 0:
        print("すべてのパッケージが最新バージョンでした。")
        return
    print(f"以下の{len(pkgs)}個のパッケージを更新できます。まとめて更新したくない場合は、[op pkg install パッケージ名]でパッケージを更新してください。\n {' '.join([p['name']+'-v'+str(p['version']) for p in pkgs])}\n")
    ind = input("更新しますか[Y/n]: ")
    if ind not in ["Y","y"]:
        print("\n更新を中止しました。")
        return
    for p in pkgs:
        sys.stdout.write(f"\n{p['name']}-v{p['version']} のインストール: ")
        dataz = requests.get(p["sources"],stream=True)
        sys.stdout.write(f"\r{p['name']}-v{p['version']} のインストール: ダウンロード完了")
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),f"{config['path']['package_folder']}\\{p['name']}.zip"),"wb") as f:
            for d in dataz.iter_content(chunk_size=1024):
                f.write(d)
                f.flush()
        sys.stdout.write(f"\r{p['name']}-v{p['version']} のインストール: zipファイルの書き込み完了")
        with zipfile.ZipFile(os.path.join(os.path.dirname(os.path.abspath(__file__)),f"{config['path']['package_folder']}\\{p['name']}.zip")) as filez:
            filez.extractall(os.path.join(os.path.dirname(os.path.abspath(__file__)),f"{config['path']['package_folder']}\\{p['name']}"))
        sys.stdout.write(f"\r{p['name']}-v{p['version']} のインストール: zipファイルの展開完了    ")
        if config["install"]["delete_zip"] == "true":
            os.remove(os.path.join(os.path.dirname(os.path.abspath(__file__)),f"{config['path']['package_folder']}\\{p['name']}.zip"))
            sys.stdout.write(f"\r{p['name']}-v{p['version']} のインストール: zipファイルの削除完了")
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),config["path"]["package_list"]),"w") as f:
            pkgl[p["name"]] = p
            json.dump(pkgl,f,indent=4)
        sys.stdout.write(f"\r{p['name']}-v{p['version']} のインストール: 完了                \n")
    print("\nすべての更新が完了しました。")

update()
