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

class cooking(commands.Cog):
	def __init__(self, client):
		self.client = client
		self.steps  = []
	
	@commands.group(pass_context=True)
	async def cook(self, ctx):
		if ctx.invoked_subcommand is None:
			await self.client.say('Invalid cook command passed...')
		
	@cook.command(pass_context = True)
	async def cut(self, ctx, *ingredient):
		try:
			self.steps.append(['cut', ingredient[0], len(self.steps) + 1, 0])
			print(len(self.steps))
			await self.client.say('Cut '+ingredient[0])
		except Exception as e:
			print(e)
		return
		
		
def setup(client):
	client.add_cog(cooking(client))	