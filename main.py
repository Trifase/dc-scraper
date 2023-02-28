import httpx
import asyncio
import time
import datetime
from telegram import Bot

import config


BOT_TOKEN = config.BOT_TOKEN
DESTINATION_CHATS = config.DESTINATION_CHATS

MINUTES = config.MINUTES
SINGLE_POST = config.SINGLE_POST
IMAGES = config.IMAGES
BOARDS = config.BOARDS


async def main():
    async def get_last_threads_from_board(board):
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(f'https://www.diochan.com/{board}/catalog.json')
            response.raise_for_status()
            return response.json()

    diochan = {}
    for board in BOARDS:
        # print(f"Getting threads from {board}")
        diochan[board] = await get_last_threads_from_board(board)
    now = int(time.time())

    delta_timestamp = 60 * MINUTES
    not_before = now - delta_timestamp
    threads = []

    for board in BOARDS:
        for page in diochan[board]:
            for thread in page['threads']:
                if thread['time'] > not_before:
                    # print(thread)
                    t = {
                        'board': board,
                        'thread': thread['no'],
                        'time': thread['time'],
                        'title': thread.get('sub'),
                        'text': thread['com'],
                        'thread_url' : f"https://www.diochan.com/{board}/res/{thread['no']}.html"
                    }
                    if thread.get('tim'):
                        t['image_url'] = f"https://www.diochan.com/{board}/src/{thread['tim']}{thread['ext']}"
                        t['is_video'] = False
                    elif thread.get('embed'):
                        t['is_video'] = True
                        youtube_id = thread['embed'].split('"')[11][39:]
                        t['image_url'] = f'http://i3.ytimg.com/vi/{youtube_id}/hqdefault.jpg'
                        t['video_url'] = f"https://www.youtube.com/watch?v={youtube_id}"
                    threads.append(t)
    

    bot = Bot(token=config.BOT_TOKEN)
    if SINGLE_POST:
        message = ''
        for thread in threads:
            timestamp = datetime.datetime.utcfromtimestamp(thread['time']).strftime('%d/%m/%Y %H:%M')
            text = thread['text'].replace('<br/>','\n').replace('<span class="quote">&gt;','>').replace('</span>','')
            if len(text) > 1000:
                text = text[:1000] + "..."
            link = f"<a href='{thread['thread_url']}'>/{thread['board']}/ | No.{thread['thread']}</a> | {timestamp}"
            if thread['is_video']:
                link += f"\n<a href='{thread['video_url']}'>[YouTube]</a>"
            message += f"{link}\n{text}\n\n"
        for chat_id in DESTINATION_CHATS:
            await bot.send_message(chat_id=chat_id, text=message, parse_mode='HTML')
    
    else:
        for thread in threads:
            timestamp = datetime.datetime.utcfromtimestamp(thread['time']).strftime('%d/%m/%Y %H:%M')
            text = thread['text'].replace('<br/>','\n').replace('<span class="quote">&gt;','>').replace('</span>','')
            if len(text) > 1000:
                text = text[:1000] + "..."
            link = f"<a href='{thread['thread_url']}'>/{thread['board']}/ | No.{thread['thread']}</a> | {timestamp}"
            
            if thread['is_video']:
                link += f"\n<a href='{thread['video_url']}'>[YouTube]</a>"

            message = f"{link}\n{text}"
            image_url = thread['image_url']

            for chat_id in DESTINATION_CHATS:
                if IMAGES:
                    try:
                        await bot.send_photo(chat_id=chat_id, photo=image_url, caption=message, parse_mode='HTML')

                    # We catch everything, because we don't want to stop the bot if something goes wrong. We send a basic text message.
                    except Exception as e: 
                        print(e)
                        await bot.send_message(chat_id=chat_id, text=message, parse_mode='HTML')
                else:
                    await bot.send_message(chat_id=chat_id, text=message, parse_mode='HTML')

if __name__ == '__main__':
    asyncio.run(main())