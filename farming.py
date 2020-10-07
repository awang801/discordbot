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


conn = sqlite3.connect('data.db')

c = conn.cursor()

class farming(commands.Cog):
	def __init__(self, client):
		self.client = client
		
		
def setup(client):
	client.add_cog(farming(client))