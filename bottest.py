from __future__ import annotations

from discord.ext import commands
import discord
import re
import config
import asyncio
import socketio
import random
import waiting
from waiting import wait
import json
import mysql.connector as mysql

conn = mysql.connect(
    host = config.host,
    user = config.user,
    passwd = config.pw,
    database = config.db
    )
c = conn.cursor(buffered=True)


intents = discord.Intents.all()
bot = commands.Bot(command_prefix='$', intents=intents)
sio = socketio.AsyncClient()

file = open("info.json")

js = json.load(file)

playerList = []

currentGameContext = None
currentView = None
currentMessage = None
        
#--------------------Bot Initialization--------------------#


class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(command_prefix=commands.when_mentioned_or('$'), intents=intents)

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')


@bot.event
async def on_ready():
    print("Connecting to socketio")
    await sio.connect(config.server)




#--------------------Socket Base Functions--------------------#


@sio.event
async def connect():
    print("Connected to socketio server")

@sio.event
async def connect_error(data):
    print("Connection to socketio server failed")

@sio.event
async def disconnect():
    print("Disconnected from socketio server")




    
#----------------------------------------------------#
#----------------------------------------------------#
#--------------------Bot Commands--------------------#
#----------------------------------------------------#
#----------------------------------------------------#


@bot.command()
async def file(ctx):
    global playerList
    #team1, team2 = splitTeams(playerList)
    await ctx.send("Click the button to see your files and labels:", view = File(playerList))


@bot.command()
async def cooking(ctx):
    await ctx.send("Click the button below to see your clue:", view = Cooking())
    

@bot.command()
async def connections(ctx):
    await ctx.send(view = Connections())


@bot.command()
async def user(ctx):
    view = discord.ui.View()
    
    options = [discord.SelectOption(label = ctx.message.author.display_name,emoji = "<a:cuffs:532014602742136852>")]
    
    view.add_item(Dropdown(options))
    
    await ctx.send(view= view)
    
@bot.command()
async def turn(ctx):
    view = TurnOptions()
    await ctx.send('It is your turn', view = view)
    
    
@bot.command()
async def sort(ctx):
    """Sends a message with our dropdown containing colours"""
    global playerList
    # Create the view containing our dropdown
    view = DropdownSort(playerList)

    # Sending a message containing our view
    await ctx.send('order these events:', view=view)
    
@bot.command(pass_context=True)
async def initiate(ctx):
    global currentGameContext
    currentGameContext = ctx
    await ctx.send('This channel will be used for the current game session')   


@bot.command(pass_context=True)
async def join(ctx):
    #userid, username
    global playerList
    
    if len(playerList) == 0:
        playerList.append(ctx.author.id)
        await ctx.send("Joining game")
    else:
        if ctx.author.id in playerList:
            await ctx.send("You have already joined the game")
            return
        else:
            playerList.append(ctx.author.id)
            await ctx.send("Joining game")
    #await ctx.send("Joining game")             
    #await sio.emit('unity', {'command': 'lobbyjoin','id': ctx.author.id, 'choice': ctx.author.display_name})

@bot.command(pass_context=True)
async def select(ctx, char):
    #userid, username
    await ctx.send("Joining game")
    await sio.emit('unity', {'command': 'lobbyselect','id': ctx.author.id, 'choice':char})






#---------------------------------------------------------#
#---------------------------------------------------------#
#--------------------Events from Unity--------------------#
#---------------------------------------------------------#
#---------------------------------------------------------#



@sio.event
async def text(data):
    global currentGameContext
    gctx = currentGameContext
    
    print(data)
    view = Textform()
    await gctx.send('Press the Green button to open the answer prompt', view=view)
    # event = await sio.receive()
    # print(f'received event: "{event[0]}" with arguments {event[1:]}')
    
    



@sio.event
async def spawn(data):
    print("emit test")
    
    
