import discord
import asyncio
import sqlite3
import math
import random
import itertools
import config
from helper import *
from prettytable import PrettyTable
from prettytable import from_db_cursor
from discord.ext import commands
import time
import traceback
import mysql.connector as mysql

#remake tables using splice
conn = mysql.connect(
	host = config.host,
	user = config.user,
	passwd = config.pw,
	database = config.db
	)


c = conn.cursor(buffered=True)

client = commands.Bot(command_prefix = '!')

#@client.event
#async def on_message(message):
    # we do not want the bot to reply to itself
	#if message.author == client.user:
		#return

	#if message.content.startswith('i/'):
		#await client.send_message(message.channel, input + author)
		#await client.send_message(message.channel, switch(message))
@client.event
async def on_ready():
	print('Logged in as')
	print(client.user.name)
	print(client.user.id)
	print('------')
	#client.loop.create_task(shopStockUpdate())


	
@client.command(brief = 'brief', description = 'description', help = 'help', pass_context = True)
@commands.cooldown(1, 2, commands.BucketType.user)
async def test(ctx, *argv):
	try:
		msg = await ctx.send('anone')
		
		await client.add_reaction(msg, '💢')
		await client.add_reaction(msg, '👍')
		await client.add_reaction(msg, '👎')
		reaction = await client.wait_for_reaction(['👎', '👍', '💢'], message = msg, user = ctx.message.author, timeout=5)
		print(type(reaction.reaction.emoji))
		if(reaction):
			await ctx.send(str(reaction.reaction.emoji))
	except Exception as e:
		print(e)


		
		
@client.command(aliases = ['description', 'd'], pass_context = True)
@commands.cooldown(1, 2, commands.BucketType.user)
async def describe(ctx, *city):
	#city not provided
	try:
		if len(city) < 1:
			c.execute("SELECT currentCity FROM characters WHERE id = '{}'".format(str(ctx.message.author.id)))
			currentCity = c.fetchone()[0]
			c.execute('SELECT name FROM cities')
			result = c.fetchall()
			x = ""
			for row in result:
				if(cityFound(row[0], str(ctx.message.author.id))):
					x += row[0].capitalize() + "\n"
			await ctx.send("Cities you can look at a description of:```\n" + x + "```\n\n Please type the city name you would like to travel to ask about after the command:\n ```!describe Lumbridge```")
			return
		
		#city provided
		else:		
			temp = ''
			for value in city:
				if temp == '':
					temp += value
				else:
					temp += " " + value
			myCity = temp.lower()
			if(getCityLocation(myCity)):
				if (not cityFound(myCity, str(ctx.message.author.id))):
					await ctx.send('*You have heard stories of '+myCity.capitalize()+', but does such a land even really exist?*')
					return
				c.execute('SELECT description FROM cities WHERE name = "'+myCity+'"')
				description = c.fetchone()[0]
				await ctx.send(description)
			else:
				await ctx.send('Nice try guy, '+myCity+' does not exist')
			
			
	except:
		traceback.print_exc()
	
@client.command(pass_context = True)
@commands.cooldown(1, 2, commands.BucketType.user)
async def delete(ctx):
	try:
		c.execute('SELECT id FROM Wagons WHERE owner = "'+str(ctx.message.author.id)+'"')
		wagons = c.fetchall()
		
		for wagon in wagons:
			c.execute('DELETE FROM WagonInventory WHERE wagon = '+str(wagon[0]))
		c.execute('DELETE FROM Wagons WHERE owner = "'+str(ctx.message.author.id)+'"')
			
		c.execute('DELETE FROM Inventory WHERE owner = "'+str(ctx.message.author.id)+'"')
			
		c.execute('DELETE FROM Characters WHERE id = "'+str(ctx.message.author.id)+'"')
		
		conn.commit()
		
		await ctx.send("Don't kid yourself. You know you'll be back")
	except Exception as e:
		print(e)

@client.command(pass_context = True)
@commands.cooldown(1, 2, commands.BucketType.user)
async def upgrade(ctx, *argv):
	if(not created(str(ctx.message.author.id))):
		await ctx.send("You don't even exist. You mean literally nothing to me. Use !create first to bring meaning to your life")	
		return
	if(locationisStables(str(ctx.message.author.id))):
		try:
			#did not give size or speed
			if(len(argv)<1):
				await ctx.send('What would you like to upgrade? Type *speed* or *size*')
				response = await client.wait_for('message', check=lambda m: m.author==ctx.message.author and m.channel==ctx.message.channel, timeout=7)
				if response:
					if(response.content.lower() == 'size'):
						toUpgrade = 'size'
					elif(response.content.lower() == 'speed'):
						toUpgrade = 'speed'
					else:
						await ctx.send("That's not speed or size genius")
						return
					print(response.content)
			
			#gave size or speed
			else:
				if(argv[0].lower() == 'size'):
					toUpgrade = 'size'
				elif(argv[0].lower() == 'speed'):
					toUpgrade = 'speed'
				else:
					await ctx.send("That's not speed or size dumbass")
					return
			c.execute('SELECT id FROM wagons WHERE owner = "'+str(ctx.message.author.id)+'" AND rider = "'+str(ctx.message.author.id)+'"')
			wagon = c.fetchone()[0]
			
			c.execute('SELECT stock FROM Inventory WHERE item = "money" AND owner = "'+str(ctx.message.author.id)+'"')
			money = c.fetchone()[0]
			
			#size upgrade
			if (toUpgrade == 'size'):
				c.execute('SELECT size FROM wagons WHERE id = '+str(wagon))
				size = int(c.fetchone()[0]) + 100
				cost = int((size*size)/40)
				if(cost<=money):
					await ctx.send('Upgrading the size of your wagon will cost '+str(cost)+'\nWould you like to get this upgrade?(y/n)')
					response = await client.wait_for('message', check=lambda m: m.author==ctx.message.author and m.channel==ctx.message.channel, timeout= 7)
					if response:
						if(response.content == 'y'):
							money = money-cost
							c.execute('UPDATE Inventory SET stock = '+str(money)+' WHERE owner = "'+str(ctx.message.author.id)+'"')
							c.execute('UPDATE wagons SET size = '+str(size)+' WHERE id = '+str(wagon))
							conn.commit()
							await ctx.send('Your wagon now has a size of '+str(size))
						elif(response.content == 'n'):
							await ctx.send("You're really content with that size? I mean... I guess")
						else:
							await ctx.send('Wrong answer')
				else:
					await ctx.send("Upgrading the size of your wagon will cost "+str(cost)+"\nYou really thought your peon-lookin' ass could afford it?")
			
			#speed upgrade
			elif(toUpgrade == 'speed'):
				c.execute('SELECT speed FROM wagons WHERE id = '+str(wagon))
				speed = int(c.fetchone()[0]) + 1
				cost = int(1000 * speed * speed)
				if(cost<=money):
					await ctx.send('Upgrading the speed of your wagon will cost **'+str(cost)+'**\nWould you like to get this upgrade?(y/n)')
					response = await client.wait_for('message', check=lambda m: m.author==ctx.message.author and m.channel==ctx.message.channel, timeout= 7)
					if response:
						if(response.content == 'y'):
							money = money-cost
							c.execute('UPDATE Inventory SET stock = '+str(money)+' WHERE owner = "'+str(ctx.message.author.id)+'"')					
							c.execute('UPDATE wagons SET speed = '+str(speed)+' WHERE id = '+str(wagon))
							conn.commit()
							await ctx.send('Your wagon now has a speed of '+str(speed))
						elif(response.content == 'n'):
							await ctx.send('Guess you gotta get fast another time')
						else:
							await ctx.send('Wrong answer')
				else:
					await ctx.send("Upgrading the speed of your wagon will cost **"+str(cost)+"**\nYou really thought your peon-lookin' ass could afford it?")
		except Exception as e:
			print(e)
			return
	else:
		await ctx.send('You must be at the stables to upgrade your wagon')
		
