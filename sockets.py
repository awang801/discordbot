#--------------------------------------#
#---------------OBSOLETE---------------#
#--------------------------------------#

import discord
import config2
import socketio
from discord.ext import commands

class Sockets(commands.Cog):
    sio = socketio.AsyncClient()
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(pass_context=True)
    async def join(self, ctx):
        #userid, username
        await ctx.send("Joining game")             
        await self.sio.emit('join', {'id': ctx.author.id, 'username':ctx.author.display_name})

    # @commands.command(pass_context=True)
    # async def move(self, ctx, direction):
        # match direction.lower():
            # case 'u' | 'd' | 'l' | 'r':
                # await ctx.send("Moving " + direction)
                # await self.sio.emit('move', {'id': ctx.message.author.id, 'direction': direction})
            # case _:
                # await ctx.send("Invalid direction (u, d, l, r)")
        
    @commands.command(pass_context=True)
    async def test(self, ctx):
        await ctx.send("Test worked")

    @commands.Cog.listener()
    async def on_ready(self):
        print("Connecting to socketio")
        await self.sio.connect(config.server)
        
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
    async def register(self, id):
        print("connected socketio: ", id)
    

async def setup(bot):
    await bot.add_cog(Sockets(bot))