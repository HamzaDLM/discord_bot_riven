import discord
from discord.ext import commands
from discord import FFmpegPCMAudio
from discord.utils import get
from dotenv import load_dotenv
import os
import json
import random as rd

from media import Music
from utils import opgg_username, random_champ, random_quote, opgg_username


load_dotenv()

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

chat_file = os.path.join(__location__, "chatting.json")

with open(chat_file, "r") as chat:
    chatting = json.load(chat)

intents = discord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix = '$', intents=intents)


@client.event
async def on_ready():
    """To be triggered on start up"""
    print(f'[+] Logged in as {client.user}')


@client.command(pass_context=True)
async def random(ctx, arg="champion"):
    """This command returns a random champion selected (can also do based on lane chosen ex: random mid)"""
    
    lane = ["Midlane", "Toplane", "Support", "ADC", "Jungle"]

    if arg == "champion":
        champ = random_champ(patch="12.6.1")

        embed = discord.Embed(
            colour=  discord.Colour.blue()
            )
        embed.add_field(name="Champion", value=champ["champion"])
        embed.set_image(url=champ["img_url"])
        await ctx.send(embed=embed)
    elif arg == "lane":
        lane = rd.choice(lane)
        await ctx.send(lane)


@client.command(pass_context=True)
async def opgg(ctx, *, arg):
    """Get opgg stats for a username"""

    elo = opgg_username(arg)

    embed = discord.Embed(
        colour = discord.Colour.dark_red()
        )
    embed.add_field(name=arg, value=elo["elo"])
    embed.set_image(url=elo["img"])

    await ctx.send(embed=embed)

@client.command(pass_context=True)
async def tracks(ctx):
    """List available tracks"""

    l=os.listdir(__location__ + "\\media")
    tracks=[x.split('.')[0] for x in l]
    tracks = "\n".join(tracks)

    embed = discord.Embed(
        colour = discord.Colour.dark_gold()
        )
    embed.add_field(name="Tracks", value=tracks)

    await ctx.send(embed=embed)


@client.command(pass_context=True)
async def games(ctx):
    """List available games"""
    
    games = [
        "Guess champion from a voiceline"
    ]
    games = "\n".join(games)
    embed = discord.Embed(
        colour = discord.Colour.dark_gold()
        )
    embed.add_field(name="Games List", value=games)

    await ctx.send(embed=embed)


#We delete default help command
client.remove_command("help")

@client.command(pass_context=True)
async def help(ctx):
    """List commands"""

    embed = discord.Embed(
        colour = discord.Colour.green()
        )
    embed.add_field(name='$help', value='List available commands', inline=False)
    embed.add_field(name='$opgg username', value='Return opgg stats for a username', inline=False)
    embed.add_field(name='$random champion', value='Pick a random champion', inline=False)
    embed.add_field(name='$random lane', value='Pick a random lane', inline=False)
    embed.add_field(name='$youtube', value='Play a url from youtube', inline=False)
    embed.add_field(name='$join', value='Join the voice channel', inline=False)
    embed.add_field(name='$leave', value='Leave the voice channel', inline=False)
    embed.add_field(name='$play', value='Play one of the tracks', inline=False)
    embed.add_field(name='$tracks', value='List available tracks', inline=False)
    embed.add_field(name='$game', value='Play a game from the games list', inline=False)
    embed.add_field(name='$games', value='List the games available', inline=False)

    await ctx.send(embed=embed)


@client.event
async def on_command_error(ctx, error):
    """If there is an error, it will answer with an error"""

    await ctx.send(f'Error. Try $help ({error})')


@client.event
async def on_message(message):
    """Reply to messages that contains a specific word"""

    # Don't responde to messages from the bot itself
    if message.author == client.user:
        return
    
    if "playing" in message.content:
        await message.channel.send("Whos playing? invite me please :3")
    for k, v in chatting.items():
        if message.content.startswith(f"{k.lower()}") or message.content.startswith(f"${k.lower()}"):
            await message.channel.send(v)

    await client.process_commands(message)


client.add_cog(Music(client))
client.run(os.getenv('TOKEN'))

