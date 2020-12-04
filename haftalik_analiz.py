import pandas as pd
import matplotlib.pyplot as plt
import pymysql as MySQLdb
import numpy as np
from datetime import datetime, timedelta
import locale
from PIL import Image
import os
from instabot import Bot
import time

db = MySQLdb.connect("ip","user","password","db_names" )
cursor = db.cursor()

try:
    bot = Bot()
    bot.login(username="",password="")
except:
    pass

dun = datetime.today() - timedelta(days=1)
gun_ad = dun.strftime("%A")
dun = dun.strftime("%Y-%m-%d")
print(dun)

gunler_list=[]
gunler_ad=[]
for i in range(1,8):
    gun= datetime.today() - timedelta(days=i)
    gun_ad = gun.strftime("%A")
    gun = gun.strftime("%Y-%m-%d")
    
    if gun_ad=="Monday":
        gunler_ad.append("Pazartesi")
    elif gun_ad=="Tuesday":
        gunler_ad.append("Salı")
    elif gun_ad=="Wednesday":
        gunler_ad.append("Çarşamba")
    elif gun_ad=="Thursday":
        gunler_ad.append("Perşembe")
    elif gun_ad=="Friday":
        gunler_ad.append("Cuma")
    elif gun_ad=="Saturday":
        gunler_ad.append("Cumartesi")
    elif gun_ad=="Sunday":
        gunler_ad.append("Pazar")

    gunler_list.append(gun)

gunler_list.reverse() #Listeyi ters çevirir
gunler_ad.reverse()
print(gunler_list)

query="Select * from kanal"
df = pd.read_sql(query, con=db)

kanalID_list = df["ID"].unique()
kanalad_list = df["ad"].unique()
kanaltag_list = df["tag"]
kanaltaglar=[]
for j in kanaltag_list:
    kanaltaglar.append(j)
kanaluser_list = df["user_id"].unique()

def watermark_photo(input_image_path,
                    output_image_path,
                    watermark_image_path,
                    position):
        base_image = Image.open(input_image_path)
        watermark = Image.open(watermark_image_path)
        base_image.paste(watermark, position)
        base_image.save(output_image_path)

