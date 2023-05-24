#Alpha-Dolphin

#Discord bot

import os
import random
from dotenv import load_dotenv
from discord.ext import commands
import discord
import json
from sentiment import analyze_sentiment

load_dotenv()
TOKEN = str(os.getenv('DISCORD_TOKEN'))
INTENTS = discord.Intents().all()
INTENTS.messages = True
DEBUG = os.getenv("DEBUG", 'False').lower() in ('true', '1', 't') #.env for booleans is buggy

bot = commands.Bot(command_prefix='>', case_insensitive=True, intents = INTENTS)

@bot.event
async def on_ready():
    print(f'{bot.user.name} is online')

@bot.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(
        f'Hey {member.name}, welcome to the server'
    )

@bot.command(name='Speak', help='Gives you a friendly greeting!')
async def speak_command(ctx):
    bot_responses = [
        'Hi',
        'Hello there',
        'What\'s up',
        'Hey!'
    ]
    response = random.choice(bot_responses)
    await ctx.send(response)

#Roll a die of side foo, bar times
@bot.command(name='roll', help="""1st param = sides of dice 2nd param = number of dice""")
async def roll_command(ctx, number_of_dice = '-1', number_of_sides = '-1'):
    if not (number_of_dice.isnumeric() and int(number_of_dice) > 0 
    and number_of_sides.isnumeric() and int(number_of_sides) > 0): 
        await invalid_arg_error(ctx)
    number_of_dice = int(number_of_dice)
    number_of_sides = int(number_of_sides)
    dice = [
        str(random.choice(range(1, number_of_sides + 1)))
        for _ in range(number_of_dice)
    ]
    await ctx.send(', '.join(dice))

#Generates a cryptographically random password of length 4n in a string of length 5n-1
@bot.command(name='password', help="""Generates a cryptographically random password of length 4n""")
async def password_command(ctx, length = '-1'):
    encrypt = random.SystemRandom()
    pw = ""
    if (length.isnumeric() and int(length) > 0):
        length = int(length)
        for x in range(length * 5 - 1):
            if (x % 5 == 4):
                pw += " "
            else:
                numOrLetter = encrypt.randint(0,1)
                if (numOrLetter):
                    pw += chr(encrypt.randint(65,122))
                else:
                    pw += chr(encrypt.randint(33, 64))
        await ctx.send('```' + pw + '```')
    else:
        await invalid_arg_error(ctx)

#General purpose invalid args function
@bot.event
async def invalid_arg_error(ctx):
    await ctx.send("Invalid args")

@bot.event
async def on_message(message):
    if not (message.author.bot) :
        await bot.process_commands(message)
        result = await analyze_sentiment(message)
        if result is not None:
            await socialCredit(message, result)

#Social credit output message function
async def socialCredit(message, struct) :
    if DEBUG : print(struct['compound score'] > 0)
    if DEBUG : print('negative' in struct['topic'])
    if DEBUG : print((struct['compound score'] > 0) != ('negative' in struct['topic']))
    if (struct['compound score'] > 0) != ('negative' in struct['topic']):
        if (struct['compound score'] * 10 > 7.5 ) : await message.channel.send(f"The CCP is most happy with your message! They give you {struct['compound score'] * 10} social credits")
        else : await message.channel.send(f"Your message appeases the CCP. They give you {struct['compound score'] * 10} social credits")
        await pointsChange(message, struct['compound score'] * 10)
    else:
        if (struct['compound score'] * 10 < -7.5 ) : await message.channel.send(f"Your actions have outraged the CCP! You have lost {abs(struct['compound score'] * 10)} social credits")
        else: await message.channel.send(f"The CCP has noted your disobedience. You have lost {abs(struct['compound score'] * 10)} social credits")
        await pointsChange(message, struct['compound score'] * 10)

    # respond = random.randint(0,100)
    # if not (message.author.bot or respond):
    #     credit = random.randint(0,1)
    #     points = random.randint(1,10)
    #     if credit >= 1:
    #         await message.channel.send(f"The CCP is most happy with your message! They give you {points} social credits")
    #         await pointsChange(message, points)
    #     else:
    #         await message.channel.send(f"Your actions have displeased the CCP! You have lost {points} social credits")
    #         await pointsChange(message, 0 - points)
    # await bot.process_commands(message)

#Social credit update function
@bot.event
async def pointsChange(message, points):
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "user_data.json")
    with open(file_path, "r") as file:
        existing_data = json.load(file)
    print(str(message.author.id) in existing_data)
    if str(message.author.id) in existing_data:
        existing_data[str(message.author.id)]["credits"] += points
    else:
        existing_data[str(message.author.id)] = {"credits": points}
    
    with open(file_path, "w") as file:
        json.dump(existing_data, file)

    await message.channel.send(f"You now have {existing_data[str(message.author.id)]['credits']} credits")

#General purpose invalid perms function
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You can\'t do that.')

#Anonymously messages another user
@bot.command(name='message', help="""Anonymously messages another user - <@ID>""")
async def dm(ctx, user: discord.User, *message):
    await user.send("You have an anonymous message:")
    await user.send(" ".join(message[:]))

bot.run(TOKEN)

#TODO: Social credit leaderboard
#   Multi dice roll?
#   Social credit for server boosting
