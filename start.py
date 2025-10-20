import asyncio
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
import uvicorn

# 修改前提：bot.eq_bot 與 bot.wea_bot 裡的 run_bot 函式要改成非阻塞
# 也就是用 await bot.start(TOKEN) 而非 bot.run(TOKEN)
import bot.eq_bot
import bot.wea_bot

app = FastAPI()

# 個人網站登入頁面
@app.get("/", response_class=HTMLResponse)
async def login_page():
    html_content = """"""
    return html_content

# API 
@app.get("/status")
async def status():
    return {"message": "網站運作中，HelloBot + MathBot 正常啟動"}

# 同時啟動 FastAPI + Discord Bot
async def main():
    config = uvicorn.Config(app, host="0.0.0.0", port=8000)
    server = uvicorn.Server(config)

    # 將 Discord Bot 啟動改成非阻塞任務
    task_eq = asyncio.create_task(bot.eq_bot.run_bot())    # 修改位置：用 create_task 非阻塞
    task_wea = asyncio.create_task(bot.wea_bot.run_bot())  # 修改位置：用 create_task 非阻塞

    # 啟動 FastAPI
    await server.serve()  # FastAPI 先啟動，後面的 bot 會在後台運行

    # 理論上 bot 永遠運作，可以加上 gather 等待
    await asyncio.gather(task_eq, task_wea)

if __name__ == "__main__":
    asyncio.run(main())
