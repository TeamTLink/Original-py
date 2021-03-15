import sys,requests,configparser,json,os,zipfile

version = 0.1

config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(os.path.abspath(__file__)),"config.ini"),encoding="utf-8")

class print_color:
    ### 文字 ###
    black = "\033[30m" #黒
    red = "\033[31m" #赤
    green = "\033[32m" #緑
    yellow = "\033[33m" #黄
    blue = "\033[34m" #青
    purple = "\033[35m" #紫
    cyan = "\033[36m" #シアン
    white = "\033[37m" #白
    bold = "\033[1m" #太字
    underline = "\033[4m" #下線
    flash = "\033[5m" #点滅
    invisible = "\033[8m" #不可視
    end_color = "\033[39m" #終了
    ### 背景 ###
    bg_black = "\033[40m" #黒
    bg_red = "\033[41m" #赤
    bg_green = "\033[42m" #緑
    bg_yellow = "\033[43m" #黄
    bg_blue = "\033[44m" #青
    bg_magenta = "\033[45m" #マゼンタ
    bg_cyan = "\033[46m" #シアン
    bg_white = "\033[47m" #白
    end_bg = "\033[49m" #終了
    ### 文字&背景 ###
    reverce = "\033[7m" #文字色と背景色を反転
    red_flash = "\033[5;41m" #赤背景+点滅
    end = "\033[0m" #終了

def package_list_load():
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
    return pkgo,pkgl


def show():
    global version,config
    

class UpdateError(Exception):
    pass

def update():
    global version,config
    pkgo,pkgl = package_list_load()
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