sayac=0
fotolar=[]
users_to_tag=[]
for kanalID in kanalID_list:

    kanalad = kanalad_list[sayac]
    kanaltag= kanaltag_list[sayac]
    
    try:
        kanaluser = kanaluser_list[sayac]
        x = 0.1
        y = 0.1
        
        if len(kanaluser.split(","))!=1:
            user = kanaluser.split(",")
            for j in user:
                print(j)
                s = {'user_id': j, 'x': x, 'y': y}
                users_to_tag.append(s)
                x += 0.3
                if x==1.0:
                    y += 0.4
                    x = 0.1
        else:
            s = {'user_id': kanaluser, 'x': x, 'y': y}
            users_to_tag.append(s) 
    except:
        pass


    goruntulenme=[]
    goruntulenme_ortalama=[]
    for gun in gunler_list:
        query=f"Select * from gunluk where kanal_ID='{kanalID}' and tarih = '{gun}'"
        df = pd.read_sql(query, con=db)
        goruntulenme_gun = df["goruntulenme"].sum()
        print(goruntulenme_gun)
        goruntulenme.append(goruntulenme_gun)

    
    goruntulenme_son=[]
    for i in goruntulenme:
        a = i / 1000000
        goruntulenme_son.append(a)

    for i in goruntulenme:
        goruntulenme_ortalama.append(sum(goruntulenme_son)/len(goruntulenme_son))

    plt.style.use("dark_background")
    for param in ['text.color', 'axes.labelcolor', 'xtick.color', 'ytick.color']:
        plt.rcParams[param] = '0.9'  # very light grey
    for param in ['figure.facecolor', 'axes.facecolor', 'savefig.facecolor']:
        plt.rcParams[param] = '#212946'  # bluish dark grey
    colors = [
        '#08F7FE',  # teal/cyan
        '#FE53BB',  # pink
        '#F5D300',  # yellow
        '#00ff41',  # matrix green
    ]
    df = pd.DataFrame({'goruntulenme': goruntulenme_son, 'Ortalama': goruntulenme_ortalama}, 
                   index=gunler_ad
                   )
    fig, ax = plt.subplots()

    df.plot(marker='o', color=colors, ax=ax,fontsize=22) 
    n_shades = 10
    diff_linewidth = 1.05
    alpha_value = 0.3 / n_shades
    for n in range(1, n_shades+1):
        df.plot(marker='o',
                linewidth=2+(diff_linewidth*n),
                alpha=alpha_value,
                legend=False,
                ax=ax,
                color=colors)
    # Color the areas below the lines:
    for column, color in zip(df, colors):
        ax.fill_between(x=df.index,
                        y1=df[column].values,
                        y2=[0] * len(df),
                        color=color,
                        alpha=0.1)
    ax.grid(color='#2A3459')
    ax.set_xlim([ax.get_xlim()[0] - 0.2, ax.get_xlim()[1] + 0.2])  # to not have the markers cut off
    ax.set_ylim(0)

    figure = plt.gcf()  # get current figure
    figure.set_size_inches(16, 9) # set figure's size manually to your full screen (32x18)

    plt.ylabel("Goruntulenme (Milyon Cinsinden)",fontsize=20)
    plt.xticks(rotation=20, horizontalalignment="center")
    plt.title(f"{kanalad} \n {gunler_list[0]} - {gunler_list[6]}  Tarihleri Arasında\n Günlük görüntülenme karşılaştırılması",fontsize=25)
    plt.savefig('haftalik.jpg',bbox_inches='tight') 
    caption=f"{kanalad} kanalının son 7 gün içerisinde ki günlük görüntülenme sayıları\nGünlük Ortalama {int(goruntulenme_ortalama[0] * 1000000)} kez görüntülenmişsiniz\n\n{kanaltag}\n\n#youtube #youtubetürkiye #enesbatur #basakkarahan #delimine #reynmen #orkunışıtmak #twitchturkiye #wtcnn #hazretiyasuo #hzyasuo #evonmoss #twitch #kafalar #alibicim #mesutcantomay #babala #oguzhanugur #magazin #youtubemagazin" 

    img = '/home/yonetici/verianaliz/arkaplan.jpg'
    watermark_photo(img, f'{sayac}.jpg',
                        'haftalik.jpg', position=(175,50))
    
    fotolar.append(f"{sayac}.jpg")
    
    
    sayac += 1
    if(sayac==7):
        bot.upload_album(fotolar,user_tags= users_to_tag,caption=f"Kanalların son 7 gün içerisinde ki günlük görüntülenme sayıları\n\n{kanaltaglar}\n\n#youtube #youtubetürkiye #enesbatur #basakkarahan #delimine #reynmen #orkunışıtmak #twitchturkiye #wtcnn #hazretiyasuo #hzyasuo #evonmoss #twitch #kafalar #alibicim #mesutcantomay #babala #oguzhanugur #magazin #youtubemagazin")
        fotolar=[]
        users_to_tag=[]
    plt.close()

bot.upload_album(fotolar,user_tags= users_to_tag,caption=f"Kanalların son 7 gün içerisinde ki günlük görüntülenme sayıları\n\n{kanaltaglar}\n\n#youtube #youtubetürkiye #enesbatur #basakkarahan #delimine #reynmen #orkunışıtmak #twitchturkiye #wtcnn #hazretiyasuo #hzyasuo #evonmoss #twitch #kafalar #alibicim #mesutcantomay #babala #oguzhanugur #magazin #youtubemagazin")
os.remove("0.jpg.REMOVE_ME")
os.remove("1.jpg.REMOVE_ME")
os.remove("2.jpg.REMOVE_ME")
os.remove("3.jpg.REMOVE_ME")
os.remove("4.jpg.REMOVE_ME")
os.remove("5.jpg.REMOVE_ME")
os.remove("6.jpg.REMOVE_ME")
os.remove("7.jpg.REMOVE_ME")
os.remove("8.jpg.REMOVE_ME")
os.remove("9.jpg.REMOVE_ME")
os.remove("10.jpg.REMOVE_ME")
os.remove("11.jpg.REMOVE_ME")
os.remove("12.jpg.REMOVE_ME")
os.remove("13.jpg.REMOVE_ME")
