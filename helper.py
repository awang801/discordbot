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


def created(charName):
	try:
		c.execute('SELECT * FROM Character WHERE id = "'+charName+'"')
		test = c.fetchone()[0]
		return(True)
	except:
		return(False)