@client.command(aliases=['b'], pass_context = True)
@commands.cooldown(1, 2, commands.BucketType.user)
async def buy(ctx, *argv):
	try:
		if(not created(str(ctx.message.author.id))):
			await ctx.send("You don't even exist. You mean literally nothing to me. Use !create first to bring meaning to your life")
			return
		jailed = jailCheck(str(ctx.message.author.id))
		if(jailed):
			await ctx.send(jailed)
			return

		item = ''
		amt = 0
		for value in argv:
			try:
				amt = int(value)
			except:
				if item == '':
					item += value
				else:
					item += " " + value

		
		c.execute('SELECT area FROM Characters WHERE id = '+ str(ctx.message.author.id))
		area = c.fetchone()[0]
		
		amount = math.floor(float(amt))
		
		if(not item or not amt):
			await ctx.send("Please input the item you want to buy followed by the amount of that item you want to buy:\n ```!buy egg 40```")
			return
		if(amt <= 0):
			await ctx.send('Please input a number greater than 0')
			return
		#check if item exists in area
		try:
			c.execute('SELECT item FROM Shop WHERE area = "'+area+'" AND item = "'+item+'"')
			itemCheck = c.fetchone()[0]
		except:
			await ctx.send('This item either is not sold here or does not exist. \n Use !shop to find out what is sold here')
			return
		
		price = math.floor(getPrice(item, area))
		c.execute('SELECT stock FROM Inventory WHERE owner = "'+str(ctx.message.author.id)+'" AND item = "money"')
		money = c.fetchone()[0]
		cost = price * amount

		c.execute('SELECT size FROM Items WHERE item = "'+item+'"')
		buySize = int(c.fetchone()[0]) * amount
		

		#check if funds available
		if(cost <= money):
		
			#check if here is adequate space in the wagon
			if(buySize <= wagonSpace(str(ctx.message.author.id))):
				
				c.execute('SELECT stock FROM shop WHERE area = "'+area+'" AND item = "'+item+'"')
				shopStock = c.fetchone()[0]
				
				#check if there is enough stock in the store
				if(int(amt) <= int(shopStock)):
				#Update Shop Stock
					soldOut = False #Boolean to check if the item sold out to update popularity later.
					newShopStock = int(shopStock - amount)
					if (newShopStock == 0):
						soldOut = True
					else:
						try:
							c.execute('UPDATE Shop SET stock = '+str(newShopStock)+' WHERE area = "'+area+'" AND item = "'+item+'"')
						except:
							await ctx.send('Shop stock not updated')
				
					
					#Update Money
					newCost = money - cost
					try:
						c.execute('UPDATE Inventory SET stock = '+str(newCost)+' WHERE owner = "'+str(ctx.message.author.id)+'" AND item = "money"')
					except:
						await ctx.send('Player money not updated')
					
					#Update Player Inventory(WagonInventory)
					c.execute('SELECT quality FROM Shop WHERE area = "'+area+'" AND item = "'+item+'"')
					quality = c.fetchone()[0]
					
					c.execute('SELECT id FROM Wagons WHERE owner = "'+str(ctx.message.author.id)+'" AND rider = "'+str(ctx.message.author.id)+'"')
					wagon = c.fetchone()[0]
					
					try:
						newStock = 0
						c.execute('SELECT stock FROM WagonInventory WHERE item = "'+str(item)+'" AND wagon = '+str(wagon)+' AND quality = '+str(quality))
						oldStock = c.fetchone()[0]
						newStock = oldStock + amount
						
						c.execute('UPDATE WagonInventory SET stock = '+str(newStock)+' WHERE item = "'+str(item)+'" AND quality = '+str(quality)+' AND wagon = '+str(wagon))
					except:
						try:
							c.execute('INSERT INTO WagonInventory(item, stock, quality, wagon) VALUES("'+str(item)+'", '+str(amount)+', '+str(quality)+', '+str(wagon)+')')
						except:
							await ctx.send('wagon inventory not updated')
					
					
					#global.popularity update
					try:
						c.execute('SELECT popularity FROM Items WHERE item = "'+item+'"')
						popularity = c.fetchone()[0]
						newPopularity = popularity + cost
						c.execute('UPDATE Items SET popularity = '+str(newPopularity)+' WHERE item = "'+item+'"')
						inflationCheck(item, newPopularity)
					except:
						print('global popularity not updated')
					
					#update city popularity modifer
					try:
						if(soldOut):
							c.execute('SELECT buy_multiplier FROM Shop WHERE item = "'+item+'" AND area = "'+area+'"')
							newPrice = float(c.fetchone()[0]) + 0.1
							print(newPrice)
							c.execute('UPDATE Shop SET buy_multiplier = '+str(newPrice)+' WHERE item = "'+item+'"')
						c.execute('SELECT popularity FROM Demand WHERE item = "'+item+'" AND area = "'+area+'"')
						pop = int(c.fetchone()[0])
						newPop = pop + cost
						
						if (newPop > 5000):
							c.execute('SELECT buy_multiplier FROM Shop WHERE item = "'+item+'" AND area = "'+area+'"')
							newPrice = float(c.fetchone()[0]) + 0.05
							print(newPrice)
							c.execute('UPDATE Shop SET buy_multiplier = '+str(newPrice)+' WHERE item = "'+item+'"')
				
							#reset the inflation counter
							newPop = newPop - 5000
						#c.execute('UPDATE Demand SET popularity = '+str(newPop)+' WHERE item = "'+item+'"')
					except:
						print('route popularity not updated')
					conn.commit()
					await ctx.send('Successfully purchased '+str(amt) +' '+item)
				else:
					await ctx.send('Alright calm down there Mr. Trump. We aint all as cash money as you. We only got '+str(shopStock)+' of those')
			else:
				await ctx.send("Stop it Onii-chan~~ there's no way all of it can fit!!")
			
			
		else:
			await ctx.send('Whatchu tryin to pull here. Get yo poor lookin ass outta my face')
	except Exception as e:
		print(e)

