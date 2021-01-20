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



def main():
	try:
		os.chdir('D:/discordbot2/songs')
		filename = 'youtube-2uq34TeWEdQ-Fullmetal_Alchemist_Brotherhood_Opening_1-Again_creditless2.webm'
		filename2 = filename.split('.')
		outputFile = filename2[0] + '2.' + filename2[1]
		print(outputFile)
		subprocess.call(['ffmpeg', '-i', filename, '-t', '00:01:00.00', outputFile])
		os.remove(filename)
	except Exception as e:
		print(e)

main()