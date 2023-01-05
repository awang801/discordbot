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
from discord.ext import tasks, commands
import time
import youtube_dl
import mysql.connector as mysql
import traceback
from gtts import gTTS
from PIL import Image, ImageFilter, ImageDraw, ImageFont  # imports the library



class jeopardy(commands.Cog):
    def __init__(self, client):
        self.client = client
        
    @commands.command()
    async def test1(self, ctx):
        try:
            generateBoard(100)
            await ctx.send("pick a category:", file = discord.File("images/output.png"))
        except Exception as e:
            print(e)
        

async def setup(client):
	await client.add_cog(jeopardy(client))


#initializes the board    
def generateBoard(base_score):
    img = Image.open("images/blank_jeopardy_board.png")
    font = ImageFont.truetype("fonts/GogatingBookExtrabold-23dl.ttf", 75)
    draw = ImageDraw.Draw(img)
    draw.text((40,140), str(base_score), (255,255,0), font = font)
    img.save("images/output.png")
    index = 0
    img = Image.open("images/output.png")
    ddx = random.randrange(5)
    ddy = random.randrange(6)
    board = [[0,0,0,0,0,0],[0,0,0,0,0,0],[0,0,0,0,0,0],[0,0,0,0,0,0],[0,0,0,0,0,0]]
    board[ddx][ddy] = 2
    #print(board)
    for x in range(5):
        for y in range(6):
            if x ==0 and y == 0:
                continue
            else:

                #print(str(x) + "," + str(y))

                index+=1
                font = ImageFont.truetype("fonts/GogatingBookExtrabold-23dl.ttf", 75)
                draw = ImageDraw.Draw(img)
                score = base_score * (x+1)
                newX = 40 + (y*142)
                newY = 140 + (x*110)
                draw.text((newX,newY), str(score), (255,255,0), font = font)
    img.save("images/output.png")

def questionAnswered(coordinate):
    return
    
#covers one block
def cover():
    img = Image.open("images/output29.png")
    img2 = Image.open("images/blue_box.png")
    newImg = img.copy()
    newImg.paste(img2, (35, 130))
    newImg.save("images/test.png")