import httpx
import asyncio
import time
from telegram import Bot

import config

MINUTES = 60
BOT_TOKEN = config.BOT_TOKEN
DESTINATION_CHAT = config.DESTINATION_CHAT

SINGLE_POST = False
IMAGES = False

async def main():
    async def get_last_threads_from_board(board):
        async with httpx.AsyncClient() as client:
            response = await client.get(f'https://www.diochan.com/{board}/catalog.json')
            response.raise_for_status()
            return response.json()

    diochan = await get_last_threads_from_board('b')
    # print(r)
    now = int(time.time())
    # print(now)
    

    delta_timestamp = 60 * MINUTES
    not_before = now - delta_timestamp
    threads = []
    for page in diochan:
        for thread in page['threads']:
            if thread['time'] > not_before:
                t = {
                    'board': 'b',
                    'thread': thread['no'],
                    'time': thread['time'],
                    'title': thread.get('sub'),
                    'text': thread['com'],
                    'image_url': f"https://www.diochan.com/b/src/{thread['tim']}{thread['ext']}",
                    'thread_url' : f"https://www.diochan.com/b/res/{thread['no']}.html"
                }
                threads.append(t)
    
    # print(threads)
    # print(len(threads))
    bot = Bot(token=config.BOT_TOKEN)
    for thread in threads:
        caption = f"{thread['thread_url']}\n{thread['text']}"
        image_url = thread['image_url']
        await bot.send_message(chat_id=config.ID_DIOCHAN2, text=caption, parse_mode='HTML')
        # await bot.send_photo(chat_id=config.ID_DIOCHAN2, photo=image_url, caption=caption)

if __name__ == '__main__':
    asyncio.run(main())