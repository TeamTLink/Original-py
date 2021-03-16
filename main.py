#######################################################################
#                                                                     #
#            ____       _       _             _ _____                 #
#           / __ \     (_)     (_)           | |  __ \                #
#          | |  | |_ __ _  __ _ _ _ __   __ _| | |__) |   _           #
#          | |  | | '__| |/ _` | | '_ \ / _` | |  ___/ | | |          #
#          | |__| | |  | | (_| | | | | | (_| | | |   | |_| |          #
#           \____/|_|  |_|\__, |_|_| |_|\__,_|_|_|    \__, |          #
#                          __/ |                       __/ |          #
#                         |___/                       |___/           #
#                                                                     #
#######################################################################


#printで文字に色を付ける
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
    end = "\033[39m" #終了
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
    end_all = "\033[0m" #終了


#標準モジュールの読み込み
import configparser,json,os,sys,zipfile


#標準で入っていないモジュール
try:
    import requests
except ModuleNotFoundError as e:
    print(f"{print_color.bg_red}モジュール {str(e)[17:-1]} が入っていません。pip等でインストールしてください。{print_color.end_bg}")
    sys.exit(0)


#config.iniの読み込み
config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(os.path.abspath(__file__)),"config.ini"),encoding="utf-8")
if not os.path.isfile(os.path.join(os.path.dirname(os.path.abspath(__file__)),"config.ini")):
    print(f"{print_color.bg_red}ファイル config.ini が見つかりませんでした。ファイルが {os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'config.ini'))} にあることを確認してください。{print_color.end_bg}")
    sys.exit(0)


#パッケージリストの読み込み(コマンドではない)
def _package_load_():
    sys.stdout.write("ローカルパッケージリストの読み込み: ")
    try:
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),config["path"]["package_list"])) as f:
            pkgl = json.load(f)
    except FileNotFoundError:
        filename = config["path"]["package_list"].split("\\")[-1]
        print(f"{print_color.bg_red}ファイル {filename} が見つかりませんでした。ファイルが {os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),config['path']['package_list']))} にあることを確認してください。{print_color.end_bg}")
        return sys.exit(0)
    sys.stdout.write("\rローカルパッケージリストの読み込み: 完了\n")
    sys.stdout.write("オンラインパッケージリストの読み込み: ")
    url = f"https://teamtlink.github.io/op-package/{version}/package.json"
    pkgo = requests.get(url)
    if str(pkgo.status_code)[0] != "2":
        sys.stdout.write(f"\rオンラインパッケージリストの読み込み: {print_color.bg_red}オンラインパッケージリストを読み込みできませんでした。 {url} にアクセスできる事を確認してください。{print_color.end_all}\n")
        return sys.exit(0)
    pkgo = pkgo.json()
    sys.stdout.write("\rオンラインパッケージリストの読み込み: 完了\n\n")
    return pkgo,pkgl


def install():
    pass


#updateコマンド
def update():
    pkgo,pkgl = _package_load_()
    pkgs = []
    for p in pkgl:
        if pkgl[p]["version"] < pkgo[p]["version"]:
            pkgs.append(pkgo[p])
    if len(pkgs) == 0:
        print("すべてのパッケージが最新バージョンでした。")
        return sys.exit(0)
    print(f"以下の{len(pkgs)}個のパッケージを更新できます。まとめて更新したくない場合は、[op pkg update パッケージ名]でパッケージを更新してください。\n {' '.join([p['name']+'-v'+str(p['version']) for p in pkgs])}\n")
    ind = input("更新しますか[Y/n]: ")
    if ind not in ["Y","y"]:
        print("\n更新を中止しました。")
        return sys.exit(0)
    for p in pkgs:
        sys.stdout.write(f"\n{p['name']}-v{p['version']} のインストール: ")
        dataz = requests.get(p["sources"],stream=True)
        if str(dataz.status_code)[0] != "2":
            sys.stdout.write(f"\r{p['name']}-v{p['version']} のインストール: {print_color.bg_red}ダウンロードできませんでした。 {p['sources']} にアクセスできる事を確認してください。{print_color.end_all}")
            return sys.exit(0)
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
        sys.stdout.write(f"\r{p['name']}-v{p['version']} のインストール: 完了                 \n")
    print("\nすべての更新が完了しました。")


def uninstall():
    pass


def show(arg1=None,arg2=None):
    pkgo,pkgl = _package_load_()
    if arg1 == None:
        #list
        sys.stdout.write("リスト作成中...")
        pkgy = []
        pkgn = []
        for p in pkgo:
            if p in pkgl:
                pkgy.append(f"{p}-v{pkgo[p]['version']}")
            else:
                pkgn.append(f"{p}-v{pkgo[p]['version']}")
        sys.stdout.write(f"\rインストールされているパッケージ:\n {' '.join(pkgy)}\n\nインストールされていないパッケージ:\n {' '.join(pkgn)}\n")
    elif arg1 in ["--search","-S"]:
        #検索
        sys.stdout.write("検索中...")
        pkgy1 = []
        pkgy2 = []
        pkgy3 = []
        pkgn1 = []
        pkgn2 = []
        pkgn3 = []
        for p in pkgo:
            if p in pkgl:
                if arg2 == p:
                    pkgy1.append(f"{p}-v{pkgo[p]['version']}")
                elif arg2 in p:
                    pkgy2.append(f"{p}-v{pkgo[p]['version']}")
                elif arg2 in pkgo[p]["description"]:
                    pkgy3.append(f"{p}-v{pkgo[p]['version']}")
            else:
                if arg2 == p:
                    pkgn1.append(f"{p}-v{pkgo[p]['version']}")
                elif arg2 in p:
                    pkgn2.append(f"{p}-v{pkgo[p]['version']}")
                elif arg2 in pkgo[p]["description"]:
                    pkgn3.append(f"{p}-v{pkgo[p]['version']}")
        sys.stdout.write(f"\rパッケージ名完全一致(インストール済み):\n {' '.join(pkgy1)}\nパッケージ名完全一致(未インストール):\n {' '.join(pkgn1)}\n\nパッケージ名部分一致(インストール済み):\n {' '.join(pkgy2)}\nパッケージ名部分一致(未インストール):\n {' '.join(pkgn2)}\n\nパッケージ説明部分一致(インストール済み):\n {' '.join(pkgy3)}\nパッケージ説明部分一致(未インストール):\n {' '.join(pkgn3)}\n")
    else:
        #表示
        sys.stdout.write("読み込み中...")
        if arg1 in pkgo:
            def molding(data):
                return "\n".join([d+": "+str(data[d]) for d in data])
            if arg1 in pkgl:
                if pkgl[arg1]["version"] != pkgo[arg1]["version"]:
                    sys.stdout.write(f"\rインストールされている {arg1} の詳細:\n{molding(pkgl[arg1])}\n\n最新バージョンの {arg1} の詳細:\n{molding(pkgo[arg1])}\n")
                else:
                    sys.stdout.write(f"\r{arg1} の詳細(インストール済み):\n{molding(pkgl[arg1])}\n")
            else:
                sys.stdout.write(f"\r{arg1} の詳細(未インストール):\n{molding(pkgo[arg1])}\n")
        else:
            sys.stdout.write(f"\r{print_color.bg_red}パッケージ {arg1} が見つかりませんでした。{print_color.end_bg}\n")
            return sys.exit(0)


def _help():
    pass


version = 0.1
update()

