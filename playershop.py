import discord
import asyncio
import sqlite3
import math
import random
import itertools
from prettytable import PrettyTable
from prettytable import from_db_cursor
from discord.ext import commands
import time


#remake tables using splice
conn = sqlite3.connect('data.db')

c = conn.cursor()

class playershop(commands.Cog):
	def __init__(self, client):
		self.client = client
	
	@commands.command(pass_context = True)
	@commands.cooldown(1,2, commands.BucketType.user)
	async def myShop(self, ctx):
		return
	
	@commands.command(pass_context = True)
	@commands.cooldown(1,2, commands.BucketType.user)
	async def buystall(self, ctx):
		if(not created(ctx.message.author.id)):
			await self.client.say("You don't even exist. You mean literally nothing to me. Use !create first to bring meaning to your life")	
			return
		c.execute('SELECT currentCity FROM Character WHERE id = "'+ctx.message.author.id+'"')
		city = c.fetchone()[0]
		c.execute('SELECT realEstate FROM Cities WHERE name = "'+city+'"')
		realEstate = c.fetchone()[0]
		c.execute('SELECT stock FROM Inventory WHERE item = "money" AND owner = "'+ctx.message.author.id+'"')
		money = c.fetchone()[0]
		try:
			if(realEstate > money):
				await self.client.say("This is NOT free real estate, it's "+str(realEstate)+" real estate. Get your working class ass out of here")
				return
			else:
				await self.client.say('Buying a shop here will cost '+str(realEstate)+'. \nWould you like to go through with your purchase?(y/n)')
				response = await self.client.wait_for_message(author=ctx.message.author, timeout=10)
				if response:
					if (response.content == 'y'):
						await self.client.say('Please name your shop:')
						response2 = await self.client.wait_for_message(author = ctx.message.author, timeout = 20)
						if response2:
							storeName = response2.content
							newMoney = money - realEstate
							try:
								c.execute('INSERT INTO PlayerShop(area, owner, name) VALUES("'+city+'_grand market", "'+ctx.message.author.id+'", "'+storeName+'")')
								c.execute('UPDATE Inventory SET stock = '+str(newMoney)+' WHERE owner = "'+ctx.message.author.id+'"')
								await self.client.say("Congratulations! You have managed to secure a shop in the Grand Market of "+city)
								conn.commit()
								return
							except Exception as e:
								print(e)
								await self.client.say('Something went wrong!')
						else:
							await self.client.say("Hey it's a shop not your firstborn, come back when you decide on a name")
							return
					elif(response.content == 'n'):
						await self.client.say('Alright then, stay poor kid.')
					else:
						await self.client.say("I'm too BAKA to understand what you are saying")
				else:
					await self.client.say("I ain't got all the time in the world for working class peasants. Come back when you are ready to move up in the world")
		except Exception as e:
			print(e)
def created(charName):
	try:
		c.execute('SELECT * FROM Character WHERE id = "'+charName+'"')
		test = c.fetchone()[0]
		return(True)
	except:
		return(False)		
def setup(client):
	client.add_cog(playershop(client))	