@client.command(pass_context = True)
@commands.cooldown(1, 2, commands.BucketType.user)
async def sell(ctx, *argv):
	if(not created(str(ctx.message.author.id))):
		await ctx.send("You don't even exist. You mean literally nothing to me. Use !create first to bring meaning to your life")	
		return
	try:
		jailed = jailCheck(str(ctx.message.author.id))
		if(jailed):
			await ctx.send(jailed)
			return
		item = False
		amt = False
		quality = False
		
		#check input
		for value in argv:
			try:
				if(amt):
					quality = int(value)
				else:
					amt = int(value)
			except:
				if(item):
					item += " " + value.lower()
				else:
					item = value.lower()
		
		
		if(item):
			if(not amt):
				await ctx.send('How much '+item+' would you like to sell?')
				response = await client.wait_for('message', check=lambda m: m.author==ctx.message.author and m.channel==ctx.message.channel, timeout= 7)
				if (response):
					try:
						amt = int(response.content)
					except:
						await ctx.send('That is not a number')
						return
				else:
					await ctx.send("It's not like I wanted you to answer or anything b-b-b-baka")
					return
			
			c.execute('SELECT id FROM Wagons WHERE owner = "'+str(ctx.message.author.id)+'" AND rider = "'+str(ctx.message.author.id)+'"')
			wagon = c.fetchone()[0]
			
			if(not quality):
				
				
				#check to see if there are items with multiplie qualities
				c.execute('SELECT item, stock, quality FROM WagonInventory WHERE wagon = ' + str(wagon)+' AND item = "'+item+'"')   
				table = from_db_cursor(c)
				if(len(table._rows)>1):
					await ctx.send('You posses '+item+' of different qualities:\n```'+table.get_string() + '```\nPlease specify which quality of '+item+' you which to sell (Just type the number below):')
					response = await client.wait_for('message', check=lambda m: m.author==ctx.message.author and m.channel==ctx.message.channel, timeout= 7)
					if response:
						try:
							c.execute('SELECT quality FROM WagonInventory WHERE item = "'+item+'" AND quality = '+str(response.content)+' AND wagon = '+str(wagon))
							quality = c.fetchone()[0]
							
						except Except as e:
							await ctx.send('You do not own a '+item+' with a quality of '+str(response.content))
							return
					else:
						await ctx.send('You did not respond in time')
						return
				else:
					c.execute('SELECT quality FROM WagonInventory WHERE item = "'+item+'" AND wagon = '+str(wagon))
					quality = c.fetchone()[0]
			else:
				try:
					#select the quality if the quality is unique
					c.execute('SELECT quality FROM WagonInventory WHERE item = "'+item+'" AND wagon = '+str(wagon))
					quality = c.fetchone()[0]
				except:
					await ctx.send("You do not own an item of that name or of that quality.\nUse !inventory to find out what you own")
					return
			
			#get the amount of the item the player actually owns
			try:
				c.execute('SELECT stock FROM WagonInventory WHERE item = "'+item+'" AND wagon = '+str(wagon)+' AND quality = '+str(quality))
				stock = int(c.fetchone()[0])
			except:
				await ctx.send("You do not own an item of that name or of that quality.\nUse !inventory to find out what you own")
				return
			if (amt <= 0):
				await ctx.send('Please enter an amount greater than 0')

			if(amt <= stock):
				
				#calculate sell price
				c.execute('SELECT base_price FROM Items WHERE item = "' + item +'"')
				price = c.fetchone()[0]
				
				c.execute('SELECT area FROM characters WHERE id = "'+str(ctx.message.author.id)+'"')
				area = c.fetchone()[0]
				try:
					c.execute('SELECT sell_multiplier FROM DEMAND WHERE item = "'+ item +'" AND area = "' + area +'"')
					mult = c.fetchone()[0]
					
				except:
					mult = 1

				try:
					c.execute('SELECT quality_multiplier FROM DEMAND WHERE ITEM = "'+ item +'" AND area = "'+ area +'"')
					mult2 = c.fetchone()[0]
								
					qualityMult = mult2 -1
				except:
					qualityMult = 1
					
				print(mult)
				print(qualityMult)
				qualityPay = math.floor(qualityMult * quality)
				demandPay = math.floor((mult * price) - price)
				pricePer = math.floor(qualityPay + demandPay + price)
				#total money received for the sale
				saleTotal = math.floor(pricePer * amt)
				
				await ctx.send('You are offered '+str(pricePer)+' for each ' +str(item)+' for a total of '+str(saleTotal)+'\n Would you like to accept this offer? (y/n)')
				response = await client.wait_for('message', check=lambda m: m.author==ctx.message.author and m.channel==ctx.message.channel, timeout= 7)
				if response:
					if (response.content == 'y'):
						#Update player money
						c.execute('SELECT stock FROM Inventory WHERE owner = "'+str(ctx.message.author.id)+'" AND item = "money"')
						money = c.fetchone()[0]
						newBank = money + saleTotal
						
						try:
							c.execute('UPDATE Inventory SET stock = '+str(newBank)+' WHERE owner = "'+str(ctx.message.author.id)+'" AND item = "money"')
						except:
							await ctx.send('Player money not updated, item selling aborted')
							return
						
						#update player inventory

						
						try:
							newStock = stock - amt
							
							if(newStock == 0):
								c.execute('DELETE FROM WagonInventory WHERE item = "'+str(item)+'" AND quality = '+str(quality)+' AND wagon = '+str(wagon))
							else:	
								c.execute('UPDATE WagonInventory SET stock = '+str(newStock)+' WHERE item = "'+str(item)+'" AND quality = '+str(quality)+' AND wagon = '+str(wagon))
						except:
							await ctx.send('Error selling item')
							print('player inventory not updated')
							return
						
						#global stock update
						try:
							c.execute('SELECT stock FROM Items WHERE item = "'+item+'"')
							oldStock = int(c.fetchone()[0])
							newStock = oldStock - amt
							c.execute('UPDATE Items SET stock = '+str(newStock)+' WHERE item = "'+item+'"')
						except:
							print('global stock not updated')
						
						#global.popularity update
						try:
							c.execute('SELECT popularity FROM Items WHERE item = "'+item+'"')
							popularity = int(c.fetchone()[0])
							newPopularity = popularity + saleTotal
							c.execute('UPDATE Items SET popularity = '+str(newPopularity)+' WHERE item = "'+item+'"')
							inflationCheck(item, newPopularity)
						except:
							print('global popularity not updated')
						
						#update city modifer
						try:
							c.execute('SELECT popularity FROM Demand WHERE item = "'+item+'" AND area = "'+area+'"')
							pop = int(c.fetchone()[0])
							newPop = pop + saleTotal
							
							if (newPop > 5000):
								c.execute('SELECT sell_multiplier FROM Demand WHERE item = "'+item+'" AND area = "'+area+'"')
								newPrice = float(c.fetchone()[0]) - 0.1
								c.execute('UPDATE Demand SET sell_multiplier = '+str(newPrice)+' WHERE item = "'+item+'"')
					
								#reset the inflation counter
								newPop = newPop - 5000
							c.execute('UPDATE Demand SET popularity = '+str(newPop)+' WHERE item = "'+item+'"')
						except:
							print('route popularity not updated')
							
						conn.commit()
						await ctx.send('Successfully sold '+str(amt) +' '+item+' for '+str(saleTotal))
					elif (response.content == 'n'):
						await ctx.send('Yeah that guy was totally trying to rip you off')
					else:
						await ctx.send('Could not compute answer')
				else:
					await ctx.send('You did not respond in time and the shopkeeper forcibly shooes you away from his storefront')
			else:
				await ctx.send("Okay let's try to sell an amount you actually have")
		else:
			await ctx.send("Please input the items in the following order: \n item name --> amount you wish to sell of said item\n Example: ```!sell shrimp 100 42```")
	except Exception as e:
		print(e)


