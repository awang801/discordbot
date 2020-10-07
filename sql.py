import mysql.connector
from mysql.connector import errorcode
import re
from discord.ext import commands
import os.path

class SQL:
    def __init__(self, client):
        self.client = client
        self.startingMoney = 100

    def create_card(self, name, top, right, bottom, left, img_path, rarity):
        default_path = r'F:\Wheat and Wolf\img'
        full_path = os.path.join(default_path, img_path)
        card_description = ("INSERT INTO cards "
        "(`name`, `top`, `right`, `bottom`, `left`, `img_path`, `rarity`) "
        "VALUES (%(name)s, %(top)s, %(right)s, %(bottom)s, %(left)s, %(img_path)s, %(rarity)s)")        
        #print(card_description)
        card_data = {
            'name': name,
            'top': top,
            'right': right,
            'bottom': bottom,
            'left': left,
            'img_path': full_path,
            'rarity': rarity,
            }
        #print(card_data)
        try:
            self.cursor.execute(card_description, card_data)
            self.connection.commit()
            print("Successfully added card: {}".format(name))
            return True
        except mysql.connector.Error as err:
            print("Failed to create card: {}".format(err))
            return False

    def create_database(self, db_name):
        try:
            self.cursor.execute("CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(db_name))
        except mysql.connector.Error as err:
            print("Failed creating database: {}".format(err))
            exit(1)
        
    def connect(self):
        self.connection = mysql.connector.connect(
            host="localhost",
            user="raene",
            passwd="WCzidaneWS2@",
            database="botdb1"
        )
        self.cursor = self.connection.cursor(buffered=True)

    def disconnect(self):
        self.cursor.close()
        self.connection.close()
    
    def query_users(self):
        self.cursor.execute("SELECT discord_id FROM users")
        self.existing_users = ', '.join([str(users[0]) for users in self.cursor])

    def query_user(self, discordID):
        self.cursor.execute("SELECT `discord_id`, `name`, `money` FROM users WHERE `discord_id` = {}".format(discordID))
        return self.cursor
    
    def query_card(self, cardID):
        self.cursor.execute("SELECT * FROM cards WHERE `card_id` = {}".format(cardID))
        return self.cursor

    def query_card2(self, cardName):
        self.cursor.execute("SELECT * FROM cards WHERE `name` = {}".format(cardName))
        return self.cursor
    
    @commands.command(pass_context=True)
    async def register(self, ctx):
        self.connect()
        self.query_users()
        discord_id = str(ctx.message.author.id)

        if discord_id in self.existing_users:
            await self.client.say('You are already registered, {}'.format(ctx.message.author.mention))
        else:
            await self.client.say("Please enter a name for your character (no symbols or numbers, limit 15 characters): ")
            nameResponse = await self.client.wait_for_message(author=ctx.message.author, timeout=10)
            
            if not re.match("^[a-z]*$", nameResponse.clean_content.lower()):
                await self.client.say('Only letters a-z allowed. Cancelling registration')
            elif len(nameResponse.clean_content) > 15:
                await self.client.say('Only 15 characters allowed. Cancelling registration')
            else:
                self.cursor.execute("INSERT INTO users (`discord_id`, `name`, `money`) VALUES (%s, %s, %s)", (discord_id, nameResponse.clean_content, self.startingMoney))
                self.connection.commit()
                await self.client.say('You are now registered in the database, {}'.format(ctx.message.author.mention))
        self.disconnect()

    @commands.command(pass_context=True)
    async def delete(self, ctx):
        await self.client.say("If you are sure, type 'confirm deletion' to delete your account")
        response = await self.client.wait_for_message(author=ctx.message.author, timeout=10)
    
        if response.clean_content.lower() == 'confirm deletion':
            self.connect()
            self.cursor.execute("DELETE FROM users WHERE discord_id={}".format(str(ctx.message.author.id)))
            self.connection.commit()
            #Delete other things related to the user account here
            await self.client.say('Successfully deleted your account, sorry to see you go {}'.format(ctx.message.author.mention))
        else:
            await self.client.say('Deletion cancelled')
    
    @commands.command(pass_context=True)
    async def profile(self, ctx):
        self.connect()        
        discord_id = str(ctx.message.author.id)
        profiledata = self.query_user(discord_id)
        if not profiledata.rowcount:
            await self.client.say("You are not registered, {}".format(ctx.message.author.mention))
        else:
            for (discordID, name, money) in profiledata:
                await self.client.say("Profile Output\nDiscord ID: {} \nName: {}\nMoney: {}".format(discordID,name,money))
        self.disconnect()
    
    @commands.command(pass_context=True)
    async def addcard(self, ctx, name, top, right, bottom, left, img_path, rarity):
        self.connect()
        result = self.create_card(name, top, right, bottom, left, img_path, rarity)
        if result:
            await self.client.say("Successfully added card {}, {}".format(name, ctx.message.author.mention))
        else:
            await self.client.say("Error, card not added")

    @commands.command(pass_context=True)
    async def card(self, ctx, cardID):
        self.connect()
        cardData = self.query_card(cardID)
        if not cardData.rowcount: 
            await self.client.say("That card does not exist")
        else:
            for (card_id, name, top, right, bottom, left, img_path, rarity) in cardData:
                await self.client.say("Card Output\nCard ID: {} \nName: {}\nTop: {}\nRight: {}\nBottom: {}\nLeft: {}\nImg: {}\nRarity: {}\n".format(card_id,name,top,right,bottom,left,img_path,rarity))
        self.disconnect()

    @commands.command(pass_context=True)
    async def card2(self, ctx, cardName):
        self.connect()
        cardData = self.query_card(cardName)
        if not cardData.rowcount: 
            await self.client.say("That card does not exist")
        else:
            for (card_id, name, top, right, bottom, left, img_path, rarity) in cardData:
                await self.client.say("Card Output\nCard ID: {} \nName: {}\nTop: {}\nRight: {}\nBottom: {}\nLeft: {}\nImg: {}\nRarity: {}\n".format(card_id,name,top,right,bottom,left,img_path,rarity))
        self.disconnect()


def setup(client):
    client.add_cog(SQL(client))