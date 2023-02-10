#Alpha-Dolphin

#Discord bot

import os
import random
from dotenv import load_dotenv
from discord.ext import commands
import discord
import io

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents().none()

bot = commands.Bot(command_prefix='>', case_insensitive=True, intents = intents)

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
async def password_command(ctx, len = '-1'):
    encrypt = random.SystemRandom()
    pw = ""
    if (len.isnumeric() and int(len) > 0):
        len = int(len)
        for x in range(len * 5 - 1):
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

#Social credit addition/deduction function
@bot.event
async def on_message(message):
    respond = random.randint(0,100)
    if not (message.author.bot or respond):
        credit = random.randint(0,10)
        points = random.randint(1,10)
        if credit >= 5:
            await message.channel.send(f"The CCP is most happy with your message! They give you {points} social credits")
            await points_change(message, points)
        else:
            await message.channel.send(f"Your actions have displeased the CCP! You have lost {points} social credits")
            await points_change(message, 0 - points)
    await bot.process_commands(message)

#Social credit point scoring function
@bot.event
async def points_change(message, points):
        member = message.author.name
        data_levels_new_member = {'credit': 0}
        out_file = rf'{message.guild}\{message.author.id}.json'
        logged_credits = data['credit']
        logged_credits += points
        data_levels_member = {'credit': logged_credits}
        await message.channel.send(f"You now have {logged_credits} credits")

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