@client.command(aliases=['i'], brief = 'Displays your inventory', Description = 'Displays all items that are in your inventory as well as your wagon. Your money is displayed at the top', pass_context = True)
@commands.cooldown(1, 2, commands.BucketType.user)
async def inventory(ctx):
	if(not created(str(ctx.message.author.id))):
		await ctx.send("You don't even exist. You mean literally nothing to me. Use !create first to bring meaning to your life")	
		return
	c.execute('SELECT id FROM Wagons WHERE owner = "'+str(ctx.message.author.id)+'" AND rider = "'+str(ctx.message.author.id)+'"')
	wagon = c.fetchone()[0]

	c.execute('SELECT item, stock, quality FROM WagonInventory WHERE wagon = ' + str(wagon))   
	table = from_db_cursor(c)

	c.execute('SELECT stock FROM Inventory WHERE item = "money" AND owner = "'+str(ctx.message.author.id)+'"')
	money = c.fetchone()[0]


	await ctx.send('```Money: '+str(money)+'\n'+table.get_string()+ '```')

	
	
@client.command(brief = 'Shows what you can purchase from your current area', description = 'Shows what you can purchase from your current area', help = 'Shops are specific to the AREA. What you can buy could differ from area to area in the same city', pass_context = True)
@commands.cooldown(1, 2, commands.BucketType.user)
async def shop(ctx):
	if(not created(str(ctx.message.author.id))):
		await ctx.send("You don't even exist. You mean literally nothing to me. Use !create first to bring meaning to your life")	
		return
	c.execute('SELECT area FROM Characters WHERE id = ' + str(ctx.message.author.id))
	area = c.fetchone()[0]
	c.execute('SELECT item, quality, stock FROM Shop WHERE area = "' + area +'"')   
	table = PrettyTable()
	table.field_names = ["item", "price", "quality", "stock"]
	x = c.fetchall()
	for row in x:
		if(row[2] == 0):
			row = (row[0], 'X', 'X', 'SOLD OUT')
			table.add_row(row)
		else:
			price = getPrice(row[0], area)
			row = (row[0], int(price), row[1], row[2])
			table.add_row(row)
	await ctx.send('```' +table.get_string()+ '```')
	
    
	
@client.command(brief = 'Creates you character', description = 'Makes a character tied to your discord account', pass_context = True)
@commands.cooldown(1, 2, commands.BucketType.user)
async def create(ctx):
	try:
		c.execute('INSERT INTO Characters(id, currentCity, previousCity, area) VALUES ("'+str(ctx.message.author.id)+'", "lumbridge", "lumbridge", "lumbridge_market square")')
		c.execute('INSERT INTO Inventory(item, stock, owner, quality) VALUES("money", 500, "'+str(ctx.message.author.id)+'", 1)')
		c.execute('INSERT INTO Wagons(size, owner, rider, speed) VALUES (200, "'+str(ctx.message.author.id)+'", "'+str(ctx.message.author.id)+'", 1)')
		c.execute('INSERT INTO Status(player, playerState) VALUES("'+str(ctx.message.author.id)+'", "idle")')
		conn.commit()
		await ctx.send('Welcome to (insert name here)! Here are your basic commands to get you started:\n```!help - Shows a list of commands and brief description of each\n!helpa - lists all the commands you can use in a designated area\n!travel - travel to a different city(travel time required)\n!goto - move to a different area in the same city (no travel time required)\n!status - Displays your current status and location```')
	except:
		await ctx.send('One of you in this world is more than enough')
	
	

