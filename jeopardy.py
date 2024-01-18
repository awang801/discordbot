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
from PIL import Image, ImageFilter, ImageDraw, ImageFont, ImageColor  # imports the library
import textwrap
import numpy as np

#defined in bot.py globally
invalidBuzzUserIds = [] 
inGame = False
teamGame = True
teams = {}
score = {}
teamCount = 0
buzzed = []
gameOver = False
board = [[0,0,0,0,0,0],[0,0,0,0,0,0],[0,0,0,0,0,0],[0,0,0,0,0,0],[0,0,0,0,0,0]]
boardNum = 0
baseScore = 0
dailyDouble = (0,0)
class Buzzer(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None
        self.firstClickUser = None
        self.userName = None
        self.ctx = None
        self.timeout = None
    
    @discord.ui.button(label="🔴 Buzzer", style=discord.ButtonStyle.blurple)
    async def buzz(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            if (interaction.user.name not in teams.keys()):
                await interaction.response.send_message("You aren't registered to play", ephemeral = True)
                return
            if (interaction.user.name in invalidBuzzUserIds):
                await interaction.response.send_message("You can't buzz in anymore this round", ephemeral = True)
                return
            if (self.firstClickUser == None):
                self.firstClickUser = interaction.user.id
                button.disabled = True
                self.userName = interaction.user.name
                await interaction.response.edit_message(view=self)
                await interaction.channel.send("<@{}>".format(self.firstClickUser) + " buzzes in!")
                # if (self.ctx.voice_client):        
                    # if(self.ctx.voice_client.is_playing()):
                        # self.ctx.voice_client.stop()
                team = teams[interaction.user.name]
                #if using teams, add all user ids from that team to the invalidBuzzUserIds so they can't buzz
                if (teamGame):
                    for x in teams:
                        if (teams[x] == team):
                            invalidBuzzUserIds.append(x)
                else:
                    #add user id to list so they can't buzz until invalidBuzzUserIds is reset
                    invalidBuzzUserIds.append(interaction.user.name)
            return(interaction.user.name)
        except Exception as e:
            print(e)
    async def on_timeout(self):
        self.stop()
        



class jeopardy(commands.Cog):
    def __init__(self, client):
        self.client = client
        
    @commands.command()
    async def jeopardy(self, ctx):
        try:
            global inGame
            global board
            if(inGame == False):
                inGame = True
                if (np.sum(board) == 0):
                    generateBoard(1, 100)
                while(inGame):
                    global score
                    channel = ctx.message.channel
                    await ctx.send("pick a category:", file = discord.File("images/output.png"))
                    #gamemaster picks a category
                    boardQuestion = 0
                    global dailyDouble
                    def adminCheck(m):
                        return isinstance(m.channel, discord.channel.DMChannel) and m.author.id == 96488280010260480
                        
                    def dCheck(m):
                        return m.channel == channel and m.author.id == 96488280010260480
                    while(boardQuestion == 0):
                    

                        # input1 = input()
                        input1 = await self.client.wait_for('message', check=adminCheck)
                        if(input1.content == "pause"):
                            inGame = False
                            return
                        if(input1.content == "end"):

                            board = [[0,0,0,0,0,0],[0,0,0,0,0,0],[0,0,0,0,0,0],[0,0,0,0,0,0],[0,0,0,0,0,0]]
                            inGame = False
                            score = dict.fromkeys(score, 0)
                            return
                        row = int(input1.content[0]) - 1

                        column = int(input1.content[1]) - 1
                        boardQuestion = board[row][column]
                        
                    buzzing = True
                    
                    if(dailyDouble == (row, column)):
                        await ctx.send(file = discord.File("images/Jeopardy21_S30_Daily_Double_Logo.webp"))
                        buzzing = False
                        input2 = await self.client.wait_for('message', check=dCheck)
                        player = input2.mentions[0]
                        q = displayQuestion(row, column)
                        await ctx.send(file = discord.File("images/question.png"))
                        input3 = await self.client.wait_for('message', check=adminCheck)
                        score[player.name] += int(input3.content)
                        await ctx.send(scoreboard())
                    else:    
                        q = displayQuestion(row, column)
                        if(q[1] == "emoji"):
                            await ctx.send(q[0])
                        else:
                            await ctx.send(file = discord.File("images/question.png"))
                        

                        while(buzzing):
                            view = Buzzer()
                            try:
                                if(q[1] == "audio"):
                                    try:
                                        if ctx.voice_client is None:
                                            await ctx.author.voice.channel.connect(reconnect=True)
                                        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("songs/" + q[2]))
                                        ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)
                                        view.ctx = ctx
                                    except:
                                        traceback.print_exc()
                                await ctx.reply(view=view)
                                input2 = await self.client.wait_for('message', check=adminCheck, timeout=20)
                                if (input2.content == "y"):
                                    invalidBuzzUserIds.clear()
                                    buzzing = False
                                    
                                    score[view.userName] += ((row+1)*baseScore)
                                    await ctx.send(scoreboard())
                                elif(input2.content == "n"):
                                    score[view.userName] -= ((row+1)*baseScore)
                                    await ctx.send(scoreboard())
                                elif(input2.content == "cancel"):
                                    buzzing = False
                                    invalidBuzzUserIds.clear()
                                else:
                                    continue
                            except asyncio.TimeoutError:
                                buzzing = False
                                view.stop()
                                invalidBuzzUserIds.clear()
                                await ctx.send('No one got this one!')
                            
                    if (ctx.voice_client):        
                        if(ctx.voice_client.is_playing()):
                            ctx.voice_client.stop()
                    cover (row, column)
                    if(np.sum(board) == 0):
                        inGame = False
                
            else:
                await ctx.send("There is already a game in session")
        except:
            traceback.print_exc()
            
    @commands.command()
    async def resetscore(self, ctx):
        if(ctx.message.author.id == 96488280010260480):
            global teams
            global score
            score = dict.fromkeys(score, 0)
        
    @commands.command()
    async def ingame(self, ctx):
        if(ctx.message.author.id == 96488280010260480):
            global inGame
            inGame = False
    
    @commands.command()
    async def generate(self, ctx, board_num, base_score):
        try:
            if(ctx.message.author.id == 96488280010260480):
                generateBoard(int(board_num), int(base_score))
                await ctx.send(file = discord.File("images/output.png"))
        except:
            traceback.print_exc()
    @commands.command()
    async def add(self, ctx, user, scoreAddition):
        try:
            if(ctx.message.author.id == 96488280010260480):
                if (user == None):
                    await ctx.send('Need to @ someone to add')
                user = ctx.message.mentions[0]
                found = False
                for key in teams:
                    if (user.name == key):
                        found = True
                        score[user.name] += int(scoreAddition)
                        await ctx.send(scoreboard())
                        return
                await ctx.send("User not registered")
        except Exception as e:
            print(e)
    @commands.command()
    async def scoreboard(self, ctx):
        try:
            await ctx.send(scoreboard())
        except Exception as e:
            print(e)
    #command to use if the first person that buzzed got it wrong (displays another buzzer)
    @commands.command()
    async def buzz(self, ctx):
        try:
            await ctx.reply("Buzz in to answer!", view=Buzzer(ctx))
        except:
            traceback.print_exc()

    #For testing only
    #Instead of using a command for this, just do this whenever a new question is asked
    @commands.command()
    async def resetbuzz(self, ctx):
        if(ctx.message.author.id == 96488280010260480):
            invalidBuzzUserIds.clear()
            await ctx.reply("Cleared buzz list")

    @commands.command()
    async def register(self, ctx, user, teamNumber=0):
        try:
            user = ctx.message.mentions[0]
            if (user == None):
                await ctx.send('Need to @ someone to add')
            for key in teams:
                if (user.name == key):
                    if(teams[key] != teamNumber):
                        await ctx.send("Added {} from team {} to team {}".format(user.name, teams[key], teamNumber))
                        teams[key] = teamNumber
                    else:
                        await ctx.send("User already registered")

            if (teamNumber > 0):
                if (user.name not in teams.keys()):
                    teams[user.name] = teamNumber
                    score[user.name] = 0
                    await ctx.send("Added {} to team {}".format(user.name, teamNumber))
            
            if (teamNumber == 0):
                teams[user.name] = 0
                score[user.name] = 0
                await ctx.send("Added {} to game without a team".format(user.name))
        except Exception as e:
            print(e)
       

