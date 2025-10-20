import discord
from discord.ext import tasks, commands
from bot.modules import weather
from dotenv import load_dotenv
import os
import traceback

# 讀取 .env 檔案
load_dotenv()

TOKEN = os.getenv("WEA_BOT_TOKEN")
CHANNEL_ID = int(os.getenv("WEA_CHANNEL_ID"))

# 設定 Intents
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="？", intents=intents)

@tasks.loop(minutes=4)
async def check_weather():
    try:
        link = weather.get_url()
        new_wea = weather.get_data(link)
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
                            for p in range(len(paragraphs[i])):
                                if paragraphs[i][p] == "燈" and paragraphs[p+1] == "號":
                                    break
                            p = p + 1
                            title = paragraphs[i][p-3:p+1]
                        elif "：" in paragraphs[i]:
                            title, content = paragraphs[i].split("：",1)
                        else:
                            title = ""
                            content = f"{content}\n {paragraphs[i]}"
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

async def run_bot():
    await bot.start(TOKEN)
