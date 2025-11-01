from firebase_admin import credentials
from firebase_admin import db
from flask import Flask
import firebase_admin
import os

app = Flask(__name__)

class MAINDB():
    def __init__(self):
        dbkey = os.path.join(app.root_path, 'firebase-dbkey.json') # 找到 firebase 的 key
        dburl = 'https://timapp-2008-default-rtdb.asia-southeast1.firebasedatabase.app/'
        try:
            cred = credentials.Certificate(dbkey)
            firebase_admin.initialize_app(cred, {'databaseURL': dburl})
        except:
            pass
        self.ref = db.reference()

    def test_add(self):
        achild = self.ref.child('test-data')
        adict = {
            'fruit': 'fruit',
            'vegetable': 'vegetable'
        }
        achild.set(adict)

        dict_fruit = {
            'a': 'apple',
            'b': 'banana'
        }
        achild.child('fruit').set(dict_fruit)

    def test_del(self):
        achild = self.ref.child('test-data')
        achild.set({})

    def moderator_add(self, moderator_id):
        # table
        achild = self.ref.child(f'moderators/{moderator_id}')
        dict_moderator = {
            'function 1': 'on',
            'function 2': 'on',
            'function 3': 'on'
        }
        achild.set(dict_moderator)

    def moderator_del(self, moderator_id):
        achild = self.ref.child(f'moderators/{moderator_id}')
        achild.set({})
    
    def weather_data_add(self, discord_id):
        import bot.modules.weather
        num = "09020"
        data = bot.modules.weather._get_city_weather(num)
        print(data)
        achild = self.ref.child(f'discord_weather/{discord_id}')
        adict = {}
        for i, row in enumerate(data):
            # data[i] <=> row
            adict = {
                'date': row[0],
                'temp1': row[1],
                'temp2': row[2],
                'temp3': row[3],
                'ultraviolet': row[4]
                }         
            data[i] = adict

        achild.set(data)

    def weather_data_read(self, discord_id):
        achild = self.ref.child(f'discord_weather/{discord_id}')
        return achild.get()

"""
[
    {
        'date': '11/01'
        'temp1':?,
        'temp2':?,
        'temp3':?
        'level':? 
    },
    {
        'date': '11/0ㄉ'
        'temp1':?,
        'temp2':?,
        'temp3':?
        'level':? 
    },
]
""" 

if __name__ == '__main__':
    # object(物件) vs. class(類別)
    # instance(實體) vs. blueprint(設計藍圖)
    # 實際可用的手機 vs. 手機設計規格書
    # 設計藍圖規格定義所有的組件和操作方法
    # 實際上是使用實體物件操作所以的物件
    # mainDB 變數是指到一個用 MAINDB 產生的實體物件
    # 因此操作物件時要用的是 mainDB
    # 一類多例：用一個版本的手機設計規格書，可以產生許多支實際手機用 MAINDB 類別，
    # 可以產生許多和 mainDB 一樣的物件變數
    mainDB = MAINDB()
    op = input("1.get_weather: ")
    if op == '1':
        mainDB.weather_data_add("123")
    