@sio.event
async def itemList(data):
    global currentMessage
    print(currentMessage.content)
    
    print(data)
    async def my_callback(interaction):
        await interaction.response.send_message('you chose' + select.values[0], ephemeral = True)

    options = []
    for x in data:
        options.append(data[x])
    view = discord.ui.View()
    select = Dropdown(options)
    select.callback = my_callback
    select.placeholder = 'Choose an Item'
    view.add_item(select)

    print(options)
    await currentMessage.edit(content = 'Your items:',view = view)
    
@sio.event
async def connectionsResult(data):
    global currentView
    if data["result"] == "success":
        await currentView.success()
    else:
        await currentView.fail()
    
    
    
    
    
    
#--------------------------------------------------------#
#--------------------------------------------------------#
#--------------------Items and Modals and Helpers--------------------#
#--------------------------------------------------------#
#--------------------------------------------------------#  


def splitTeams(allPlayers):

    half = int(len(allPlayers)/2)
    random.shuffle(allPlayers)
    
    return allPlayers[:half], allPlayers[half:]



class Dropdown(discord.ui.Select['Select']):
    def __init__(self,optionList):
        
        
        # optionList = list of options that need to be passed into this item
        self.optionList = optionList 
        
        
        # initialize options as an empty list
        options = [            
            ]
        # put the options passed in for the dropdown into the options list
        for x in self.optionList:
            if(type(x) is str):
                options.append(discord.SelectOption(label=x))
            else:
                options.append(x)
            
        # The placeholder is what will be shown when no option is chosen
        # The min and max values indicate we can only pick one of the three options
        # The options parameter defines the dropdown options. We defined this above
        super().__init__(placeholder='Choose an event', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        
        #makes the interaction occur, interaction will fail if you dont have the response do something
        await interaction.response.defer() 
        

class Textbox(discord.ui.Modal, title='Textbox'):
    # Our modal classes MUST subclass `discord.ui.Modal`,
    # but the title can be whatever you want.

    # This will be a short input, where the user can enter their name
    # It will also have a placeholder, as denoted by the `placeholder` kwarg.
    # By default, it is required and is a short-style input which is exactly
    # what we want.
    
    # Initialize the item in the modal, in this case a singular text box
    name = discord.ui.TextInput(
        label='Answer',
        placeholder='Write your answer here',
    )

    # This is a longer, paragraph style input, where user can submit feedback
    # Unlike the name, it is not required. If filled out, however, it will
    # only accept a maximum of 300 characters, as denoted by the
    # `max_length=300` kwarg.
    # feedback = discord.ui.TextInput(
        # label='What do you think of this new feature?',
        # style=discord.TextStyle.long,
        # placeholder='Type your feedback here...',
        # required=False,
        # max_length=300,
    # )


    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'Thanks for your feedback, {self.name.value}!', ephemeral=True)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)

        # Make sure we know what the error actually is
        traceback.print_exception(type(error), error, error.__traceback__)


# Define a simple View that gives us a confirmation button
class SortConfirm(discord.ui.Button):
    def __init__(self):
        super().__init__(label = "Confirm",style=discord.ButtonStyle.green)
        self.value = None

    # When the confirm button is pressed, set the inner value to `True` and
    # stop the View from listening to more input.
    # We also send the user an ephemeral message that we're confirming their choice.
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message('Confirming', ephemeral=True)
        self.value = True
        self.disabled = True
        assert self.view is not None
        view: Select = self.view
        for x in view.ordered:
            try:
                print(str(view.ordered.index(x)) + x.values[0])
            except:
                print('You have not chosen your '+str(x.order)+' value')
        view.stop()
        
        
#button class specifically for Connections view
class ConnectionsButton(discord.ui.Button['Connections']):
    def __init__(self, x: int, y: int):
        super().__init__(style=discord.ButtonStyle.primary, label='\u200b',row=y)
        self.x = x
        self.y = y

    # This function is called whenever this particular button is pressed
    # This is part of the "meat" of the game logic
    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        view: Connections = self.view
        #state = view.board[self.y][self.x]
        isChosen = False
        for x in view.chosen:
            if self == x:
                view.chosen.remove(x)
                self.style = discord.ButtonStyle.primary
                isChosen = True
                break
                
        if not isChosen:
            self.style = discord.ButtonStyle.success
            view.chosen.add(self)
        
        
        
        
        global currentMessage
        global currentView

        # if len(view.chosen) >=4:
            
            # for x in view.chosen:
                # x.style = discord.ButtonStyle.primary
            # view.chosen.clear()

        await interaction.response.edit_message(view=view)
        currentView = view
        # print(type(view))
        # print(type(currentView))
        currentMessage = await interaction.original_response()
        await sio.emit('unity', {'command': 'connectionsInput','id': interaction.user.id, 'x':self.x, 'y':self.y}) 