@client.command(aliases=['go', 'g'], brief = 'Move to a different area', description = 'Using !goto displays the areas you can go at your present location, no travel time required to move areas.', pass_context = True)
@commands.cooldown(1, 2, commands.BucketType.user)
async def goto(ctx, *argv):
	if(not created(str(ctx.message.author.id))):
		await ctx.send("You don't even exist. You mean literally nothing to me. Use !create first to bring meaning to your life")	
		return
	jailed = jailCheck(str(ctx.message.author.id))
	if(jailed):
		await ctx.send(jailed)
		return
	# if travel._buckets.valid:
		# travelling = travel._buckets.get_bucket(ctx).is_rate_limited()
	# if travelling:
		# await ctx.send ("`" +formatTime(travelling) + "` until you arrive at " + loc.capitalize())
		# return
	c.execute('SELECT currentCity FROM Characters WHERE id = '+str(ctx.message.author.id))
	loc = c.fetchone()[0]
	
	c.execute('SELECT area FROM Characters WHERE id = "'+str(ctx.message.author.id)+'"')
	area = c.fetchone()[0]

	#If you need to move from the front gate
	if area == loc + "_front gate":
		await ctx.send('You have arrived at ' + loc.capitalize() + '\n Would you like to enter through the Front Gate? (y/n)')
		response = await client.wait_for('message', check=lambda m: m.author==ctx.message.author and m.channel==ctx.message.channel, timeout=10)
		if response:
			if response.content == "y":
				#tax
				illegal = isIllegal(str(ctx.message.author.id))
				if(illegal):
					await ctx.send('*The guards promptly bind, gag, and blindfold you after confiscating your illegal goods and whisper "You need the fear of god instilled in you" as they drag you into the darkness*\n\n.... Did you really just try to stroll through the front gate with '+illegal[0].capitalize()+'?')
					jail(str(ctx.message.author.id), 120)
				else:	
					taxPrint = taxHelper(str(ctx.message.author.id), "check")
					if(taxPrint):
						await ctx.send(taxPrint + '\nYou enter '+ loc.capitalize() +' through the Front Gate')
						c.execute('UPDATE characters SET area = "'+ loc +'_market square" WHERE id = '+str(ctx.message.author.id))
					else:
						await ctx.send("*You are away swiftly dragged from the gate kicking and screaming as your complaints of taxation without representation fall upon deaf ears*\n Use !tax to see a breakdown of how much tax you owe")
		
			elif response.content == "n":
				await ctx.send('You circle around the castle and spot some people going in through what looks like another gate. Would you like to try your luck here? (y/n)')
				response2 = await client.wait_for('message', check=lambda m: m.author==ctx.message.author and m.channel==ctx.message.channel, timeout=10)
				if response2:
					if response2.content == "y":
						bribePrint = bribe(str(ctx.message.author.id))
						if(bribePrint):
							await ctx.send(bribePrint)
							c.execute('UPDATE characters SET area = "'+ loc +'_market square" WHERE id = '+str(ctx.message.author.id))
						else:
							await ctx.send("*The guard looks at the meager offerings you present him in disgust, snatches it all away and kicks you to the curb*")
					
					elif response2.content == "n":
						await ctx.send('WTF what you wanna do then.\n Use !status when you make up your damn mind')
					else:
						await ctx.send("Sorry I'm too BAKA to understand what you're saying")
				elif response2 is None:
					await ctx.send('You did not answer in time. Use !status again when you are ready to enter the city')
			else:
				await ctx.send("Sorry I'm too BAKA to understand what you're saying")
			
			travel.reset_cooldown(ctx)
			c.execute('UPDATE characters SET previousCity = "'+loc+'" WHERE id = "'+ str(ctx.message.author.id) +'"')
			conn.commit()
		elif response is None:
			await ctx.send('You did not answer in time. Use !status again when you are ready to enter the city')
			travel.reset_cooldown(ctx)
	
	else:
		
		#area not provided
		if len(argv) < 1:
			c.execute('SELECT area FROM Characters WHERE id = "'+str(ctx.message.author.id)+'"')
			currentArea = c.fetchone()[0]
			c.execute('SELECT area FROM Areas WHERE city = "'+loc+'"')
			result = c.fetchall()
			indent = len(loc) + 1
			x = ""
			for row in result:
				if (row[0] != currentArea):
					x += row[0][indent:].capitalize() + "\n"
			await ctx.send("Areas you can go to:```\n" + x + "```\n\n Please type the city name you would like to travel to after the command:\n ```!goto market square```")
			return
		
		#area is provided
		else:
			temp = ''
			for value in argv:
				if temp == '':
					temp += value
				else:
					temp += " " + value
			areaFull = (loc + '_' + temp).lower()
			print(areaFull)
			if checkArea(areaFull):
				await ctx.send('You have moved to ' + areaFull)
				c.execute('UPDATE characters SET area = "'+ areaFull +'" WHERE id = '+str(ctx.message.author.id))
				conn.commit()
			else:
				await ctx.send('Nice try guy ' + temp + ' is not a real area in '+ loc.capitalize())

	travel.reset_cooldown(ctx)
