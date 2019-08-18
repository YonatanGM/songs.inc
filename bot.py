from telethon import TelegramClient, events, utils
from telethon.tl.types import InputBotInlineResult
import pandas as pd
from fuzzywuzzy import process
import numpy, random, logging, csv



logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
level=logging.WARNING)

api_id = 937875
api_hash = '91895d720754903477ed269223104595'
TOKEN = '813113477:AAHhTvv1WwlpBCjZ6N3WDbXFHPjvOymrg9A'

bot = TelegramClient('bot', api_id, api_hash).start(bot_token=TOKEN)


@bot.on(events.NewMessage(pattern='/start'))
async def send_welcome(event):
    await event.reply('How are you doing?')


@bot.on(events.NewMessage)
async def handler(message):
    if message.audio:
        if message.file.title and message.file.performer:
            chat = await message.get_sender()
            info = [message.file.title.lower(), message.file.performer.lower(), message.id, chat.id]
            with open("collection.csv", 'a', encoding='utf8') as file:
                writer = csv.writer(file)
                writer.writerow(info)

        await bot.send_message(chat, "Done. Thanks for supporting us!")
        

        
@bot.on(events.InlineQuery(pattern="^(?!\s*$).+"))
async def inlinehandler(event):
    builder = event.builder
    chat = await event.get_sender()
    query = event.text.lower()
    df = pd.read_csv("collection.csv", index_col=['title', 'artist'], encoding='utf8')
    title = df.index.dropna().to_list()
    result = set()
    
    x = process.extractBests(query, title, score_cutoff=90, limit=8)
    for i in range(len(x)):
        
        msg_id = df.at[x[i][0], 'msg_id']
        from_peer = df.at[x[i][0], 'from_peer']
        print(x)
        if type(msg_id) == numpy.ndarray:
            msg_id = int(msg_id[random.randint(0, len(msg_id)-1)])
        if type(from_peer) == numpy.ndarray:
            from_peer = int(from_peer[random.randint(0, len(from_peer)-1)])
        
        from_peer_entity = await bot.get_entity(int(from_peer))
        message = await bot.get_messages(int(from_peer), limit=1, ids=int(msg_id))
        resolved_id = utils.resolve_bot_file_id(message.file.id)

        result.add(builder.document(resolved_id, type='audio'))

    await event.answer(list(result))

    
    
@bot.on(events.NewMessage(pattern='/close'))
async def close(event):
    global file
    await event.reply('closing')
    file.close()
    
    
bot.run_until_disconnected()


