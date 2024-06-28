"""
Microsoft edge downloads integration

"""
import sqlite3
import shutil
import json
import os
import socket 
from Crypto.Hash import SHA256
from datetime import datetime, timedelta

username = os.getlogin()
hostname = socket.gethostname()

temp = shutil.copy(f'C:\\Users\\{username}\\AppData\\Local\\Microsoft\\Edge\\User Data\\Default\\History',f'C:\\Users\\{username}\\AppData\\Local\\Temp\\edge_history')
con = sqlite3.connect(f'C:\\Users\\{username}\\AppData\\Local\\Temp\\edge_history')
cursor = con.cursor()

cursor.execute("SELECT id,guid,target_path,end_time,mime_type,referrer FROM downloads")
downloads = cursor.fetchall()
cursor.execute("SELECT id,url FROM downloads_url_chains")
download_chain = cursor.fetchall()
key = ""

if (os.path.exists(f"C:\\Users\\{username}\\AppData\\Local\\Microsoft\\Edge\\User Data\\Default\\edge.track")):
    key = open(f"C:\\Users\\{username}\\AppData\\Local\\Microsoft\\Edge\\User Data\\Default\\edge.track","rb").read().decode()

with open(f"C:\\Users\\{username}\\AppData\\Local\\Microsoft\\Edge\\User Data\\Default\\edge_history.json","ab+") as file:
    with open(f"C:\\Users\\{username}\\AppData\\Local\\Microsoft\\Edge\\User Data\\Default\\edge.track","wb+") as track: 
        gen = ""
        start = False

        if(key == ""):
            key = downloads[0][1]
            key = SHA256.new(key.encode()).hexdigest()
            track.write(key.encode())
            time = datetime(1601,1,1) + timedelta(microseconds=downloads[0][3])
            time = str(time).replace(" ","T") + "Z"
            structure = {"dhost":hostname,"duser":username,"guid":downloads[0][1],"description":"Microsoft Edge download","path":downloads[0][2],"rule":{"level":5,"groups":"downloads"},"time":time,"mime_type":downloads[0][4],"referrer":downloads[0][5],"download_chain":[link[1] for link in download_chain if link[0]==downloads[0][0]]}
            payload = json.dumps(structure) + "\n"
            payload = payload.encode()
            file.write(payload)
    
        for download in downloads:
            gen = download[1]
            gen = SHA256.new(gen.encode()).hexdigest()
            
            if(start == True):
                time = datetime(1601,1,1) + timedelta(microseconds=download[3])
                time = str(time).replace(" ","T") + "Z"
                structure = {"dhost":hostname,"duser":username,"guid":download[1],"description":"Microsoft Edge download","path":download[2],"rule":{"level":5,"groups":"downloads"},"time":time,"mime_type":download[4],"referrer":download[5],"download_chain":[link[1] for link in download_chain if link[0]==download[0]]}
                payload = json.dumps(structure) + "\n"
                payload = payload.encode()
                file.write(payload)

            if(key == gen):
                start = True

        track.write(gen.encode())