async def setup(client):
	await client.add_cog(jeopardy(client))

def displayQuestion(x,y):
    conn = mysql.connect(
        host = config.host,
        user = config.user,
        passwd = config.pw,
        database = config.db
        )
    c = conn.cursor(buffered=True)
    c.execute('SELECT question,type,link from jeopardy where id = "' +str(board[x][y])+ '"')
    
    out = c.fetchall()[0]
    question = out[0]
    qType = out[1]
    qLink = out[2]
    print(question)
    MAX_W, MAX_H = 1920, 1400
    im = Image.new('RGB', (MAX_W, MAX_H), ImageColor.getrgb("#060ce9"))
    draw = ImageDraw.Draw(im)
    para = textwrap.wrap(question, width=42,replace_whitespace=False)
    lineCount = len(para)

    font = ImageFont.truetype(
        'fonts/GogatingBookExtrabold-23dl.ttf', 90)



    if(qType == "text" or qType == "audio"):
        current_h, pad = 700 - (lineCount * 50), 10
        for line in para:
            w, h = draw.textsize(line, font=font)
            draw.text(((MAX_W - w) / 2, current_h), line, font=font)
            current_h += h + pad
    
    elif(qType == "image"):
        im2 = Image.open("images/"+ qLink)
        w, h = im2.size
        if (w>h):
            ratio = h/w
            if(w>1700):
                new_h = int(ratio * 1700)
                im2 = im2.resize((1700, new_h))
            elif(w<1200):
                new_h = int(ratio * 1200)
                im2 = im2.resize((1200, new_h))
            elif(h>1200):
                ratio = w/h
                new_w = int(ratio * 1200)
                im2 = im2.resize((new_w, 1200))
        elif(h>w):
            ratio = w/h
            if(h>1200):
                ratio = w/h
                new_w = int(ratio * 1200)
                im2 = im2.resize((new_w, 1200))
            elif(h<1000):
                new_w = int(ratio * 1000)
                im2 = im2.resize((new_w, 1000))
        w,h = im2.size
        w = int((1920-w)/2)
        h = int(1400 - h - 50)
        im.paste(im2, (w,h))
        current_h, pad = 100 - (lineCount * 19), 10
        for line in para:
            w, h = draw.textsize(line, font=font)
            draw.text(((MAX_W - w) / 2, current_h), line, font=font)
            current_h += h + pad
            if(current_h > h):
                break
    im.save('images/question.png')
    return (out)
