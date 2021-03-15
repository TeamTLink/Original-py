import sys,requests,configparser,json,os,zipfile

config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(os.path.abspath(__file__)),"config.ini"),encoding="utf-8")

print(type(config["install"]["delete_zip"]))