class File1Button(discord.ui.Button):
    def __init__(self):
        super().__init__(label = "Confirm",style=discord.ButtonStyle.green)
        self.value = None


    async def callback(self, interaction: discord.Interaction):
        global currentMessage
        assert self.view is not None
        view: Select = self.view

        
        # if self.identifier == "file1":
            # view.playersWithCorrectFiles[interaction.user.id]
            # message = "Current File ``` " + view.fileToDescription[view.children[0].values[0]]
            # await currentMessage.edit(content = message)
        # elif self.identifier == "label":
            # await interaction.response.defer()
        # elif self.identifier == "file2":
            # await interaction.response.defer()
        # else:
            # await interaction.response.defer()




#---------------------------------------------#
#---------------------------------------------#
#--------------------Views--------------------#
#---------------------------------------------#
#---------------------------------------------#

class File(discord.ui.View):
    def __init__(self,players):
        super().__init__()
        # self.allCharacters = js["filing"]
        # self.series = [random.choices(set(self.allCharacters["))[0]
        
        self.clueGenerators = [self.before,self.after,self.exactPosition,self.nextTo,self.notNextTo]
        self.players = players
        self.series = 0
        self.characterLists = {}
        self.fileLists = {}
        self.operations = {}
        self.clues = {}
        self.toLabel = []
        self.currentFile = None
        self.fileToDescription = {} #key is file name, value is description
        self.labelCheckList = {} #key is name, value is description
        self.correctlyLabeled = {}
        self.ephemerals = []
        
        #choose a random series to choose characters from to file
        c.execute("SELECT DISTINCT series FROM animecharacters")
        self.series = random.choice(c.fetchall())[0]
        
        c.execute("SELECT * FROM animecharacters")
        self.allCharacters = c.fetchall()
        
        
        
        
        if(len(self.players)<6):
            fileTotal = 6
        else:
            fileTotal = len(self.players)


        #endgoal amount of correct characters to label and file
        amountCorrect = random.randrange(4,6)

        
        c.execute("SELECT name,description,attributes FROM animecharacters where series = '"+self.series+"'")        
        self.toFile = random.sample(c.fetchall(),amountCorrect) #endgoal characters to file and label

        
        #initialize list of files to label
        for x in self.toFile:
            self.labelCheckList[x[0]] = x[1]
            self.toLabel.append(x)
        
        #generate more if the total file amount is higher than the randomly generated number of correctly filed characters
        c.execute("SELECT name,description,attributes FROM animecharacters where series != '"+self.series+"'")
        otherCharactersList = c.fetchall()
        toAdd = random.sample(otherCharactersList,fileTotal-amountCorrect)
        for x in toAdd:
            self.labelCheckList[x[0]] = x[1]
            self.toLabel.append(x)

        
        fileIter = 0 #keeps track of how many times the correct file has been put into the options
        self.playersWithCorrectFiles = {} # key: player id, value : list of File descriptions

        self.playersWithCorrectLabels =  {} #key: player id, value: list of character names
        
        
        self.labelPlayers, self.filePlayers = splitTeams(self.players)

        
        #assign labels and files to different players on the team
        for x in self.toLabel:

            if(self.filePlayers[fileIter] in self.playersWithCorrectFiles):
                self.playersWithCorrectFiles[self.filePlayers[fileIter]].append(x[1])
            else:
            
                self.playersWithCorrectFiles[self.filePlayers[fileIter]] = [x[1]]
            
            
            randomPlayer = random.choice(self.labelPlayers)
            
            if randomPlayer in self.playersWithCorrectLabels:
                self.playersWithCorrectLabels[randomPlayer].append(x[0])
                
            else:
                self.playersWithCorrectLabels[randomPlayer] = [x[0]]
            if(fileIter >= len(self.filePlayers)-1):
                fileIter = 0
            else:
                fileIter += 1
        
        print(self.playersWithCorrectFiles, self.playersWithCorrectLabels)
        fileIter = 0 #reset iterator
        
        #initalize list with characters that are not from the related series to file
        for x in self.labelPlayers:
            tempList = []
            tempMax = 10 - len(self.labelPlayers)
            if tempMax < 5:
                tempMax = 5
            
            for u in random.sample(self.allCharacters,tempMax):
                tempList.append(u[0])
            self.characterLists[x] = tempList
        
        
        #replace values in the character lists for those who have correct answers
        for y in self.playersWithCorrectLabels:
            for z in self.playersWithCorrectLabels[y]:
                if z in self.characterLists[y]:
                    fileIter+=1
                else:
                    replaced = False
                    while not replaced:
                        w = random.randrange(0,tempMax)
                        if self.characterLists[y][w] not in self.playersWithCorrectLabels[y]:
                            replaced = self.characterLists[y][w]
                        
                    
                    print(z, replaced)
                    self.characterLists[y][w] = z
                    print(z, self.characterLists[y][w])
                    fileIter+=1

        # print(self.playersWithCorrectFiles)
        # print(self.playersWithCorrectLabels)

        #generate clues for filing
        for x in self.players:
            clueRelation = False
            while not clueRelation:
                selectedIndex = random.randrange(0,len(self.toFile)-1)
                clueRelation = random.choice(self.clueGenerators)(selectedIndex)
            clue = self.stringFormatter(clueRelation)
            self.clues[x] = clue

 


 
    def before(self, index):
        indexMax = len(self.toFile)-1
        if index >= indexMax:
            return False
        else:
            currentChar = self.toFile[index]
            currentCharAttributes = currentChar[2].split(",")
            currentChosenAttribute = random.choice(currentCharAttributes)
            
            
            relatedChar = self.toFile[random.randrange(index+1, len(self.toFile))]
            relatedCharAttributes = relatedChar[2].split(",")
            relatedChosenAttribute = random.choice(relatedCharAttributes)
            return("before",currentChar,currentChosenAttribute,relatedChar,relatedChosenAttribute)
            
            
    
    def after(self,index):
        indexMax = len(self.toFile)-1
        if index == 0:
            return False
        else:
            currentChar = self.toFile[index]
            currentCharAttributes = currentChar[2].split(",")
            currentChosenAttribute = random.choice(currentCharAttributes)
            
            
            relatedChar = self.toFile[random.randrange(0,index)]
            relatedCharAttributes = relatedChar[2].split(",")
            relatedChosenAttribute = random.choice(relatedCharAttributes)
            return("after",currentChar,currentChosenAttribute,relatedChar,relatedChosenAttribute)
    
    
    def exactPosition(self, index):
        currentChar = self.toFile[index]
        currentCharAttributes = currentChar[2].split(",")
        currentChosenAttribute = random.choice(currentCharAttributes)
        return("exactPosition", currentChar,currentChosenAttribute)
    def nextTo(self, index):
        if index == 0:
            beforeOrAfter = 0
        elif index >= len(self.toFile) - 1:
            beforeOrAfter = 1
        else:
            #0 for before, 1 for after
            beforeOrAfter = random.randrange(0,1)
            
        if beforeOrAfter == 0:
            currentChar = self.toFile[index]
            currentCharAttributes = currentChar[2].split(",")
            currentChosenAttribute = random.choice(currentCharAttributes)
            relatedChar = self.toFile[index + 1]
            relatedCharAttributes = relatedChar[2].split(",")
            relatedChosenAttribute = random.choice(relatedCharAttributes)

            
        else:
            currentChar = self.toFile[index]
            currentCharAttributes = currentChar[2].split(",")
            currentChosenAttribute = random.choice(currentCharAttributes)
            relatedChar = self.toFile[index - 1]
            relatedCharAttributes = relatedChar[2].split(",")
            relatedChosenAttribute = random.choice(relatedCharAttributes)
            return("nextTo",currentChar,currentChosenAttribute,relatedChar,relatedChosenAttribute)
    def notNextTo(self,index):

                
        currentChar = self.toFile[index]
        currentCharAttributes = currentChar[2].split(",")
        currentChosenAttribute = random.choice(currentCharAttributes)
        exclude = [(index-1), index, (index+1)]
        for x in exclude:
            if 0<=index<len(self.toFile):
                continue
            else:
                exclude.remove(x)
        tempMax = len(self.toFile)-1
        chosenIndex = random.choice([i for i in range(0,tempMax) if i not in [exclude]])
        relatedChar = self.toFile[chosenIndex]
        relatedCharAttributes = relatedChar[2].split(",")
        relatedChosenAttribute = random.choice(relatedCharAttributes)
        return("notNextTo",currentChar,currentChosenAttribute,relatedChar,relatedChosenAttribute)
        
    def stringFormatter(self,relation):

        operation = relation[0]
        
        
        if operation == "before":
        
            return ("# __**File only characters from {}:**__\n```elm\nThe {} must be filed before the {} \n```".format(self.series,relation[2],relation[4]))
        
        elif operation == "after":
        
            return ("# __**File only characters from {}:**__\n```elm\nThe {} must be filed after the {} \n```".format(self.series,relation[2],relation[4]))
        
        elif operation == "exactPosition":
            index = self.toFile.index(relation[1])
            if index == 0:
                position = "first"
            elif index == 1:
                position = "second"
            elif index == 2:
                position = "third"
            elif index == 3:
                position = "fourth"
            elif index == 4:
                position = "fifth"
            elif index == 5:
                position = "sixth"

            return ("# __**File only characters from {}:**__\n```elm\nThe {} must be the {} file \n```".format(self.series,relation[2],position))
        
        elif operation == "nextTo":
        
            return ("# __**File only characters from {}:**__\n```elm\nThe {} must be filed next to the {} \n```".format(self.series,relation[2],relation[4]))
        
        elif operation == "notNextTo":
        
            return ("# __**File only characters from {}:**__\n```elm\nThe {} must not be filed next to the {} \n```".format(self.series,relation[2],relation[4]))
            
        else:
            return False    
        
    @discord.ui.button(label='Show', style=discord.ButtonStyle.green)
    async def Show(self, interaction: discord.Interaction, button: discord.ui.Button):
    
        async def my_callback(interaction):
            await interaction.response.defer()




                

        
        if interaction.user.id in self.labelPlayers:
            
            async def button_callback(interaction):
                global currentMessage
                if self.currentFile == None:
                    await interaction.response.send_message("There is currently no file chosen", ephemeral = True)
                else:
                    chosenCharacter = view.children[0].values[0]
                    #self.playersWithCorrectFiles[interaction.user.id]
                    if  chosenCharacter in self.labelCheckList.keys():
                        index = self.characterLists[interaction.user.id].index(chosenCharacter)
                        
                        self.characterLists[interaction.user.id].pop(index)
                        view.children[0].options.pop(index)
                    
                        
                        self.labelCheckList.pop(chosenCharacter)
                        await interaction.response.edit_message(view = view)

                        if len(self.labelCheckList) == 0:
                            await currentMessage.edit(content = "You have Successfully Labeled all files!")
                            self.stop()
                        else:
                            await currentMessage.edit(content = "You have successfully labeled " + chosenCharacter)
                            self.currentFile = None
                    else:
                        await currentMessage.edit(content = "That is not the correct label for this file")
                        await interaction.response.defer()
                    
                    
                    
                    #save the ephemeral interaction message and map it to its author
                
                
                thisMessage = await interaction.original_response()
                

                ephemPair = (interaction.user.id , thisMessage)
                
                if ephemPair not in self.ephemerals:
                    self.ephemerals.append(ephemPair)
                    
                    
            view = discord.ui.View()
            options = self.characterLists[interaction.user.id]
            select = Dropdown(options)
            select.callback = my_callback
            select.placeholder = 'Choose a Label'
            
            
            button = File1Button()
            button.callback = button_callback     
            
            
            view.add_item(select)
            view.add_item(button)
        
            await interaction.response.send_message('Your Labels:\n',view = view, ephemeral=True)
        elif interaction.user.id in self.filePlayers:
            options = []
            message = "Your Files:\n"
            fileIndex = 0
            
            for x in self.playersWithCorrectFiles[interaction.user.id]:
                
                fileHeader = "File " + str(fileIndex + 1)
                if interaction.user.id in self.fileToDescription.keys():
                    self.fileToDescription[interaction.user.id][fileHeader] = x
                else:
                    self.fileToDescription[interaction.user.id] = {}
                    self.fileToDescription[interaction.user.id][fileHeader] = x
                message += fileHeader + ": ```" +x+ "```\n" 
                options.append(fileHeader)
                fileIndex += 1
            
            view = discord.ui.View()

            Select = Dropdown(options)
            Select.callback = my_callback
            Select.placeholder = 'Choose a File'
            
            async def button_callback(interaction):
                global currentMessage
                await interaction.response.defer()
                selectValue = view.children[0].values[0]
                chosenFile = self.fileToDescription[interaction.user.id][selectValue]
                


                
                self.currentFile = chosenFile
                message = "Current File\n`" + chosenFile + "'"
                await currentMessage.edit(content = message)
                thisMessage = await interaction.original_response()

                ephemPair = (interaction.user.id , thisMessage)
                if ephemPair not in self.ephemerals:
                    self.ephemerals.append(ephemPair)
                
                
            button = File1Button()
            button.callback = button_callback     
            view.add_item(Select)
            view.add_item(button)
            await interaction.response.send_message(message,view = view, ephemeral=True)

        else:
            print("error")
            self.stop()
        global currentMessage
        currentMessage = interaction.message


        


