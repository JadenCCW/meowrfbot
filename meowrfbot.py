import queue
import discord
from discord.ext import commands, tasks
import youtube_dl

from random import choice

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

queue = []

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



client = commands.Bot(command_prefix='^')

status = ['Justin Play League', 'Jaden Sleep', 'The Stars', 'Aiden Read Manga', 'Avery Working Out', 'Jake Gym with Jay']

@client.event
async def on_ready():
    change_status.start()
    print('Bot is online!')

@client.command(name='ping', help='This command returns the latency')
async def ping(ctx):
    await ctx.send(f'**Pong!** latency: {round(client.latency * 1000)} ms')

@client.command(name='greet', help='This command returns a random welcome message')
async def greet(ctx):
    responses = ['**Whats up bitch**', '**Shut up lmao**', '**Good morning!**', '**Hey!**', '**Wassup!**', '**Jaden Chung says: shut up bitch**', '**Have a wonderful day!**']
    await ctx.send(choice(responses))

@client.command(name='credits', help='This command returns the credits')
async def credits(ctx):
    await ctx.send('**Made by jaden#0008**')
    await ctx.send('**ABGs hmu @chung.jaden on ig**')

@client.command(name='join')
async def join(ctx):
    if not ctx.author.voice:
        await ctx.send('**You are not connected to a vc!**')
        return
    
    else:
        channel = ctx.author.voice.channel
        await ctx.send('**Successfully Connected! I hate minorities!**')
    
    await channel.connect()

@client.command(name='play', help='This command plays a song')
async def play(ctx, url):

    global queue
    if ctx.voice_client in client.voice_clients:
        return
    else:
        if not ctx.author.voice:
            await ctx.send('**You are not connected to a vc!**')
            return
    
        else:
            channel = ctx.author.voice.channel
            await ctx.send('**Successfully Connected! I hate minorities!**')
            await channel.connect()

    queue.append(url)

    async with ctx.typing():
        player = await YTDLSource.from_url(queue[0], loop=client.loop, stream=True)
        ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
        del(queue[0])

    await ctx.send(':arrow_forward: **Now playing: {}** :arrow_forward:'.format(player.title))

@client.command(name='pause', help='This command pauses a song')
async def pause(ctx):
    
    ctx.voice_client.pause()

@client.command(name='resume', help='This command resumes a song')
async def resume(ctx):
    
    ctx.voice_client.resume()

@client.command(name='stop', help='This command stops a song')
async def stop(ctx):
    
    ctx.voice_client.stop()

@client.command(name='skip', help='This command skips a song')
async def skip(ctx):
    
    global queue

    ctx.voice_client.stop()
    async with ctx.typing():
        player = await YTDLSource.from_url(queue[0], loop=client.loop, stream=True)
        ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
        del(queue[0])

    await ctx.send(':arrow_forward: **Now playing: {}** :arrow_forward:'.format(player.title))


@client.command(name='dc')
async def dc(ctx):
    if not ctx.voice_client in client.voice_clients:
        await ctx.send('**I\'m not connected to a vc!**')
        return

    else:
        await ctx.voice_client.disconnect()
        await ctx.send('**Successfully Disconnected!**')

@client.command(name='queue')
async def queue_(ctx, url):
    global queue
    
    queue.append(url)
    await ctx.send(f'**\'{url}\' added to queue!**')

@client.command(name='remove')
async def remove(ctx, number):
    global queue

    number += 0

    try:
        del(queue[int(number)])
        await ctx.send(f'**Your queue is now \'{queue}!\'**')
    
    except:
        await ctx.send('**Your queue is either *empty* or the index is *out of range***')

@client.command(name='view')
async def view(ctx):
    global queue
    await ctx.send(f'**Your queue is now \'{queue}!\'**')

@tasks.loop(seconds=20)
async def change_status():
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=choice(status)))

client.run('OTYwMDg1MDY1ODQzNDc0NDcy.YklS5Q.960Yu53rdWRlRnTYARGIZQmxTGw')