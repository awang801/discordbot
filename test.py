import math
import sqlite3
import random
import asyncio
import mal
from myanimelist.session import Session
from prettytable import PrettyTable
from prettytable import from_db_cursor

mal = Session()
conn = sqlite3.connect('data.db')
c = conn.cursor()


tension = 0

def main():
	steps = []
	for x in range(1, 4):
		steps.append(['cut', x])
	print(len(steps))
	
def changeTension():
	global tension
	tension += 5
	print(tension)
def reStockDef():
	c.execute('SELECT item, area, quality FROM Shop')
	fields = c.fetchall()
	
	for value in fields:
		try:
			c.execute('INSERT INTO ReStock(item, area, base_quality) VALUES("'+value[0]+'", "'+value[1]+'", '+str(value[2])+')')
		except Exception as e:
			print(e)
	conn.commit()
def locationCheck():
	try:
		c.execute('SELECT shopColumns FROM Preferences WHERE character = "SmallWeeb"')
		tuple = c.fetchone()[0]
		print(tuple)
		print(tuple[0])
	except Exception as e:
		print(e)
def newCommonArea():
	c.execute('SELECT name FROM cities')
	cities = c.fetchall()
	
	for value in cities:
		print(value)
		c.execute('INSERT INTO AREAS(area, city) VALUES("'+value[0]+'_grand market", "'+value[0]+'")')
	conn.commit()
	
async def background_loop():

	end = 0
	print('loop started')
	while(end != 10):
		x = random.randint(1, 3)
		print(x)
		if (x ==5):
			print('Random wolf girl appears!')

		end += 1
		await asyncio.sleep(2)		
def travel(destination, currentLocation, wagonspeed):

	

	return	


def distance(location1, location2):
	x = location1[0] - location2[0]
	y = location1[1] - location2[1]
	
	
	printx = str(location1[0])

	dist = math.sqrt((x*x) + (y*y))
	printy = "test test" + str(dist)
	print(type(printy))
	print(printy)
	return dist
	
def getLocation(cityName):
	c.execute('SELECT location_x FROM Cities WHERE name = "'+ cityName +'"')
	x = int(c.fetchone()[0])
	print(c.rowcount)
	c.execute('SELECT location_y FROM Cities WHERE name = "'+ cityName +'"')
	y = int(c.fetchone()[0])
	return (x,y)
	
def createCharacter(charName):
	c.execute('INSERT INTO Character(location_x, location_y, id) VALUES (0, 0, "'+charName+'")')
	print(charName)
	conn.commit()
	return

def test(charName):
	c.execute('SELECT id FROM Wagons WHERE owner = "'+charName+'" AND rider = "'+charName+'"')
	wagon = c.fetchone()[0]
	
	c.execute('SELECT item FROM WagonInventory WHERE wagon = '+str(wagon))
	itemList = c.fetchall()
	
	totalTax = 0
	for entry in itemList:
		item = entry[0]
		c.execute('SELECT legal FROM Items WHERE item = "'+item+'"')
		legal = c.fetchone()[0]
		if(legal == 0):
			return(False)
	
	return(True)

	

#--------Execution--------#
main()

