import discord
import asyncio
import sqlite3
import math
import random
import itertools
import os
import subprocess
import re
import config
from helper import *
from prettytable import PrettyTable
from prettytable import from_db_cursor
from discord.ext import commands
import time
import youtube_dl
import mysql.connector as mysql
import traceback
from gtts import gTTS
from PIL import Image, ImageFilter, ImageDraw, ImageFont  # imports the library


#remake tables using splice
#conn = sqlite3.connect('data.db')

intent = discord.Intents.default()
intent.members = True
intent.message_content = True

client = commands.Bot(command_prefix = '!', description = "music", intents = intent)


youtube_dl.utils.bug_reports_message = lambda: ''


ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': 'songs/%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn -af loudnorm=I=-25:TP=-1.5:LRA=5',
    'before_options': '-ss 0'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

    @classmethod
    async def from_url2(cls, url, num, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        filename = filename.strip("songs\\")
        if(data['duration'] > 90):
            print(filename)
            c.execute('update weebquiz set filename = "'+filename+'" where number = '+str(num))
            conn.commit()
            return filename
        else:
            print(filename)
            c.execute('update weebquiz set filename = "'+filename+'" where number = '+str(num))
            conn.commit()
            return False





@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.command(pass_context = True)
@commands.cooldown(1, 2, commands.BucketType.user)
async def rewrite(ctx, *argv):

    toRewrite = []
    try:
        conn = mysql.connect(
            host = config.host,
            user = config.user,
            passwd = config.pw,
            database = config.db
            )
        c = conn.cursor(buffered=True)
        c.execute('select * from weebquiz where number > 186')
        weeb = c.fetchall()
        for x in weeb:
            print(x)
            url = x[1]
            number = str(x[2])
            rewrite = await YTDLSource.from_url2(url, number, loop=client.loop)
            if(rewrite):
                toRewrite.append(rewrite)
        print('rewriting...')
        print(toRewrite)
        for y in toRewrite:
            trim(y)
    except Exception as e:
        print(e)

    # for x in range(3,184):
        # c.execute('SELECT filename from weebquiz where number = '+ str(x-1))
        # filename = c.fetchone()[0]
        # c.execute('UPDATE weebquiz set filename = "'+filename+'" where number = '+ str(x))
        # conn.commit()

@client.command(pass_context = True)
@commands.cooldown(1, 2, commands.BucketType.user)
async def connect(ctx, *argv):
    channel = ctx.message.author.voice.channel
    if ctx.voice_client is not None:
        return await ctx.voice_client.move_to(channel)
    await channel.connect()

@client.command(pass_context = True)
@commands.cooldown(1, 2, commands.BucketType.user)
async def disconnect(ctx, *argv):
    await ctx.voice_client.disconnect()

@client.command(pass_context = True)
async def play(ctx, *argv):
    """Plays a file from the local filesystem"""
    try:

        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("songs/youtube-bu8hmIjf1VU-Danny_McCarthy_-_Silver_Scrapes.webm"))
        ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)

        await ctx.send('Now playing: {}'.format(query))
    except:
        traceback.print_exc()


@client.command(pass_context = True)
async def stream(ctx, url):
    """Streams from a url (same as yt, but doesn't predownload)"""
    try:
        if ctx.voice_client is None:
                await ctx.author.voice.channel.connect(reconnect=True)
        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=client.loop, stream=True)
            ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

        await ctx.send('Now playing: {}'.format(player.title))
    except:
        traceback.print_exc()

@client.command(pass_context = True)
@commands.cooldown(1, 2, commands.BucketType.user)
async def volume(ctx, volume):
    voice = ctx.voice_client
    voice.source.volume = float(volume)/100

@client.command(pass_context = True)
@commands.cooldown(1, 2, commands.BucketType.user)
async def stop(ctx, *argv):
    ctx.voice_client.stop()



# @client.command(pass_context = True)
# async def add(ctx, *argv):
    # if len(argv) == 2:
        # try:
            # aliases = argv[1]
            # url = argv[0]
            # c.execute("INSERT INTO WeebQuiz (answers,url) VALUES ('"+aliases+"', '"+url+"')")
            # conn.commit()
            # await ctx.send('Entry Successfully saved to database')
        # except Exception as e:
            # await ctx.send('Failed to submit the entry')

    # else:
        # try:
            # await ctx.send('Please enter the url of the song:')

            # def check(m):
                # return m.channel == ctx.message.channel and m.author == ctx.message.author

            # msg = await client.wait_for('message', check=check, timeout = 20.0)
            # url = msg.content

            # await ctx.send('Please enter the acceptable answers for this song in one message seperated by commas:')
            # msg = await client.wait_for('message', check=check, timeout = 20.0)
            # aliases = msg.content
            # c.execute("INSERT INTO WeebQuiz (answers,url) VALUES ('"+aliases+"', '"+url+"')")
            # conn.commit()
            # await ctx.send('Successfully saved to database')
        # except Exception as e:
            # await ctx.send('Failed to submit entry')

