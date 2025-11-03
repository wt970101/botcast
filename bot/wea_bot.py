import discord
from discord.ext import tasks, commands
from bot.modules import weather
from dotenv import load_dotenv
import os
import traceback
import amaindb

# 讀取 .env 檔案
load_dotenv()

TOKEN = os.getenv("WEA_BOT_TOKEN")
CHANNEL_ID = int(os.getenv("WEA_CHANNEL_ID"))

# 設定 Intents
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="？", intents=intents)

citys = {"基隆市": "10017", "新北市": "65", "台北市": "63", "桃園市": "68", "新竹市": "10018", "新竹縣": "10004", "苗栗縣": "10005", "台中市": "66",
        "彰化縣": "10007", "南投縣": "10008", "雲林縣": "10009", "嘉義市": "10020", "嘉義縣": "10010", "台南市": "67", "高雄市": "64", "屏東縣": "10013",
        "宜蘭縣": "10002", "花蓮縣": "10015", "台東縣": "10014", "澎湖縣": "10016", "連江縣": "09020", "金門縣": "09007"}

class WeatherComboView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(WeatherSelect())
        self.add_item(WeatherButton())
        self.city_code = None
        self.city_name = None
        self.user_id = None

    def set_user_id(self, user_id):
        self.user_id = user_id
    
    def get_user_id(self):
        return self.user_id
    
    def set_city_code(self, city_code):
        self.city_code = city_code

    def get_city_code(self):
        return self.city_code
    
    def set_city_name(self, city_name):
        self.city_name = city_name

    def get_city_name(self):
        return self.city_name

class WeatherSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label=ci) for ci in citys
        ]
        super().__init__(placeholder="選擇要查詢的縣市", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)  # 告訴 Discord：我正在處理，否則三秒過後會交互失敗
        # await interaction.response.send_message(f"已選擇 {self.values[0]}，按下查詢按鈕並稍等片刻後即可獲得資訊", ephemeral=True)
        view: WeatherComboView = self.view # 傳入以前的 view
        city_name = self.values[0]
        view.set_city_name(city_name)
        code = citys[city_name]
        view.set_city_code(code)

class WeatherButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.primary, label="查詢最新天氣 🌦️")
    
    async def callback(self, interaction: discord.Interaction):
        view: WeatherComboView = self.view
        select: WeatherSelect = view.children[0]

        if not select.values:
            await interaction.response.send_message("請先選擇城市！", ephemeral=True)
            return
        await interaction.response.send_message("載入中...", ephemeral=True)

        try:
            user_id = view.get_user_id()
            code = view.get_city_code()
            city_name = view.get_city_name()

            mainDB = amaindb.MAINDB()
            mainDB.weather_data_add(user_id ,code) # 上傳 firebase
            print("完成動作")

            massage = f"點擊 [連結](http://localhost:8000/weather_report/{user_id}) 查看 {city_name} 未來一周天氣預報"
            sent_message = await interaction.original_response()
            await sent_message.edit(content=massage)
            print("結束工作")

        except Exception as e:
            await interaction.followup.send(f"❌ 查詢失敗：{e}", ephemeral=True)






# 執行機器人 定時查詢
@tasks.loop(minutes=4)
async def check_weather():
    try:
        link = await weather.get_url()
        new_wea = await weather.get_data(link)
        previous_wea = weather.load_latest()

        if weather.compare_data(previous_wea, new_wea) == True:
            weather.save_new(new_wea)  # 更新資料
            channel = bot.get_channel(CHANNEL_ID)
            if channel:
                embed = discord.Embed(
                    title=f"🌏 最新 {new_wea['title']}",
                    color=0x1E90FF  # 天藍色，可自行調整
                )

                # 自動拆段落成欄位
                content = new_wea['content']

                # 先用換行或句號拆段落
                paragraphs = []
                for p in content.replace("。", "。\n").split("\n"):
                    paragraphs.append(p.strip())

                # 移除空字串 & 去掉開頭數字
                for i in range(len(paragraphs)):
                    if not paragraphs[i].strip():
                        continue
                    if paragraphs[i][0] in ["一","二","三","四","五","六","七","八","九","十"] and paragraphs[i][1] in ["、","．"]:
                        paragraphs[i] = paragraphs[i][2:]

                    
                    if i == 0:
                        embed.add_field(name="📌 概述", value=paragraphs[0], inline=False)

                    else:
                        if "【" in paragraphs[i] and "】" in paragraphs[i]:
                            title = paragraphs[i].split("【")[1].split("】")[0]
                            content = paragraphs[i].split("】")[1]
                            if content == "。":
                                content = "無"
                        elif "燈" in paragraphs[i] and "號" in paragraphs[i]:
                            for p in range(len(paragraphs[i])-1):
                                if paragraphs[i][p] == "燈" and paragraphs[i][p+1] == "號":
                                    break
                            p = p + 1
                            title = paragraphs[i][p-3:p+1]
                        elif "：" in paragraphs[i]:
                            title, content = paragraphs[i].split("：",1)
                        else:
                            title = ""
                            content = f"{paragraphs[i]}"
                        embed.add_field(name=title, value=content, inline=False)

                # footer 可加來源或更新時間
                embed.set_footer(text=f"資料來源｜氣象局｜{new_wea['time']}")

                await channel.send(embed=embed)

    except Exception as e:
        print(f"發生錯誤: {e}")
        traceback.print_exc() # 錯誤時自動跳過不引響操作

@bot.event
async def on_ready():
    print(f"✅ {bot.user} 已上線！")
    check_weather.start()


@bot.command()
async def cityweather(ctx):
    user_id = ctx.author.id
    view = WeatherComboView() # 下拉式選單並用按鈕查詢
    view.set_user_id(user_id)
    print("userid2", user_id)
    await ctx.send("請選擇縣市或直接查詢最新天氣 🌦️", view=view)
    
async def run_bot():
    await bot.start(TOKEN)

if __name__ == "__main__":
    import asyncio
    asyncio.run(run_bot())