@client.command(aliases=['s'], brief = 'Display the current status of your character', description = 'Not Travelling: Displays your current location (City and area)\nTravelling: Will display the time until arrival at destination', pass_context = True)
@commands.cooldown(1, 2, commands.BucketType.user)
async def status(ctx):
	try:
		if(not created(str(ctx.message.author.id))):
			await ctx.send("You don't even exist. You mean literally nothing to me. Use !create first to bring meaning to your life")
			return
		jailed = jailCheck(str(ctx.message.author.id))
		if(jailed):
			await ctx.send(jailed)
			return
		# travelling = 0
		# loc = getCharacterLocation(str(ctx.message.author.id))
		# if travel._buckets.valid:
			# travelling = travel._buckets.get_bucket(ctx).is_rate_limited()
		# if travelling:
			# await ctx.send ("`" +formatTime(travelling) + "` until you arrive at " + loc.capitalize())
			# return
		else:
			loc = getCharacterLocation(str(ctx.message.author.id))
			c.execute('SELECT area FROM Characters WHERE id = '+str(ctx.message.author.id))
			area = c.fetchone()[0]
			c.execute('UPDATE characters SET previousCity = "'+loc+'" WHERE id = "'+ str(ctx.message.author.id) +'"')
			conn.commit()
			
			#if you need to enter a city
			if area == loc + "_front gate":
				await ctx.send('You have arrived at ' + loc.capitalize() + '\n Would you like to enter through the Front Gate? (y/n)')
				response = await client.wait_for('message', check=lambda m: m.author==ctx.message.author and m.channel==ctx.message.channel, timeout=10)
				if response:
					if response.content == "y":
						#tax
						illegal = isIllegal(str(ctx.message.author.id))
						if(illegal):
							await ctx.send('*The guards promptly bind, gag, and blindfold you and whisper "You need the fear of god instilled in you" as they drag you into the darkness*\n\n.... Did you really just try to stroll through the front gate with '+illegal[0].capitalize()+'?')
							jail(str(ctx.message.author.id), 120, illegal)
						else:	
							taxPrint = taxHelper(str(ctx.message.author.id), "check")
							if(taxPrint):
								await ctx.send(taxPrint + '\nYou enter '+ loc.capitalize() +' through the Front Gate')
								c.execute('UPDATE characters SET area = "'+ loc +'_market square" WHERE id = '+str(ctx.message.author.id))
							else:
								await ctx.send("*You are away swiftly dragged from the gate kicking and screaming as your complaints of taxation without representation fall upon deaf ears*\n Use !tax to see a breakdown of how much tax you owe")
				
					elif response.content == "n":
						await ctx.send('You circle around the castle and spot some people going in through what looks like another gate. Would you like to try your luck here? (y/n)')
						response2 = await client.wait_for('message', check=lambda m: m.author==ctx.message.author and m.channel==ctx.message.channel, timeout=10)
						if response2:
							if response2.content == "y":
								bribePrint = bribe(str(ctx.message.author.id))
								if(bribePrint):
									await ctx.send(bribePrint)
									c.execute('UPDATE characters SET area = "'+ loc +'_market square" WHERE id = '+str(ctx.message.author.id))
								else:
									await ctx.send("*The guard looks at the meager offerings you present him in disgust, snatches it all away and kicks you to the curb*")
							
							elif response2.content == "n":
								await ctx.send('WTF what you wanna do then.\n Use !status when you make up your damn mind')
							else:
								await ctx.send("Sorry I'm too BAKA to understand what you're saying")
						elif response2 is None:
							await ctx.send('You did not answer in time. Use !status again when you are ready to enter the city')
					else:
						await ctx.send("Sorry I'm too BAKA to understand what you're saying")
					
					travel.reset_cooldown(ctx)
					c.execute('UPDATE characters SET previousCity = "'+loc+'" WHERE id = "'+ str(ctx.message.author.id) +'"')
					conn.commit()
				elif response is None:
					await ctx.send('You did not answer in time. Use !status again when you are ready to enter the city')
					travel.reset_cooldown(ctx)
			else:
				await ctx.send('You are current at '+ area.capitalize() +' \n Use !goto to move to a different area')
	except Exception as e:
		print(e)
		traceback.print_exc()
@client.command(brief = 'See a breakdown of the taxes you need to pay', description = 'This shows a breakdown of the taxes you will need to pay to enter the city you are currently at broken down per item.', pass_context = True)
@commands.cooldown(1, 2, commands.BucketType.user)
async def tax(ctx):
	if(not created(str(ctx.message.author.id))):
		await ctx.send("You don't even exist. You mean literally nothing to me. Use !create first to bring meaning to your life")
		return
	try:
		taxPrint = taxHelper(str(ctx.message.author.id), "list")
		if(isinstance(taxPrint, str)):
			await ctx.send(taxPrint)
		else:
			await ctx.send(taxPrint[1] + "\nYou don't have enough money to pay these taxes. Use !sell to pawn off some items before trying to enter the front gate")
	except Exception as e:
		print(e)
	

@client.command(brief = 'Cancel your current journey', pass_context = True)
@commands.cooldown(1, 2, commands.BucketType.user)
async def cancel(ctx):
	travelling = 0
	character = str(ctx.message.author.id)
	if travel._buckets.valid:
		travelling = travel._buckets.get_bucket(ctx).is_rate_limited()
	if travelling:

		c.execute('SELECT previousCity FROM Characters WHERE id = "'+ character+'"')
		previous = c.fetchone()[0].lower()

		try:
			c.execute('UPDATE characters SET currentCity = "'+previous+'" WHERE id = '+ character)
			c.execute('UPDATE characters SET area = "'+previous+'_front gate" WHERE id =' + character)
		except Exception as e:
			print(e)
		conn.commit()
		travel.reset_cooldown(ctx)
		await ctx.send ("You turn around and head back to " + previous.capitalize())
		return
	else:
		await ctx.send("You are not currently travelling")
		return


@client.command(aliases = ['t'], brief = 'Travel to other cities', description = '!travel to see a list of cities you can travel to', help = 'Use !cancel to cancel your current journey', pass_context = True)
@commands.cooldown(1, 2, commands.BucketType.user)
async def travel(ctx, *city):
	if(not created(str(ctx.message.author.id))):
		await ctx.send("You don't even exist. You mean literally nothing to me. Use !create first to bring meaning to your life")
		return
	jailed = jailCheck(str(ctx.message.author.id))
	if(jailed):
		await ctx.send(jailed)
		return
	character = str(ctx.message.author.id)
	
	#city not provided
	if len(city) < 1:
		c.execute('SELECT currentCity FROM Characters WHERE id = "' +str(ctx.message.author.id)+'"')
		currentCity = c.fetchone()[0]
		c.execute('SELECT name, hidden FROM Cities')
		result = c.fetchall()
		x = ""
		for row in result:
			if (row[0] != currentCity):
				if(cityFound(row[0], str(ctx.message.author.id))):
					c.execute('SELECT speed FROM Wagons WHERE rider = "'+character+'"')
					wagonspeed = int(c.fetchone()[0])
					dest = getCityLocation(row[0])
					start = getCityLocation(currentCity)
					dist = distance(dest, start, wagonspeed)
					x += row[0].capitalize() + " - "+formatTime(dist)+"\n"
				
		await ctx.send("Cities you can travel to:```\n" + x + "```\n\n Please type the city name you would like to travel to after the command:\n ```!travel Lumbridge```")
		return
	
	#city provided
	else:		
		temp = ''
		for value in city:
			if temp == '':
				temp += value
			else:
				temp += " " + value
		destination = temp.lower()
	if (not cityFound(destination, str(ctx.message.author.id))):
		await ctx.send('*You have heard stories of '+destination.capitalize()+', but does such a land even really exist?*')
		return
	c.execute('SELECT speed FROM Wagons WHERE rider = "'+character+'"')
	wagonspeed = int(c.fetchone()[0])
	dest = getCityLocation(destination)

	if (isinstance(dest, bool)):
		await ctx.send(destination + " does not exist. Nice try.")
		return
	
	current = getCharacterLocation(character)
	c.execute('UPDATE characters SET previousCity = "'+current+'" WHERE id = "'+ character +'"')
	if (isinstance(current, bool)):
		await ctx.send("You're not even real. Nice try. If you would like to exist, please create a character")
		return

	c.execute('UPDATE characters SET currentCity = "'+destination+'" WHERE id = "'+ str(character) +'"')

	start = getCityLocation(current)
	dist = distance(dest, start, wagonspeed)

	#Set the Cooldown
	if ctx.command._buckets.valid:
		bucket = travel._buckets.get_bucket(ctx)
		bucket.per = dist

	c.execute('UPDATE characters SET area = "'+ destination +'_front gate" WHERE id = '+character)
	conn.commit()
	await ctx.send("Traveling to " + destination.capitalize() + " in `" + formatTime(dist)+"`")
	client.loop.create_task(travelEvents(ctx))

