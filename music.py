import discord
import asyncio
import sqlite3
import math
import random
import itertools
import os
import re
import config
from helper import *
from prettytable import PrettyTable
from prettytable import from_db_cursor
from discord.ext import commands
import time
import youtube_dl
import mysql.connector as mysql

#remake tables using splice
#conn = sqlite3.connect('data.db')
conn = mysql.connect(
	host = config.host,
	user = config.user,
	passwd = config.pw,
	database = config.db
	)
c = conn.cursor(buffered=True)

client = commands.Bot(command_prefix = '!')


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
	'options': '-vn -af loudnorm=I=-16:TP=-1.5:LRA=11',
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
		print(filename)
		c.execute('update weebquiz set filename = "'+filename+'" where number = '+str(num))
		conn.commit()
		




@client.event
async def on_ready():
	print('Logged in as')
	print(client.user.name)
	print(client.user.id)
	print('------')

@client.command(pass_context = True)
@commands.cooldown(1, 2, commands.BucketType.user)
async def rewrite(ctx, *argv):
	# c.execute('SELECT * FROM WeebQuiz')
	# weebQuiz = c.fetchall()
	
	try:
		for x in range(1,185):
			print(x)
			c.execute('SELECT url FROM WeebQuiz WHERE number = '+str(x))
			url = c.fetchone()[0]
			await YTDLSource.from_url2(url, x, loop=client.loop)
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

	source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("songs/youtube-0Vwwr3VGsYg-Re_-ZERO_-_Starting_Life_in_Another_World_Opening_Theme_Redo.webm"))
	ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)

	await ctx.send('Now playing: {}'.format(query))	
	

@client.command(pass_context = True)
async def stream(ctx, url):
	"""Streams from a url (same as yt, but doesn't predownload)"""

	async with ctx.typing():
		player = await YTDLSource.from_url(url, loop=client.loop, stream=True)
		ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

	await ctx.send('Now playing: {}'.format(player.title))

@client.command(pass_context = True)
@commands.cooldown(1, 2, commands.BucketType.user)
async def volume(ctx, volume):
	voice = ctx.voice_client
	voice.source.volume = float(volume)/100
	
@client.command(pass_context = True)
@commands.cooldown(1, 2, commands.BucketType.user)
async def stop(ctx, *argv):
	ctx.voice_client.stop()
	
	
@client.command(pass_context = True)
async def okay(ctx):
	channel = ctx.message.author.voice.channel
	def check(m):
		return m.content == ctx.author and m.channel == channel

	msg = await client.wait_for('message', check=check)
	await channel.send('Hello {.author}!'.format(msg))
	
@client.command(pass_context = True)
async def add(ctx, *argv):
	if len(argv) == 2:
		try:
			aliases = argv[1]
			url = argv[0]
			c.execute("INSERT INTO WeebQuiz (answers,url) VALUES ('"+aliases+"', '"+url+"')")
			conn.commit()	
			await ctx.send('Entry Successfully saved to database')
		except Exception as e:
			await ctx.send('Failed to submit the entry')

	else:
		try:
			await ctx.send('Please enter the url of the song:')
			
			def check(m):
				return m.channel == ctx.message.channel and m.author == ctx.message.author
			
			msg = await client.wait_for('message', check=check, timeout = 20.0)
			url = msg.content
			
			await ctx.send('Please enter the acceptable answers for this song in one message seperated by commas:')
			msg = await client.wait_for('message', check=check, timeout = 20.0)
			aliases = msg.content
			c.execute("INSERT INTO WeebQuiz (answers,url) VALUES ('"+aliases+"', '"+url+"')")
			conn.commit()
			await ctx.send('Successfully saved to database')
		except Exception as e:
			await ctx.send('Failed to submit entry')
	
@client.command(pass_context = True)
async def quiz(ctx, genre = None, *argv):
		if ctx.voice_client is None:
			await ctx.author.voice.channel.connect()
		loop = True
		scoreboard = []
		unique = []
		while(loop):
			try:
				if(genre):
					c.execute('SELECT * FROM WeebQuiz where genre = "'+genre+'" ORDER BY RAND() LIMIT 1')
					weebQuiz = c.fetchall()
					if (len(weebQuiz) == 0):
						await ctx.send("That's not a valid genre b-b-baka")
						break
				else:
					c.execute('SELECT * FROM WEEBQUIZ ORDER BY RAND() LIMIT 1')
					weebQuiz = c.fetchall()
				entry = weebQuiz[0][2]
				uniqueLoop = True
				print(unique)
				while(uniqueLoop):
					if(any(x == entry for x in unique)):
						continue
					else:
						uniqueLoop = False

				unique.append(entry)
				entry = str(entry)
				print(entry)
				fileName = weebQuiz[0][3]
				answers = re.split(',|, ',weebQuiz[0][0])
				print(answers)
				random_offset = random.randrange(1,60)
				ffmpeg_options['before_options'] = '-ss ' +str(random_offset)
				print(ffmpeg_options['before_options'])
				
				source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("songs/" + fileName,**ffmpeg_options))
				ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)
				channel = ctx.message.channel
				await ctx.send('Now playing: 1')

				def check(m):
					return m.channel == channel and any(x == m.content.lower() for x in answers) or m.content.lower() == '!end'
				try:
					msg = await client.wait_for('message', check=check, timeout = 20.0)
					if msg.content == '!end':
						loop = False
					else:
						await ctx.send(msg.author.mention + ' You got it right!')
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
								if (scoreboard[index][1] == 1000):
									loop = False
									await ctx.send(msg.author.mention + ' has won the game!')
							else:
								scoreboard.append([msg.author.name, 1])
						printString = ''
						for x in scoreboard:
							printString += str(x[0]) + ' ' + str(x[1]) + '\n'
						await ctx.send(printString)
				except asyncio.TimeoutError:
					await ctx.send('No one got this one!')
				ctx.voice_client.stop()
			except Exception as e:
				print(e)



client.run(config.TOKEN)