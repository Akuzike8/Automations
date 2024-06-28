"""
Firefox Mozilla downloads integration

"""
import sqlite3
import shutil
import json
import os
import socket 
from glob import glob
from Crypto.Hash import SHA256
from datetime import datetime, timedelta

username = os.getlogin()
hostname = socket.gethostname()

profile = glob(f'C:\\Users\\{username}\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\*.default-release')[0]
temp = shutil.copy(f'{profile}\\places.sqlite',f'C:\\Users\\{username}\\AppData\\Local\\Temp\\mozilla_history')
con = sqlite3.connect(f'C:\\Users\\{username}\\AppData\\Local\\Temp\\mozilla_history')
cursor = con.cursor()

cursor.execute("SELECT moz_places.id,guid,title,url,url_hash,moz_origins.host,visit_type FROM moz_places INNER JOIN moz_historyvisits ON moz_places.id=moz_historyvisits.place_id INNER JOIN moz_origins ON origin_id=moz_origins.id WHERE visit_type=7;")
downloads = cursor.fetchall()
cursor.execute("SELECT place_id,anno_attribute_id,content,dateAdded FROM moz_annos;")
target_data = cursor.fetchall()
key = ""

if (os.path.exists(f"{profile}\\mozilla.track")):
    key = open(f"{profile}\\mozilla.track","rb").read().decode()

with open(f"{profile}\\mozilla_history.json","ab+") as file:
    with open(f"{profile}\\mozilla.track","wb+") as track: 
        gen = ""
        start = False
        
        if(key == ""):
            key = downloads[0][1]
            key = SHA256.new(key.encode()).hexdigest()
            track.write(key.encode())
            endtime = json.loads(target_data[1][2])['endTime']
            time = datetime(1601,1,1) + timedelta(microseconds=endtime)
            time = str(time).replace(" ","T") + "Z"
            path = target_data[0][2]
            structure = {"dhost":hostname,"duser":username,"guid":downloads[0][1],"description":"Mozilla FireFox download","path":path,"url":downloads[0][3],"rule":{"level":5,"groups":"downloads"},"time":time,"referrer":downloads[0][5]}
            payload = json.dumps(structure) + "\n"
            payload = payload.encode()
            file.write(payload)
        
        for download in downloads:
            gen = download[1]
            gen = SHA256.new(gen.encode()).hexdigest()

            if(start == True):
                endtime = [json.loads(t[2])['endTime'] for t in target_data if t[0] == download[0] and t[1] == 2][0]
                time = datetime(1601,1,1) + timedelta(microseconds=endtime)
                time = str(time).replace(" ","T") + "Z"
                path = [p[2] for p in target_data if p[0] == download[0] and p[1] == 1][0]
                structure = {"dhost":hostname,"duser":username,"guid":download[1],"description":"Mozilla FireFox download","path":path,"url":download[3],"rule":{"level":5,"groups":"downloads"},"time":time,"referrer":download[5]}
                payload = json.dumps(structure) + "\n"
                payload = payload.encode()
                file.write(payload)
            
            if(key == gen):
                start = True
                
        track.write(gen.encode())
            