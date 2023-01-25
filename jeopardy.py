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
teamGame = False
teams = [[],[],[]]
playingUsers = []

class Buzzer(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None
        self.firstClickUser = None        
    
    @discord.ui.button(label="🔴 Buzzer", style=discord.ButtonStyle.blurple)
    async def buzz(self, interaction: discord.Interaction, button: discord.ui.Button):
        if (interaction.user.id not in playingUsers):
            await interaction.response.send_message("You aren't registered to play", ephemeral = True)
            return
        if (interaction.user.id in invalidBuzzUserIds):
            await interaction.response.send_message("You can't buzz in anymore this round", ephemeral = True)
            return
        if (self.firstClickUser == None):
            self.firstClickUser = interaction.user.id
            button.disabled = True
            await interaction.response.edit_message(view=self)       
            await interaction.channel.send("<@{}>".format(self.firstClickUser) + " buzzes in!")
            
            #if using teams, add all user ids from that team to the invalidBuzzUserIds so they can't buzz
            if (teamGame):
                for team in teams:
                    if (self.firstClickUser in team):
                        invalidBuzzUserIds.extend(team)
            else:
                #add user id to list so they can't buzz until invalidBuzzUserIds is reset
                invalidBuzzUserIds.append(self.firstClickUser)



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
        invalidBuzzUserIds.clear()
        await ctx.reply("Cleared buzz list")

    @commands.command()
    async def add(self, ctx, user, teamNumber=0):
        user = ctx.message.mentions[0]
        if (user == None):
            await ctx.send('Need to @ someone to add')
        if (user.id not in playingUsers):
            playingUsers.append(user.id)            
        else: #player has already been added before, remove them from any teams so we don't put them in two teams
            for idx, team in enumerate(teams):
                if (user.id in team):
                    team.remove(user.id)
                    await ctx.send("Removed <@{}> from team {}".format(user.id, idx + 1))

        if (teamNumber > 0 and teamNumber <= len(teams)):
            teamIndex = teamNumber - 1
            if (user.id not in teams[teamIndex]):
                teams[teamIndex].append(user.id)
                await ctx.send("Added <@{}> to team {}".format(user.id, teamNumber))
        
        if (teamNumber == 0):
            await ctx.send("Added <@{}> to game".format(user.id))

        if (teamNumber > len(teams)):
            await ctx.send("Team number too high")
           

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