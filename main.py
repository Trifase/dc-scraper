import httpx
import asyncio
import time
from telegram import Bot

import config


BOT_TOKEN = config.BOT_TOKEN
DESTINATION_CHAT = config.DESTINATION_CHAT

MINUTES = config.MINUTES
SINGLE_POST = config.SINGLE_POST
IMAGES = config.IMAGES
BOARDS = config.BOARDS

async def main():
    async def get_last_threads_from_board(board):
        async with httpx.AsyncClient() as client:
            response = await client.get(f'https://www.diochan.com/{board}/catalog.json')
            response.raise_for_status()
            return response.json()

    diochan = {}
    for board in BOARDS:
        diochan[board] = await get_last_threads_from_board(board)
    now = int(time.time())

    delta_timestamp = 60 * MINUTES
    not_before = now - delta_timestamp
    threads = []

    for board in BOARDS:
        for page in diochan[board]:
            for thread in page['threads']:
                if thread['time'] > not_before:
                    print(thread)
                    t = {
                        'board': board,
                        'thread': thread['no'],
                        'time': thread['time'],
                        'title': thread.get('sub'),
                        'text': thread['com'],
                        'image_url': f"https://www.diochan.com/{board}/src/{thread['tim']}{thread['ext']}",
                        'thread_url' : f"https://www.diochan.com/{board}/res/{thread['no']}.html"
                    }
                    threads.append(t)
    

    bot = Bot(token=config.BOT_TOKEN)

    if SINGLE_POST:
        message = ''
        for thread in threads:
            message += f"{thread['thread_url']}\n{thread['text']}\n\n"
        await bot.send_message(chat_id=DESTINATION_CHAT, text=message, parse_mode='HTML')
    
    else:
        for thread in threads:
            caption = f"{thread['thread_url']}\n{thread['text']}"
            image_url = thread['image_url']

            if IMAGES:
                try:
                    await bot.send_photo(chat_id=DESTINATION_CHAT, photo=image_url, caption=caption)

                # We catch everything, because we don't want to stop the bot if something goes wrong.
                except Exception as e: 
                    await bot.send_message(chat_id=DESTINATION_CHAT, text=caption, parse_mode='HTML')
            else:
                await bot.send_message(chat_id=DESTINATION_CHAT, text=caption, parse_mode='HTML')

if __name__ == '__main__':
    asyncio.run(main())