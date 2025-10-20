import discord
from discord.ext import tasks, commands
from bot.modules import eq_information
from dotenv import load_dotenv
import os
import traceback

# 讀取 .env 檔案
load_dotenv()

TOKEN = os.getenv("EQ_BOT_TOKEN")
CHANNEL_ID = int(os.getenv("EQ_CHANNEL_ID"))

# 設定 Intents
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@tasks.loop(minutes=4)
async def check_earthquake():
    try:
        new_eq = eq_information.get_data()
        previous_eq = eq_information.load_latest()

        if eq_information.compare_data(previous_eq, new_eq):
            eq_information.save_new(new_eq)
            channel = bot.get_channel(CHANNEL_ID)
            if channel:
                embed = discord.Embed(
                    title="🌏 最新有感地震報報",
                    color=0xFF4500  # 震度紅色，可依需求調整
                )

                # 基本資訊欄位
                embed.add_field(name="📅 發生時間",value=(f"  {new_eq['time']}"),inline=False)
                embed.add_field(name="💥 最大震度", value=(f"{new_eq['max_intensity']} 級"),inline=False)
                embed.add_field(name="🌋 深度", value=(f"{new_eq['depth']} 公里"),inline=False)
                embed.add_field(name="📏 規模", value=(f"{new_eq['magnitude']}"),inline=False)
                embed.add_field(name="📍 發生地點", value=(f"{new_eq['location']}"),inline=False)

                # 詳細內容欄位（可加入連結或加粗標記）
                embed.add_field(
                    name="📢 詳細資訊",
                    value=(
                        f"⚠️ **地震警報**\n"
                        f"請民眾注意安全，避免靠近建築物或危險地區。\n"
                        f"更多資訊：[地震即時資訊](https://www.cwb.gov.tw/V8/C/E/EQ.html)"
                    ),
                    inline=False
                )

                # footer (標明來源與時間)
                embed.set_footer(text=f"資料來源｜中央氣象局｜{new_eq['time']}")

                await channel.send(embed=embed)

    except Exception as e:
        print(f"發生錯誤: {e}")
        traceback.print_exc()



@bot.event
async def on_ready():
    print(f"✅ {bot.user} 已上線！")
    check_earthquake.start()

async def run_bot():
    await bot.start(TOKEN)
