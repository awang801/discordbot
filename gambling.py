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
import traceback


#remake tables using splice
conn = sqlite3.connect('data.db')

c = conn.cursor()

class gambling(commands.Cog):
	def __init__(self, client):
		self.client = client
			
	@commands.command(aliases=['ou', 'roll'], pass_context = True)
	@commands.cooldown(1, 2, commands.BucketType.user)
	async def overunder(self, ctx, *argv):
		if(not created(str(ctx.message.author.id))):
			await ctx.send("You don't even exist. You mean literally nothing to me. Use !create first to bring meaning to your life")
			return

		if(not locationCheck(str(ctx.message.author.id))):
			await ctx.send("You can't just tryna be gamblin' out in broad daylight dawg. Get to the nearest casino to satisfy you gambling needs")
			return

		
		try:
			call = ouCheck(argv[0])
			bet = int(argv[1])
		except Exception as e:
			print(e)
			await ctx.send('Please input the command --> over/under/exact --> the amount you are betting:\n ```!ou exact 1000```')
			return
		
		if(bet <= 0):
			await ctx.send('Plesae enter a number greater than 0')
			return
		c.execute('SELECT stock FROM inventory WHERE item = "money" AND owner = "'+str(ctx.message.author.id)+'"')
		money = c.fetchone()[0]	
		
		if(bet<=money):
			x = random.randint(1,6)
			y = random.randint(1,6)
			roll1 = x + y
			await ctx.send('Your first roll is a **'+str(roll1)+'**\nWould you like to change your call? (If you change your call, you only receive a quarter of the bet if you win but still lose the entirety of the bet if you lose)\nType your new call (over/exact/under) or just type *roll* to continue.')
			correctResponse = False
			changeBet = False
			while(not correctResponse):
				try:
					response = await self.client.wait_for('message', check=lambda m: m.author==ctx.author and m.channel==ctx.message.channel, timeout=20)
					if response == None or response.content.lower() == 'roll':
						correctResponse = True
					elif (response.content.lower() == 'over' or response.content.lower() == 'under' or response.content.lower() == 'exact'):
						try:
							call = ouCheck(response.content)
							correctResponse = True
							changeBet = math.floor(bet/4)
						except:
							await ctx.send('not a valid call, please re-enter your response i.e. `change over` or `roll` to continue')
					else:
						await ctx.send("I'm too BAKA to understand what you are saying, please try again")
				except Exception as e:
					print(e)

			if changeBet:
				newBet = changeBet
			else:
				newBet = bet
			
			z = random.randint(1,6)
			n = random.randint(1,6)
			roll2 = z + n

			if(call == 'over'):
				if(roll1 < roll2):
					newMoney = money + newBet
					c.execute('UPDATE inventory SET stock = '+str(newMoney)+' WHERE item = "money" AND owner = "'+str(ctx.message.author.id)+'"')
					await ctx.send('Your second roll is a **'+str(roll2)+'**\nYour second roll was higher than your first roll! You won **'+str(newbet)+'**!')
				else:
					newMoney = money - bet
					c.execute('UPDATE inventory SET stock = '+str(newMoney)+' WHERE item = "money" AND owner = "'+str(ctx.message.author.id)+'"')
					await ctx.send('Your second roll is a **'+str(roll2)+'**\nYour second roll was NOT higher than your first roll! You lost **'+str(bet)+'**!')			
			elif(call == 'under'):
				if(roll1 > roll2):
					newMoney = money + newBet
					c.execute('UPDATE inventory SET stock = '+str(newMoney)+' WHERE item = "money" AND owner = "'+str(ctx.message.author.id)+'"')
					await ctx.send('Your second roll is a **'+str(roll2)+'**\nYour second roll was lower than your first roll! You won **'+str(newBet)+'**!')
				else:
					newMoney = money - bet
					c.execute('UPDATE inventory SET stock = '+str(newMoney)+' WHERE item = "money" AND owner = "'+str(ctx.message.author.id)+'"')
					await ctx.send('Your second roll is a **'+str(roll2)+'**\nYour second roll was NOT lower than your first roll! You lost **'+str(bet)+'**!')	
			elif(call == 'exact'):
				if(roll1 == roll2):
					newBet = 8*newBet
					newMoney = money + newBet
					c.execute('UPDATE inventory SET stock = '+str(newMoney)+' WHERE item = "money" AND owner = "'+str(ctx.message.author.id)+'"')
					await ctx.send('Your second roll is a **'+str(roll2)+'**\nYour second roll was equal to your first roll! You won **'+str(newBet)+'**!')
				else:
					newMoney = money - bet
					c.execute('UPDATE inventory SET stock = '+str(newMoney)+' WHERE item = "money" AND owner = "'+str(ctx.message.author.id)+'"')
					await ctx.send('Your second roll is a **'+str(roll2)+'**\nYour second roll was NOT equal to your first roll! You lost **'+str(bet)+'**!')
			conn.commit()
		else:
			await ctx.send("You ain't got enough cheddar for that brother")
		return
		

	@commands.command(aliases=['toss', 'flip', 'c'], pass_context = True)
	@commands.cooldown(1, 2, commands.BucketType.user)
	async def coin(self, ctx, *argv):
		try:
			if(not created(str(ctx.message.author.id))):
				await ctx.send("You don't even exist. You mean literally nothing to me. Use !create first to bring meaning to your life")	
				return
			if(not locationCheck(str(ctx.message.author.id))):
				await ctx.send("You can't just tryna be gamblin' out in broad daylight dawg. Get to the nearest casino to satisfy you gambling needs")
				return
			try:
				if(argv[0].lower() == 'heads'):
					failed = 'tails'
					success = 'heads'
					flip = 1
				elif(argv[0].lower() == 'tails'):
					failed = 'heads'
					success = 'tails'
					flip = 2
				else:
					raise ValueError()
				bet = int(argv[1])
			except:
				await ctx.send('Please input the command --> heads or tails --> the amount you are betting:\n ```!coin heads 100```')
				return
			

			if(bet <=0):
				await ctx.send('Please enter a number greater than 0')
				return
			c.execute('SELECT stock FROM inventory WHERE item = "money" AND owner = "'+str(ctx.message.author.id)+'"')
			money = c.fetchone()[0]
			
			if(bet<=money):
				flipped = random.randint(1,2)
				if(flip == flipped):
					newMoney = money + bet
					c.execute('UPDATE inventory SET stock = '+str(newMoney)+' WHERE item = "money" AND owner = "'+str(ctx.message.author.id)+'"')
					conn.commit()
					await ctx.send('**'+success.capitalize()+'** was flipped! You won **'+str(bet)+'**!')
				else:
					newMoney = money - bet
					c.execute('UPDATE inventory SET stock = '+str(newMoney)+' WHERE item = "money" AND owner = "'+str(ctx.message.author.id)+'"')
					conn.commit()	
					await ctx.send('**'+failed.capitalize()+'** was flipped! You lost **'+str(bet)+'**!')
				print(money)
				print(newMoney)

			else:
				await ctx.send("You ain't got enough cheddar for that brother")
		except Exception as e:
			print(e)
			traceback.print_exc()
		return

def ouCheck(choice):
	if(choice.lower() == 'over'):
		call = 'over'
	elif(choice.lower() == 'under'):
		call = 'under'
	elif(choice.lower() == 'exact'):
		call = 'exact'
	else:
		raise ValueError()
	return(call)		

def locationCheck(charName):
	c.execute('SELECT area FROM Character WHERE id = "'+charName+'"')
	location = c.fetchone()[0]
	area = location.split('_')[-1]
	
	if(area == 'casino'):
		return(True)
	else:
		return(False)
	
def created(charName):
	try:
		c.execute('SELECT * FROM Character WHERE id = "'+str(charName)+'"')
		test = c.fetchone()[0]
		return(True)
	except:
		return(False)
	
def setup(client):
	client.add_cog(gambling(client))	