@client.event
async def on_command_error(error, ctx, *argv):
	if (isinstance(error, commands.CommandOnCooldown)):
		msg = "This command is on cooldown for you, maybe if you could wait **" + str(round(error.retry_after, 2)) + "** seconds for once in your damn life we wouldn't need to go over this"
		await client.send_message(ctx.message.channel, msg)

async def shopStockUpdate():
	while(True):
		print('GlobalUpdate loop initialized')
		await asyncio.sleep(86400)
		c.execute('SELECT * FROM ReStock')
		restock = c.fetchall()
		for value in restock:
			item = value[0]
			area = value[1]
			amount = value[2]
			base_quality = value[3]
			
			amt_mult =  random.randint(-25, 25)
			amt_mult = amt_mult * .01
			amount = amount + (amount * amt_mult)
			
			quality_mult = random.randint(-75, 75)
			quality_mult = quality_mult * .01
			quality = base_quality + (base_quality * quality_mult)  
			
			try:
				c.execute('SELECT stock FROM Shop WHERE item = "'+item+'" AND area = "'+area+'"')
				stock = c.fetchone()[0]
				newStock = stock + amount
				c.execute('UPDATE Shop SET stock = '+str(newStock)+' AND quality = '+str(quality)+' WHERE item = "'+item+'" AND area = "'+area+'"')
			except:
				try:
					c.execute('INSERT INTO Shop(area, item, quality, stock, buy_multiplier) VALUES("'+area+'", "'+item+'", '+str(quality)+', '+str(stock)+', 1')
				except:
					print('failed to restock '+item)
		
		

	return
		
async def travelEvents(ctx):
	if travel._buckets.valid:
		travelling = travel._buckets.get_bucket(ctx).is_rate_limited()
	while(travelling):
		x = random.randint(1, 300)
		if (x ==1):
			await client.send_message(ctx.message.channel, 'Random wolf girl appears!')
			response = await client.wait_for('message', check=lambda m: m.author==ctx.message.author and m.channel==ctx.message.channel, timeout=10)
			if (response):
				await client.send_message(ctx.message.channel, 'Wolf girl claimed!')
			else:
				await client.send_message(ctx.message.channel, 'Wolf girl unclaimed')
		#elif(x ==
		await asyncio.sleep(60)
		
		#check travel cooldown before looping again
		if travel._buckets.valid:
			travelling = travel._buckets.get_bucket(ctx).is_rate_limited()
	
	#reconcile calling travel after cooldown
	travel.reset_cooldown(ctx)
	return

def created(charName):
	c.execute('SELECT * FROM characters WHERE id = "'+charName+'"')
	test = c.fetchone()[0]
	if len(test) == 0:
		return False
	else:
		return True

		
def cityFound(city, charName):
	c.execute('SELECT hidden FROM cities WHERE name = "'+city+'"')
	hiddenCities = c.fetchone()[0]
	found = False
	if(hiddenCities):
		c.execute('SELECT city FROM citiesfound WHERE character ="'+charName+'"')
		cities = c.fetchall()
		for value in cities:
			if(value[0] == city):
				found = True
			
	else:
		found = True

	
	return found

	
def locationisStables(charName):
	c.execute('SELECT area FROM Characters WHERE id = "'+str(charName)+'"')
	location = c.fetchone()[0]
	area = location.split('_')[-1]
	
	if(area == 'stables'):
		return(True)
	else:
		return(False)
	
def jail(criminal, jailtime, illegalItems):
	current = int(time.time())
	try:
		c.execute('SELECT currentCity FROM Characters WHERE id = "'+criminal+'"')
		city = c.fetchone()[0]
		
		c.execute('SELECT id FROM Wagons WHERE owner = "'+criminal+'" AND rider = "'+criminal+'"')
		wagon = c.fetchone()[0]
		for value in illegalItems:
			c.execute('DELETE FROM WagonInventory WHERE item = "'+value+'" AND wagon = '+str(wagon))
		c.execute('INSERT INTO Jail(crime, criminal, start, jailtime) VALUES("loli trafficking", "'+criminal+'", '+str(current)+', '+str(jailtime)+')')
		c.execute('UPDATE characters SET area = "'+city+'_jail" WHERE id = "'+criminal+'"')
		conn.commit()
	except Exception as e:
		print(e)

def jailCheck(criminal):
	current = int(time.time())
	try:
		c.execute('SELECT start FROM jail WHERE criminal = "'+criminal+'"')
		start = c.fetchone()[0]
		
		
		c.execute('SELECT jailtime FROM jail WHERE criminal = "'+criminal+'"')
		jailTime = c.fetchone()[0]
		
		timeJailed = current - start
		
		if(timeJailed < jailTime):
			timeLeft = jailTime - timeJailed
			return('You are in jail for another `'+formatTime(timeLeft)+"`")
		else:
			c.execute('DELETE FROM Jail WHERE criminal = "'+criminal+'"')
			return('You have served your time. You have fully repented and are ready to start down a righteous path led by your fear of God\n\n .... or so they think')
	except:
		return(False)

		
def bribe(charName):
	c.execute('SELECT currentCity FROM Characters WHERE id = "'+charName+'"')
	city = c.fetchone()[0]
	
	c.execute('SELECT bribe FROM Cities WHERE name = "'+city+'"')
	bribe = c.fetchone()[0]
	
	c.execute('SELECT stock FROM inventory WHERE owner = "'+charName+'"')
	money = c.fetchone()[0]
	
	if(money >= bribe):
	
		newBank = money - bribe
		try:
			c.execute('UPDATE inventory SET stock = '+str(bribe)+' WHERE owner = "'+charName+'"')
		except:
			print('player money not updated')
		
		return("You slip the guard a pouch with "+str(bribe)+" in it and enter "+city.capitalize())
	else:
		try:
			c.execute('UPDATE inventory SET stock = 0 WHERE owner = "'+charName+'"')
		except:
			print('player money not updated')
		return(False)


