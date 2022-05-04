import discord
from discord.ext import commands
import youtube_dl
import asyncio
import time
import os

from utils import random_quote


__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}
 
ffmpeg_options = {
    'options': '-vn'
}
 
ytdl = youtube_dl.YoutubeDL(ytdl_format_options)
 
 
class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
 
        self.data = data
 
        self.title = data.get('title')
        self.url = data.get('url')
 
    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
 
        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]
 
        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)
 
 
class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
 
    @commands.command()
    async def join(self, ctx, *, channel: discord.VoiceChannel):
        """Joins a voice channel"""
 
        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)
 
        await channel.connect()
 
    @commands.command()
    async def youtube(self, ctx, *, url):
        """Plays from a url (almost anything youtube_dl supports)"""
 
        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
 
        await ctx.send('Now playing: {}'.format(player.title))
 
    @commands.command()
    async def game(self, ctx, *, query):
        """random quote generator for champion guessing game"""
        
        if query == "guess the champion":
            while True:
                try:
                    quote = random_quote()
                    source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(quote["quote_url"]))
                    ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)
                    await ctx.send('Guess the champion from the following quote! \n The champ will be revealed in 10 seconds.')
                    time.sleep(15)
                    embed = discord.Embed(
                        colour=discord.Colour.  orange()
                    )
                    embed.add_field(name="Champion is:", value=quote["champion"])
                    embed.set_image(url=quote["img_url"])
                    await ctx.send(embed=embed)
                    break
                except:
                    pass
        else:
            await ctx.send('Please select the game type, enter $games to see the list of games available.')
    
    @commands.command()
    async def play(self, ctx, *, query):
        """Play tracks from local media directory"""
        sound = f"{__location__}\\media\\{query}.mp3"
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(sound))
        ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)

        await ctx.send('Now playing: {}'.format(query))

    @commands.command()
    async def stop(self, ctx):
        """Stops and disconnects the bot from voice"""
    
        await ctx.voice_client.disconnect()
 
    @game.before_invoke
    @play.before_invoke
    @youtube.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()


