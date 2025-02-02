from __future__ import annotations

from discord.ext import commands
import discord
import re
import config2
import asyncio
import socketio
import random


intents = discord.Intents.all()
bot = commands.Bot(command_prefix='$', intents=intents)
sio = socketio.AsyncClient()

currentGameContext = None


# Defines a custom Select containing colour options
# that the user can choose. The callback function
# of this class is called when the user changes their choice
class Dropdown(discord.ui.Select['Select']):
    def __init__(self,optionList):
        self.optionList = optionList
        # Set the options that will be presented inside the dropdown
        options = [            
            ]
        
        for x in self.optionList:
            options.append(discord.SelectOption(label=x))
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


# Define a simple View that gives us a confirmation menu
class Confirm(discord.ui.Button):
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



class TurnOptions(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None
        
        
    @discord.ui.button(label='Roll', style=discord.ButtonStyle.green)
    async def Roll(self, interaction: discord.Interaction, button: discord.ui.Button):
        roll = random.randrange(1,6)
        await interaction.response.send_message('You rolled a '+str(roll), ephemeral=True)
        self.value = True
        self.stop()

    # This one is similar to the confirmation button except sets the inner value to `False`
    @discord.ui.button(label='Use Item', style=discord.ButtonStyle.grey)
    async def Item(self, interaction: discord.Interaction, button: discord.ui.Button):
        async def my_callback(interaction):
            await interaction.response.send_message('you chose' + select.values[0], ephemeral = True)
            view.stop()
            
        options = ['item 1', 'item 2', 'item 3']
        view = discord.ui.View()
        select = Dropdown(options)
        select.callback = my_callback
        view.add_item(select)
        await interaction.response.send_message('Your Items:',view = view, ephemeral=True)
        self.value = False
        self.stop()



class DropdownSort(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.ordered = []
        # Adds the dropdown to our view object.
        options = ['event 1', 'event 2', 'event 3', 'event 4']
        for x in options:
            toAdd = Dropdown(options)
            self.add_item(toAdd)
            self.ordered.append(toAdd)
            
        self.add_item(Confirm())

class Textform(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None
    
    @discord.ui.button(label='input', style=discord.ButtonStyle.green)
    async def openInput(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(Textbox())
        
        
        
class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(command_prefix=commands.when_mentioned_or('$'), intents=intents)

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')



@bot.command()
async def turn(ctx):
    view = TurnOptions()
    await ctx.send('It is your turn', view = view)
    
    
@bot.command()
async def sort(ctx):
    """Sends a message with our dropdown containing colours"""

    # Create the view containing our dropdown
    view = DropdownSort()

    # Sending a message containing our view
    await ctx.send('order these events:', view=view)
    
    

@sio.event
async def text(data):
    global currentGameContext
    gctx = currentGameContext
    
    print(data)
    view = Textform()
    await gctx.send('Press the Green button to open the answer prompt', view=view)
    # event = await sio.receive()
    # print(f'received event: "{event[0]}" with arguments {event[1:]}')


@bot.command(pass_context=True)
async def initiate(ctx):
    global currentGameContext
    currentGameContext = ctx
    await ctx.send('This channel will be used for the current game session')
    
    
@bot.command(pass_context=True)
async def join(ctx):
    #userid, username
    await ctx.send("Joining game")             
    await sio.emit('unity', {'command': 'spawn','id': ctx.author.id, 'username':ctx.author.display_name})

@sio.event
async def spawn(data):
    print("emit test")

# @commands.command(pass_context=True)
# async def move(self, ctx, direction):
    # match direction.lower():
        # case 'u' | 'd' | 'l' | 'r':
            # await ctx.send("Moving " + direction)
            # await self.sio.emit('move', {'id': ctx.message.author.id, 'direction': direction})
        # case _:
            # await ctx.send("Invalid direction (u, d, l, r)")
    
@bot.event
async def on_ready():
    print("Connecting to socketio")
    await sio.connect(config2.server)
    
@sio.event
async def connect():
    print("Connected to socketio server")

@sio.event
async def connect_error(data):
    print("Connection to socketio server failed")

@sio.event
async def disconnect():
    print("Disconnected from socketio server")

@sio.event
async def register(id):
    print("connected socketio: ", id)


bot.run(config2.TOKEN)
# async def main():
    # extensions = ['sockets']
    # for extension in extensions:
        # try:
            # await bot.load_extension(extension)
            # print('Loaded extension: {}'.format(extension))            
        # except Exception as error:
            # print('{} cannot be loaded. [{}]'.format(extension, error))             
    # await bot.start(config2.TOKEN)

# if __name__ == '__main__':
    # try:
        # asyncio.run(main())
    # except KeyboardInterrupt:
        # print('Exited via keyboard interrupt')
    # except Exception as error:
        # print(error)
