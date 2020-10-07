import discord
import asyncio
import sqlite3
import math
import random
import itertools
from helper import *
from prettytable import PrettyTable
from prettytable import from_db_cursor
from discord.ext import commands
import time


#remake tables using splice
conn = sqlite3.connect('data.db')

c = conn.cursor()

coroutines = {}

class fishing(commands.Cog):
	def __init__(self, client):
		self.client = client
		self.coroutines = {}
		# cast = False
			

	@commands.command(pass_context = True)
	@commands.cooldown(1, 1, commands.BucketType.user)
	async def cast(self, ctx):
		# if(self.cast):
			# await self.client.say("You already had your line cast out. You now retract your line.")
			# return
		
		# self.cast = True
		try:
			if(not created(ctx.message.author.id)):
				await client.say("You don't even exist. You mean literally nothing to me. Use !create first to bring meaning to your life")
				return
			c.execute('SELECT playerState FROM Status WHERE player = "'+ctx.message.author.id+'"')
			state = c.fetchone()[0]
			global coroutines
			if(state == 'fishing'):
				c.execute('UPDATE Status SET playerState = "idle" WHERE player = "'+ctx.message.author.id+'"')
				await self.client.say('You retract your line')
				conn.commit()
				for x in coroutines[ctx.message.author.id]:
					x.cancel()
			else:
				c.execute('UPDATE Status SET playerState = "fishing" WHERE player = "'+ctx.message.author.id+'"')
				await self.client.say('You cast out your line....')
				fishy = fishingcoro(self.client)
				coroutines[ctx.message.author.id] = [self.client.loop.create_task(fishy.fishingLoop(ctx))]
				conn.commit()
		except Exception as e:
			print(repr(e))