class Cooking(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.modifiers = [self.multiply,self.addY,self.subtractY,self.asIs,self.divide]
        
        self.recipe = random.choices(js["recipes"])[0]
        
        self.ingredients = random.sample(js["ingredients"][self.recipe],len(js["ingredients"][self.recipe]))            
        
        #first value is ID, second value is a dictionary in this order: {answer, relatedAnswer, ingredient, relatedIngredient}
        self.answers = {} 
        
        
        
    def check(self, x):
        if 1<= x <= 12 and isinstance(x,int):
            return x
        else:
            return False
    
    def multiply(self,x):
        y = random.randrange(2,4)
        return (self.check(x*y), "multiply", 2)
    
    def addY(self,x):
        y = random.randrange(1,5)
        return (self.check(x + y), "add", y) 

    def subtractY(self,x):
        y = random.randrange(1,5)
        return (self.check(x - y), "subtract", y)

    def asIs(self,x):
        y = random.randrange(1,12)
        return (self.check(y), "asis", 0)
    
    def divide(self,x):
        return (self.check(x/2), "divide", 2)
        

    def stringFormatter(self, info, recalc):
    
        operation = recalc[1]
        
        
        if operation == "multiply":
        
            return ("# __**Follow The Instructions:**__\n```fix\nThe perfect amount of {} for {} is {} times the amount of {}\n```".format(info['ingredient'], self.recipe, recalc[2], info['relatedIngredient']))
        
        elif operation == "add":
        
            return ("# __**Follow The Instructions:**__\n```fix\nThe perfect amount of {} for {} is {} more than the amount of {}\n```".format(info['ingredient'], self.recipe, recalc[2], info['relatedIngredient']))
        
        elif operation == "subtract":
        
            return ("# __**Follow The Instructions:**__\n```fix\nThe perfect amount of {} for {} is {} less than the amount of {}\n```".format(info['ingredient'], self.recipe, recalc[2], info['relatedIngredient']))
        
        elif operation == "asis":
        
            return ("# __**Follow The Instructions:**__\n```fix\nThe perfect amount of {} for {} is {}\n```".format(info['ingredient'], self.recipe, info['answer']))
        
        elif operation == "divide":
        
            return ("# __**Follow The Instructions:**__\n```fix\nThe perfect amount of {} for {} is half than the amount of {}\n```".format(info['ingredient'], self.recipe, info['relatedIngredient']))
            
        else:
            return False
 



 
    @discord.ui.button(label='Clue', style=discord.ButtonStyle.green)
    async def Clue(self, interaction: discord.Interaction, button: discord.ui.Button):
        
        
        
        if not self.answers:

            
            
            answer = random.randrange(1,10)
            
            self.answers[interaction.user.id] = {}
            self.answers[interaction.user.id]['answer'] = answer
            
            self.answers[interaction.user.id]['ingredient'] = self.ingredients[0] 

            self.ingredients.pop(0)

            #await sio.emit('unity', {'command': 'cooking', 'id': interaction.user.id, 'recipe': self.recipe, 'ingredients': self.ingredients}) 
            await interaction.response.send_message("# __**Follow The Instructions:**__\n```fix\nThe perfect amount of {} for {} is {}\n```".format(self.answers[interaction.user.id]['ingredient'], self.recipe, self.answers[interaction.user.id]['answer']),ephemeral=True)


        else:
            for x in self.answers:
                if x == interaction.user.id:
                    await interaction.response.send_message("You have already been given your clue", ephemeral = True)
                    return
            
            
            
            relation = random.sample(self.answers.items(), 1)[0][1]

            relatedAnswer = relation['answer']
            relatedIngredient = relation['ingredient']

            
            answer = False
            while not answer:
            
                relateCalc = random.choice(self.modifiers)(relatedAnswer)
                answer = relateCalc[0]
            
            
            
            
            self.answers[interaction.user.id] = {}
            self.answers[interaction.user.id]['answer'] = answer
            
            self.answers[interaction.user.id]['relatedAnswer'] = relatedAnswer
            
            self.answers[interaction.user.id]['ingredient'] = self.ingredients[0]

            self.ingredients.pop(0)
            
            self.answers[interaction.user.id]['relatedIngredient'] = relatedIngredient
            print(self.answers[interaction.user.id])
            
            
            message = self.stringFormatter(self.answers[interaction.user.id], relateCalc)
            await interaction.response.send_message(message,ephemeral=True)
            

        

        

        
        

    
    

# This is our actual board View
class Connections(discord.ui.View):
    children: List[ConnectionsButton]
    def __init__(self):
        super().__init__()
        self.chosen = set()
        self.cleared = 0
        
        
        for x in range(4):
            for y in range(4):
                self.add_item(ConnectionsButton(x, y))
    async def success(self):
        
        if len(self.children) > 4:
            for x in self.chosen:
                x.style = discord.ButtonStyle.primary
            self.chosen.clear()
            for x in self.children:
                if x.row == self.cleared:
                    x.style = discord.ButtonStyle.success
                    x.disabled = True

            await currentMessage.edit(view = self)
            self.cleared += 1
        else:
            self.stop()
        
    
    async def fail(self):
        global currentMessage
        for x in self.chosen:
            x.style = discord.ButtonStyle.primary
        self.chosen.clear()
        await currentMessage.edit(view = self)
    



# Defines a custom Select containing colour options
# that the user can choose. The callback function
# of this class is called when the user changes their choice




class TurnOptions(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None
        self.items = {}
        
        
    @discord.ui.button(label='Roll', style=discord.ButtonStyle.green)
    async def Roll(self, interaction: discord.Interaction, button: discord.ui.Button):
        #roll = random.randrange(1,6)
        await sio.emit('unity', {'command': 'roll','id': interaction.user.id, 'username':interaction.user.display_name}) 
        #await interaction.response.send_message('You rolled a '+str(roll), ephemeral=True)
        self.value = True
        self.stop()

    # This one is similar to the confirmation button except sets the inner value to `False`
    @discord.ui.button(label='Use Item', style=discord.ButtonStyle.grey)
    async def Item(self, interaction: discord.Interaction, button: discord.ui.Button):
        async def my_callback(interaction):
            await interaction.response.send_message('you chose' + select.values[0], ephemeral = True)
        view = discord.ui.View()
        
 
        # options = ['placeholder']

        # select = Dropdown(options)
        # select.callback = my_callback
        # view.add_item(select)
        await interaction.response.send_message('Your Items:',ephemeral = True)
        global currentMessage
        currentMessage = await interaction.original_response()
        await sio.emit('unity', {'command': 'requestitem','id': interaction.user.id, 'choice':interaction.user.display_name})

class DropdownSort(discord.ui.View):
    def __init__(self,players):
        super().__init__()
        self.ordered = []
        self.players = players
        random.shuffle(players)
        
        self.category = random.choices(list(js["sorting"].keys()))[0]
        self.answer = js["sorting"][self.category]
        self.optionLists = {}
        self.playerAnswer = []
        print(self.answer)
        iteration = 0
        shuffledAnswers = []
        for x in self.answer:
            shuffledAnswers.append(x)
        random.shuffle(shuffledAnswers)
        print(self.answer)
        print(shuffledAnswers)
        for x in shuffledAnswers:
            
            if self.players[iteration] in self.optionLists:
                self.optionLists[self.players[iteration]].append(x)
            else:
                self.optionLists[self.players[iteration]] = []
                self.optionLists[self.players[iteration]].append(x)
            iteration += 1
            
            if iteration >= len(self.players):
                iteration = 0
    @discord.ui.button(label='Show', style=discord.ButtonStyle.green)
    async def Show(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Adds the dropdown to our view object.
        view = discord.ui.View()


        select = Dropdown(self.optionLists[interaction.user.id])
        #Select.callback = my_callback
        select.placeholder = 'Choose an event'    
        
        async def button_callback(interaction):
            global currentMessage

            selectValue = view.children[0].values[0]
            
            index = self.optionLists[interaction.user.id].index(selectValue)
            view.children[0].options.pop(index)
            self.optionLists[interaction.user.id].pop(index)
            self.playerAnswer.append(selectValue)
            message = ""
            if len(self.answer) == len(self.playerAnswer):
            
                if self.answer == self.playerAnswer:
                    await interaction.response.send_message("You have sorted the answers correctly!")
                else:
                    for x in self.answer:
                        message += x + "\n" 
                    await interaction.response.send_message("You have not sorted the answers correctly! Here is the correct order:\n" + message)
                view.stop()
                self.stop()
                
                    
            else:        
                for x in self.playerAnswer:
                    message += x + "\n"
                if len(view.children[0].options) == 0:
                    await interaction.response.edit_message(content = "You have no more events", view = None)
                else:
                    await interaction.response.edit_message(view=view)
                await currentMessage.edit(content = "Your current event order:\n" + message)
            

            
        button = File1Button()
        button.callback = button_callback     
        view.add_item(select)
        view.add_item(button)
        
        await interaction.response.send_message("Your Events:", view = view, ephemeral = True)
        global currentMessage
        currentMessage = interaction.message

class Textform(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None
    
    @discord.ui.button(label='input', style=discord.ButtonStyle.green)
    async def openInput(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(Textbox())
# @commands.command(pass_context=True)
# async def move(self, ctx, direction):
    # match direction.lower():
        # case 'u' | 'd' | 'l' | 'r':
            # await ctx.send("Moving " + direction)
            # await self.sio.emit('move', {'id': ctx.message.author.id, 'direction': direction})
        # case _:
            # await ctx.send("Invalid direction (u, d, l, r)")

# @sio.event
# async def register(id):
    # print("connected socketio: ", id)



# async def main():
    # extensions = ['sockets']
    # for extension in extensions:
        # try:
            # await bot.load_extension(extension)
            # print('Loaded extension: {}'.format(extension))            
        # except Exception as error:
            # print('{} cannot be loaded. [{}]'.format(extension, error))             
    # await bot.start(config.TOKEN)

# if __name__ == '__main__':
    # try:
        # asyncio.run(main())
    # except KeyboardInterrupt:
        # print('Exited via keyboard interrupt')
    # except Exception as error:
        # print(error)
        
        
bot.run(config.TOKEN)