#initializes the board    
def generateBoard(board_num, base_score):
    conn = mysql.connect(
        host = config.host,
        user = config.user,
        passwd = config.pw,
        database = config.db
        )
    c = conn.cursor(buffered=True)
    global boardNum
    global baseScore
    boardNum = board_num
    baseScore = base_score
    img = Image.open("images/blank_jeopardy_board.png")
    font = ImageFont.truetype("fonts/CONSOLAB.TTF", 25)
    c.execute('SELECT DISTINCT category FROM jeopardy where board = ' +str(boardNum))
    
    category = c.fetchall()
    draw = ImageDraw.Draw(img)


    lineLength = 1
    iteration = 0
    for x in category:
        categoryString = textwrap.fill(x[0].upper(), width=9)
        
        draw.text((35 + 142*iteration,30), categoryString, (255,255,255), font = font)
        c.execute('SELECT id from jeopardy where category = "' + x[0] + '" and board = '+str(boardNum)+' ORDER BY difficulty')
        questions = c.fetchall()
        #print(questions)
        questionIterator = 0
        for questionID in questions:
            board[questionIterator][iteration] = questionID[0]
            questionIterator += 1
        iteration += 1
    print(board)
    font = ImageFont.truetype("fonts/GogatingBookExtrabold-23dl.ttf", 60)

    draw.text((50,150), str(base_score), (255,255,0), font = font)
    img.save("images/output.png")
    index = 0
    img = Image.open("images/output.png")
    ddx = random.randrange(5)
    ddy = random.randrange(6)
    
    global dailyDouble
    dailyDouble = (ddx,ddy)
    print(dailyDouble)
    #print(board)
    for x in range(5):
        for y in range(6):
            if x ==0 and y == 0:
                continue
            else:

                #print(str(x) + "," + str(y))

                index+=1
                draw = ImageDraw.Draw(img)
                score = base_score * (x+1)
                newX = 50 + (y*142)
                newY = 150 + (x*110)
                draw.text((newX,newY), str(score), (255,255,0), font = font)
    img.save("images/output.png")



    
def questionAnswered(coordinate):
    return
    
def scoreboard():
    printString = ""
    total = 0
    current = False
    teamSort = sorted(teams.items(), key=lambda x:x[1])
    printString += "**\nCURRENT SCORE**:\n```\n"
    for x in teamSort:
        if (current== False):
            printString += "--TEAM " + str(x[1]) + "--\n"
            current = x[1]
            printString += (str(x[0]) + " " + str(score[x[0]]) + "\n")
            total = score[x[0]]
        elif x[1] == current:
            printString += (str(x[0]) + " " + str(score[x[0]]) + "\n")
            total += score[x[0]]
        else:
            current = x[1]
            printString += "total " + str(total) + "\n"
            printString += ('--TEAM ' + str(x[1]) + "--\n")
            printString += (str(x[0]) + " " + str(score[x[0]]) + "\n")
            total = score[x[0]]
    printString += "TOTAL " + str(total) + "\n"
    printString += "```"
    return(printString)
#covers one block
def cover(x, y):
    board[x][y] = 0
    print(board)
    img = Image.open("images/output.png")
    img2 = Image.open("images/blue_box.png")
    newImg = img.copy()
    newX = 35 + (y*142)
    newY = 130 + (x*110)
    newImg.paste(img2, (newX, newY))
    newImg.save("images/output.png")