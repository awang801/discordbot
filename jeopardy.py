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


#defined in bot.py globally
invalidBuzzUserIds = [] 
inGame = False
teamGame = False
teams = {}
score = {}
teamCount = 0
buzzed = []
gameOver = False

class Buzzer(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None
        self.firstClickUser = None        
    
    @discord.ui.button(label="🔴 Buzzer", style=discord.ButtonStyle.blurple)
    async def buzz(self, interaction: discord.Interaction, button: discord.ui.Button):
        if (interaction.user.name not in teams.keys()):
            await interaction.response.send_message("You aren't registered to play", ephemeral = True)
            return
        if (interaction.user.name in invalidBuzzUserIds):
            await interaction.response.send_message("You can't buzz in anymore this round", ephemeral = True)
            return
        if (self.firstClickUser == None):
            self.firstClickUser = interaction.user.id
            button.disabled = True
            await interaction.response.edit_message(view=self)       
            await interaction.channel.send("<@{}>".format(self.firstClickUser) + " buzzes in!")
            
            


#sorted(footballers_goals.items(), key=lambda x:x[1])

class jeopardy(commands.Cog):
    def __init__(self, client):
        self.client = client
        
    @commands.command()
    async def test1(self, ctx):
        try:
            global inGame
            if(inGame == False):
                inGame = True
                generateBoard(100)
                while(inGame):
                    await ctx.send("pick a category:", file = discord.File("images/output.png"))
                    #gamemaster picks a category
                    input1 = input()
                    row = int(input1[0]) - 1
                    column = int(input1[1]) - 1
                    print(row)
                    print(column)
                    cover (row, column)
                    await ctx.send("pick a category:", file = discord.File("images/output.png"))
                    inGame = False
                
            else:
                await ctx.send("There is already a game in session")
        except Exception as e:
            print(e)
            
    @commands.command()
    async def score(self, ctx):
        try:
            printString = ""
            total = 0
            current = False
            teamSort = sorted(teams.items(), key=lambda x:x[1])
            for x in teamSort:
                if x[1] == 1:
                    printString += "**\nCURRENT SCORE**:\n```\n"
                    printString += "--TEAM " + str(x[1]) + "--\n"
                    current = x[1]
                    printString += (str(x[0]) + " " + str(score[x[0]]) + "\n")
                    total = score[x[0]]
                elif x[1] == current:
                    printString += str(score[x[0]])
                    total += score[x[0]]
                else:
                    current = x[1]
                    printString += "total " + str(total) + "\n"
                    printString += ('--TEAM ' + str(x[1]) + "--\n")
                    printString += (str(x[0]) + " " + str(score[x[0]]) + "\n")
                    total = score[x[0]]
            printString += "total " + str(total) + "\n"
            printString += "```"
            await ctx.send(printString)
        except Exception as e:
            print(e)
    #command to use if the first person that buzzed got it wrong (displays another buzzer)
    @commands.command()
    async def buzz(self, ctx):
        #list of user ids that should NOT be able to buzz in    
        view = Buzzer()
        await ctx.reply(view=view)

    #For testing only
    #Instead of using a command for this, just do this whenever a new question is asked
    @commands.command()
    async def resetbuzz(self, ctx):
        await ctx.reply("Cleared buzz list")

    @commands.command()
    async def add(self, ctx, user, teamNumber=0):
        try:
            user = ctx.message.mentions[0]
            if (user == None):
                await ctx.send('Need to @ someone to add')
            for key in teams:
                if (user.name == key):
                    if(teams[key] != teamNumber):
                        await ctx.send("Added <@{}> from team {} to team {}".format(user.name, teams[key], teamNumber))
                        teams[key] = teamNumber
                    else:
                        await ctx.send("User already added")

            if (teamNumber > 0):
                if (user.name not in teams.keys()):
                    teams[user.name] = teamNumber
                    score[user.name] = 0
                    await ctx.send("Added {} to team {}".format(user.name, teamNumber))
            
            if (teamNumber == 0):
                await ctx.send("Added {} to game without a team".format(user.name))
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
def cover(x, y):
    img = Image.open("images/output.png")
    img2 = Image.open("images/blue_box.png")
    newImg = img.copy()
    newX = 35 + (y*142)
    newY = 130 + (x*110)
    newImg.paste(img2, (newX, newY))
    newImg.save("images/output.png")