@client.command(pass_context = True)
async def quiz(ctx, genre = None, *argv):
    try:
        if ctx.voice_client is None:
            await ctx.author.voice.channel.connect(reconnect=True)
        loop = True
        scoreboard = []
        unique = []
        if(genre):
            conn = mysql.connect(
                host = config.host,
                user = config.user,
                passwd = config.pw,
                database = config.db
                )
            c = conn.cursor(buffered=True)
            c.execute('SELECT * FROM WeebQuiz where genre = "'+genre+'" ORDER BY RAND() LIMIT 1')
            weebQuiz = c.fetchall()
            if (len(weebQuiz) == 0):
                await ctx.send("That's not a valid genre b-b-baka")
                loop = False
            conn.close()
        while(loop):
            try:

                uniqueLoop = True
                tries = 0
                print('enter loop')
                while(uniqueLoop):
                    try:
                        conn = mysql.connect(
                            host = config.host,
                            user = config.user,
                            passwd = config.pw,
                            database = config.db
                            )
                        c = conn.cursor(buffered=True)
                        tries = tries + 1
                        print(tries)
                        if(genre):
                            c.execute('SELECT * FROM WeebQuiz where genre = "'+genre+'" ORDER BY RAND() LIMIT 1')
                            weebQuiz = c.fetchall()
                        else:
                            c.execute('SELECT * FROM WEEBQUIZ ORDER BY RAND() LIMIT 1')
                            weebQuiz = c.fetchall()
                        entry = weebQuiz[0][2]
                        if(any(x == entry for x in unique)):
                            continue
                        else:
                            uniqueLoop = False
                    except:
                        traceback.print_exc()

                unique.append(entry)
                entry = str(entry)
                print(entry)
                print(unique)
                fileName = weebQuiz[0][3]
                answers = re.split(',|, ',weebQuiz[0][0])
                print(answers)
                random_offset = random.randrange(1,60)
                ffmpeg_options['before_options'] = '-ss ' +str(random_offset)
                print(ffmpeg_options['before_options'])
                    
                if ctx.voice_client is None:
                    await ctx.author.voice.channel.connect(reconnect=True)  

                    
                source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("songs/" + fileName,**ffmpeg_options))
                ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)
                channel = ctx.message.channel

                await ctx.send('Guess this song!')

                def check(m):
                    return m.channel == channel and any(x == m.content.lower() for x in answers) or m.content.lower() == '!end'
                try:
                    msg = await client.wait_for('message', check=check, timeout = 20)
                    if msg.content == '!end':
                        ctx.voice_client.stop()
                        loop = False
                        break
                    else:
                        printString = msg.author.mention + ' You got it right!'
                        ctx.voice_client.stop()
                        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("songs/correct sound effect.mp3"))
                        ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)
                        if(len(scoreboard)==0):
                            scoreboard.append([msg.author.name, 1])
                        else:
                            index = 0
                            present = False
                            for x in scoreboard:
                                if x[0] == msg.author.name:
                                    present = True
                                    break
                                index += 1
                            if (present):
                                scoreboard[index][1] += 1
                                if (scoreboard[index][1] == 10):
                                    loop = False
                                    await ctx.send(':trophy: :trophy:' +msg.author.mention + ' has won the game!:trophy: :trophy:')
                                    ctx.voice_client.stop()
                                    announcement= "Congratulations " + msg.author.name + " You win!"
                                    
                                    announce = gTTS(text=announcement,lang='ja', slow=False)
                                    
                                    announce.save('songs/winner.mp3')
                                    
                                    source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("songs/winner.mp3"))
                                    ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)
                                    await asyncio.sleep(5)
                                    ctx.voice_client.stop()
                                    source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("songs/Final Fantasy VII - Victory Fanfare [HQ].mp3"))
                                    ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)
                                    await asyncio.sleep(10)
                                    ctx.voice_client.stop()


                                    break
                            else:
                                scoreboard.append([msg.author.name, 1])
                        printString += '**\nCURRENT SCORE**:\n```\n'
                        for x in scoreboard:
                            printString += str(x[0]) + ' ' + str(x[1]) + '\n'
                        printString = printString + '```'
                        await ctx.send(printString)
                        await asyncio.sleep(1)
                except asyncio.TimeoutError:
                    await ctx.send('No one got this one!')



                ctx.voice_client.stop()
                conn.close()
                await asyncio.sleep(2)
            except:
                traceback.print_exc()
    except:
        traceback.print_exc()

# async def jeopardy(ctx, *argv):
    # img = Image.open(images/blank_jeopardy_board.png)
    # font = ImageFont.truetype("PleasantlyPlump-pRv1.ttf", 24)
    # draw = ImageDraw.Draw(img)
    # score = "100"
    # draw.text((0,150), score, (0,0,0) font = font)
    # img.save("output.png")

def trim(filename):
    os.chdir('D:/discordbot/songs')
    filename2 = filename.split('.')
    outputFile = ""
    for x in filename2:
        outputFile = outputFile + '2.' + x
    print(outputFile)
    subprocess.call(['ffmpeg', '-i', filename, '-t', '00:01:30.00', outputFile])
    os.remove(filename)
    c.execute('update weebquiz set filename = "'+outputFile+'" where filename = "'+filename+'"')
    conn.commit()


extensions = ['jeopardy']

async def load(extensions):
    async with client:
        if __name__ == '__main__':
            for extension in extensions:
                try:
                    await client.load_extension(extension)
                    print('Loaded extension: {}'.format(extension))
                except Exception as error:
                    print('{} cannot be loaded. [{}]'.format(extension, error))
        await client.start(config.TOKEN)



asyncio.run(load(extensions))