class fishingcoro:
	def __init__(self, client):
		self.client = client
		self.struggling = False
		tension = 0
	async def fishingLoop(self, ctx):
		try:
			x = 5
			c.execute('SELECT area FROM Character WHERE id = "'+ctx.message.author.id+'"')
			area = c.fetchone()[0]
			c.execute('SELECT * FROM Fish WHERE area = "'+area+'"')
			availableFish = c.fetchall()
			iter = 0
			current = 0
			randomRange = [0]
			curMax = 100
			range = 0
			for currentFish in availableFish:
				range = 100 - currentFish[3]
				current += range
				randomRange.append(current)
				if(current >100):
					curMax = current
			cast = True
			while(cast):
				
				x = random.randint(1,curMax)
				if (x <= current):
					await self.client.send_message(ctx.message.channel, str(x))
					for index, value in enumerate(randomRange):
						if (x <= value):
							
							fish = availableFish[index-1][0]
							difficulty = availableFish[index-1][2]
							rarity = availableFish[index-1][3]
							quality = availableFish[index-1][4]
							cast = False
							break
					msg = await self.client.send_message(ctx.message.channel, ctx.message.author.mention + ' You feel a tug on your line. Quick! React with 🎣 to hook it!')
					await self.client.add_reaction(msg,'🎣')

					reaction = await self.client.wait_for_reaction(emoji='🎣', user=ctx.message.author, timeout=5, message=msg)
					if(reaction):
						endCount = 0
						await self.client.send_message(ctx.message.channel, ctx.message.author.mention + ', You have successfully hooked the fish! Your battle with the fish begins! You begin to reel it in... ')
						while(endCount <5):
							endCount += 1
							await asyncio.sleep(2)
							struggle = random.randint(1,3)
							if(struggle == 1):
								startValue = random.randint(50, 150)
								self.tension = random.randint(0, 200)
								msg2 = await self.client.send_message(ctx.message.channel, ctx.message.author.mention + ' The fish struggles violently! React with ⬆ and ⬇ to match your line tension to **'+str(startValue)+'**, then react with 🐟 to reel in your catch!\n\n Your line Tension:\n         `'+str(self.tension)+'`')
								global coroutines
								coro = self.client.loop.create_task(self.tensionLoop(difficulty, startValue))
								coroutines[ctx.message.author.id].append(coro)
								#global future
								#future = asyncio.run_coroutine_threadsafe(coro, self.client.loop)

								
								await self.client.add_reaction(msg2, '⬆')
								await self.client.add_reaction(msg2, '⬇')				
								await self.client.add_reaction(msg2, '🐟')

								self.struggling = True
								while(self.struggling):
									reacted = await self.client.wait_for_reaction(['⬆', '⬇', '🐟'] ,user = ctx.message.author, timeout=5, message=msg2)

									if(reacted):
										if (reacted.reaction.emoji == '⬆'):
											self.tension += 20
											await self.client.edit_message(msg2, new_content = ctx.message.author.mention + ' The fish struggles violently! React with ⬆ and ⬇ to match your line tension to **'+str(startValue)+'**, then react with 🐟 to reel in your catch!\n\n Your line tension:\n         `'+str(self.tension)+'`')
										elif(reacted.reaction.emoji == '⬇'):
											self.tension -= 20
											await self.client.edit_message(msg2, new_content = ctx.message.author.mention + ' The fish struggles violently! React with ⬆ and ⬇ to match your line tension to **'+str(startValue)+'**, then react with 🐟 to reel in your catch!\n\n Your line tension:\n         `'+str(self.tension)+'`')
										elif(reacted.reaction.emoji == '🐟'):
											self.struggling = False
											coro.cancel()
											c.execute('UPDATE Status SET playerState = "idle" WHERE player = "'+ctx.message.author.id+'"')
											if(abs(self.tension - startValue) <= 20):
												tension = random.randint(0, 200)
												await self.client.send_message(ctx.message.channel, 'You begin steadily reeling in....')
											else:
												await self.client.send_message(ctx.message.channel, 'The fish manages to struggle free!')
												endCount = 100
									else:
										coro.cancel()
										c.execute('UPDATE Status SET playerState = "idle" WHERE player = "'+ctx.message.author.id+'"')
										await self.client.send_message(ctx.message.channel, ctx.message.author.mention + ' Good work slowsack. The fish got away')
										endCount = 100
										self.struggling = False
								#future.set_result(True)
						if(endCount == 5):
							await self.client.send_message(ctx.message.channel, ctx.message.author.mention + ' You successfully caught a '+fish+'!')
							c.execute('SELECT id FROM Wagons WHERE owner = "'+ctx.message.author.id+'" AND rider = "'+ctx.message.author.id+'"')
							wagon = c.fetchone()[0]
							
							try:
								c.execute('SELECT stock FROM WagonInventory WHERE wagon = '+str(wagon)+' AND item = "'+fish+'" AND quality = '+str(quality))
								stock = c.fetchone()[0]
								stock += 1
								c.execute('UPDATE WagonInventory SET stock = '+str(stock)+' WHERE wagon = '+str(wagon)+' AND item = "'+fish+'" AND quality = '+str(quality))

							except Exception as e1:
								print(e1)
								try:
									c.execute('INSERT INTO WagonInventory(item, stock, quality, wagon) VALUES("'+fish+'", 1, '+str(quality)+', '+str(wagon)+')')
								except Exception as e:
									print(e)
							
							c.execute('SELECT stock FROM Items WHERE Item = "'+fish+'"')
							stock = c.fetchone()[0]
							stock += 1
							c.execute('UPDATE Status SET playerState = "idle" WHERE player = "'+ctx.message.author.id+'"')
							c.execute('UPDATE Items SET stock  = '+str(stock)+' WHERE item = "'+fish+'"')
							conn.commit()
					else:
						c.execute('UPDATE Status SET playerState = "idle" WHERE player = "'+ctx.message.author.id+'"')
						await self.client.send_message(ctx.message.channel, ctx.message.author.mention + ' Good work slowsack. The fish got away')
				await asyncio.sleep(5)

		except Exception as e:
			print(repr(e))
		return

	async def tensionLoop(self, difficulty, startValue):
		while(True):
			count = 5
			await asyncio.sleep(count)
			x = random.randint(-50, 50)
			self.tension = self.tension + x
			if(self.tension<0):
				self.tension = 0
			if(count >3):
				count -= 1
			
		
		return
	
def locationCheck(charName):
	c.execute('SELECT area FROM Character WHERE id = "'+str(charName)+'"')
	location = c.fetchone()[0]
	area = location.split('_')[-1]
	
	if(area == 'casino'):
		return(True)
	else:
		return(False)
	

	
def setup(client):
	client.add_cog(fishing(client))	