def isIllegal(charName):
	c.execute('SELECT id FROM Wagons WHERE owner = "'+charName+'" AND rider = "'+charName+'"')
	wagon = c.fetchone()[0]
	
	c.execute('SELECT item FROM WagonInventory WHERE wagon = '+str(wagon))
	itemList = c.fetchall()
	returnValue = []
	for entry in itemList:
		item = entry[0]
		c.execute('SELECT legal FROM Items WHERE item = "'+item+'"')
		legal = c.fetchone()[0]
		if(legal == 0):
			returnValue.append(item)
	
	return(returnValue)
		
def formatTime(time):
	seconds = time
	hours = seconds // (60*60)
	seconds %= (60*60)
	minutes = seconds // 60
	seconds %= 60

	if (hours ==0):
		if (minutes==0):
			return("%02i seconds" % (seconds))
		else:
			return("%i:%02i" % (minutes, seconds))
	else:
		return("%i:%02i:%02i" % (hours, minutes, seconds))
	
	
def taxHelper(charName, mode):

	returnString = 'Taxes charged:```'
	
	c.execute('SELECT id FROM Wagons WHERE owner = "'+charName+'" AND rider = "'+charName+'"')
	wagon = c.fetchone()[0]
	
	c.execute('SELECT item FROM WagonInventory WHERE wagon = '+str(wagon))
	itemList = c.fetchall()
	
	totalTax = 0
	for entry in itemList:
		item = entry[0]
		c.execute('SELECT base_price FROM items WHERE item = "'+item+'"')
		price = c.fetchone()[0]
		
		c.execute('SELECT stock FROM WagonInventory WHERE item = "'+item+'" AND wagon = '+str(wagon))
		temp = c.fetchall()
		stock = 0
		for x in temp:
			stock += x[0]
		total = price * stock
		
		c.execute('SELECT currentCity FROM Characters WHERE id = "'+charName+'"')
		city = c.fetchone()[0]
		
		c.execute('SELECT tax FROM Cities WHERE name = "'+city+'"')
		taxRate = c.fetchone()[0]
		
		tax = math.ceil(total * taxRate)
		
		totalTax += tax	
		
		returnString += str(tax)+" for "+item+"\n"

	returnString += "\nTotal tax due: "+str(totalTax)+"\n"

	
	returnString += '```'
	c.execute('SELECT stock FROM Inventory WHERE item = "money" AND owner = "'+charName+'"')
	money = c.fetchone()[0]
	
	if (money >= totalTax):
		if(mode == "check"):
			afterTax = money - totalTax
			try:
				c.execute('UPDATE Inventory SET stock = '+str(afterTax)+' WHERE item = "money" AND owner = "'+charName+'"')
			except:
				print('player money not updated')
	else:
		if(mode == 'check'):
			returnString = False
		elif(mode == 'list'):
			return(False, returnString)
		

	return(returnString)
	
		
#returns the available space in the wagon		
def wagonSpace(charName):
	c.execute('SELECT id FROM Wagons WHERE owner = "'+charName+'" AND rider = "'+charName+'"')
	wagon = c.fetchone()[0]
	c.execute('SELECT size FROM Wagons WHERE id = '+str(wagon))
	maxSize = c.fetchone()[0]
	spaceTaken = 0
	c.execute('SELECT item FROM WagonInventory WHERE wagon = "'+str(wagon)+'"')
	result = c.fetchall()
	for row in result:
		current = row[0]
		c.execute('SELECT size FROM items WHERE item = "'+current+'"')
		temp = int(c.fetchone()[0])
		c.execute('SELECT stock FROM WagonInventory WHERE item = "'+current+'" AND wagon = '+str(wagon))
		temp2 = int(c.fetchone()[0])
		
		itemSpace = temp * temp2
		
		
		spaceTaken += itemSpace
		
	return(maxSize - spaceTaken)
		
def getPrice(item, area):
	c.execute('SELECT base_price FROM Items WHERE item = "' + item +'"')
	price = c.fetchone()[0]
	try:
		c.execute('SELECT buy_multiplier FROM Shop WHERE item = "'+ item +'" AND area = "' + area +'"')
		mult = c.fetchone()[0]
		price = price * mult
	except:
		pass

	return(price)
		
def checkArea(area):
	try:
		c.execute('SELECT area FROM Areas WHERE area = "' + area +'"')
		x = c.fetchone()[0]
		return(x)
	except:
		return(False)

def inflationCheck(item, popularity):
	if (popularity >= 5000):
		c.execute('SELECT base_price FROM Items WHERE item = "'+item+'"')
		newPrice = c.fetchone()[0] + 1
		c.execute('UPDATE Items SET base_price = '+newPrice+' WHERE item = "'+item+'"')
		popularity = popularity - 5000
		#reset the inflation counter
		c.execute('UPDATE Items SET popularity = '+popularity+' WHERE item = "'+item+'"')
		conn.commit()
	else:
		return
	
def switch(message):
	
	command = message.content[2:]
	commander = message.author.id
	
	
	if command[:6] == "travel":
		return(travel(command[7:], commander))
	elif command[:6] == "create":
		createCharacter(commander)
		return('Successfully created a character for {0.author.mention}'.format(message))
	else:
		return("Sorry, I'm too Baka to understand that command, please use i/help to figure out what I do understand")
	


def distance(location1, location2, wagonspeed):
	x = location1[0] - location2[0]
	y = location1[1] - location2[1]
	dist = math.sqrt((x*x) + (y*y))/wagonspeed
	
	return dist
	
def getCharacterLocation(charName):
	c.execute('SELECT currentCity FROM Characters WHERE id = "'+ charName +'"')
	try:
		x = c.fetchone()[0]

	except:
		return(False)
	return x

def getCityLocation(cityName):
	try:
		c.execute('SELECT location_x FROM Cities WHERE name = "'+ cityName +'"')
		x = int(c.fetchone()[0])

		c.execute('SELECT location_y FROM Cities WHERE name = "'+ cityName +'"')
		y = int(c.fetchone()[0])
		return (x,y)
	except:
		return False
	

extensions = ['gambling', 'playershop', 'fishing', 'cooking', 'farming']
if __name__ == '__main__':
    for extension in extensions:
        try:
            client.load_extension(extension)
            print('Loaded extension: {}'.format(extension))
        except Exception as error:
            print('{} cannot be loaded. [{}]'.format(extension, error))
	
client.run(config.TOKEN)