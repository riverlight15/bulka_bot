import discord # Импортируем библиотеку discord.py
import json
import requests
from youtube_dl import YoutubeDL
from asyncio import sleep

from discord.ext import commands,tasks  # Из библиотеки Discord.py импортируем комманды
from config import settings  # Из файлика config (если он у вас есть) импортируем словарь settings

bot = commands.Bot(command_prefix=settings['prefix'])  # Создаем "тело" бота

@bot.event
async def on_ready():  # Event on_ready активируется когда бот готов к использованию
    print('Я запущен!')

#Текстовый блок
@bot.command()
async def команды(ctx):  # Создаем комманду menu
    embed = discord.Embed(color=0xB74BB9, title='Команды')  # Создание Embed
    embed.add_field(name='!привет', value='Бот с вами поздоровается.', inline=True)
    embed.add_field(name='!повтори (*ваш текст*)', value='Бот повторит то, что вы напишете.', inline=True)
    embed.add_field(name='!котик', value='Бот пришлёт фотку котика.', inline=True)
    embed.add_field(name='!пёсик', value='Бот пришлёт фотку пёсика.', inline=True)
    embed.add_field(name='!тег', value='Бот тегнет выбранного участника.', inline=True)
    embed.add_field(name='!погода (*город*)', value='Бот пришлёт погоду в выбранном городе.', inline=True)
    embed.add_field(name='!p (*ссылка на ютуб*)', value='Бот начнёт воспроизведение.', inline=True)
    embed.add_field(name='!pp', value='Бот остановит воспроизведение.', inline=True)
    embed.add_field(name='!r', value='Бот продолжит воспроизведение.', inline=True)
    embed.add_field(name='!s', value='Бот закончит воспроизведение.', inline=True)
    embed.add_field(name='!l', value='Бот выйдет из голосового канала.', inline=True)
    embed.add_field(name='!курс (*валюта 1 в буквенном коде (USD) валюта 2 в буквенном коде (EUR)*', value='Бот выдает актулальный курс выбранных валют.', inline=True)
    await ctx.send(embed=embed)  # Отправка нашего меню сообщением

@bot.command()
async def привет(ctx):  # Создаем комманду hello
    author = ctx.message.author  # Создаем переменную author в которую занесем имя и тэг пользователя.
    await ctx.send(f'Привет, {author.mention}!')  # Используем метод .mention, который "тэгает" пользователя

@bot.command()
async def повтори(ctx, arg):  # Создаем комманду repeat, которая будет повторять всё что мы напишем в чат
    await ctx.send(arg)  # Затем просто выводим arg(переменная в которую занеслось наше сообщение)


@bot.command()
async def тег(ctx, member: discord.Member = None):
    if member == None:
        return
    await ctx.channel.send(f"{ctx.author.mention} считает, что {member.mention} не хватает здесь!")

#Блок отправки фоток
@bot.command()
async def котик(ctx):
    response = requests.get('https://some-random-api.ml/img/cat') # Get-запрос
    json_data = json.loads(response.text) # Извлекаем JSON

    embed = discord.Embed(color = 0xB74BB9, title = 'Котик') # Создание Embed'a
    embed.set_image(url = json_data['link']) # Устанавливаем картинку Embed'a
    await ctx.send(embed = embed)

@bot.command()
async def пёсик(ctx):
    response = requests.get('https://some-random-api.ml/img/dog') # Get-запрос
    json_data = json.loads(response.text) # Извлекаем JSON

    embed = discord.Embed(color = 0xB74BB9, title = 'Пёсик') # Создание Embed'a
    embed.set_image(url = json_data['link']) # Устанавливаем картинку Embed'a
    await ctx.send(embed = embed)

#Блок с погодой
api_key = "0422e4b2b0b51a28867629bafdb5c870"
base_url = "http://api.openweathermap.org/data/2.5/weather?"

@bot.command()
async def погода(ctx, *, city: str):
    city_name = city
    complete_url = base_url + "appid=" + api_key + "&q=" + city_name
    response = requests.get(complete_url)
    x = response.json()
    channel = ctx.message.channel
    if x["cod"] != "404":
        async with channel.typing():
            y = x["main"]
            current_temperature = y["temp"]
            current_temperature_celsiuis = str(round(current_temperature - 273.15))
            current_pressure = y["pressure"]
            current_humidity = y["humidity"]
            z = x["weather"]
            weather_description = z[0]["description"]
            embed = discord.Embed(title=f"Погода в {city_name}", color = 0xB74BB9, timestamp=ctx.message.created_at,)
            embed.add_field(name="Описание", value=f"**{weather_description}**", inline=False)
            embed.add_field(name="Температура(C)", value=f"**{current_temperature_celsiuis}°C**", inline=False)
            embed.add_field(name="Влажность(%)", value=f"**{current_humidity}%**", inline=False)
            embed.add_field(name="Атмосферное давление(hPa)", value=f"**{current_pressure}hPa**", inline=False)
            embed.set_thumbnail(url="https://i.ibb.co/CMrsxdX/weather.png")
            embed.set_footer(text=f"Requested by {ctx.author.name}")
        await channel.send(embed=embed)
    else:
        await channel.send("Город не найден.")

#Музыка

YDL_OPTIONS = {'format': 'worstaudio/best', 'noplaylist': 'True', 'simulate': 'True', 'preferredquality': '192', 'preferredcodec': 'mp3', 'key': 'FFmpegExtractAudio'}
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

@bot.command()
async def l(ctx):
    try:
        voice_client = ctx.message.guild.voice_client
        await voice_client.disconnect()
        await ctx.send(f'{ctx.message.author.mention}, меня выгнал!')
    except:
        await ctx.send(f'{ctx.message.author.mention}, я не поключен!')

@bot.command()
async def pp(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await ctx.send(f'{ctx.message.author.mention}, поставил на паузу.')
        await voice_client.pause()
    else:
        await ctx.send(f'{ctx.message.author.mention}, я не играю!')

@bot.command()
async def r(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_paused():
        await ctx.send(f'{ctx.message.author.mention}, продолжил воспроизведение.')
        await voice_client.resume()
    else:
        await ctx.send(f'{ctx.message.author.mention}, я не играю!')

@bot.command()
async def s(ctx):

    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await voice_client.disconnect()
        await ctx.send(f'{ctx.message.author.mention}, завершил воспроизведение.')
        await voice_client.stop()
    else:
        await ctx.send(f'{ctx.message.author.mention}, я не играю!')

@bot.command()
async def p(ctx, arg):
    global vc

    try:
        voice_channel = ctx.message.author.voice.channel
        vc = await voice_channel.connect()
        await ctx.send(f'{ctx.message.author.mention}, играю {arg}')
    except:
        print('Уже подключен или не удалось подключиться')
        await ctx.send(f'{ctx.message.author.mention}, не удалось подключиться!')

    if vc.is_playing():
        await ctx.send(f'{ctx.message.author.mention}, музыка уже проигрывается.')

    else:
        with YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(arg, download=False)

        URL = info['formats'][0]['url']

        vc.play(discord.FFmpegPCMAudio(executable="C:\\Users\\gfif-\\MediaGet2\\ffmpeg.exe", source=URL, **FFMPEG_OPTIONS))

        while vc.is_playing():
            await sleep(1)
        if not vc.is_paused():
            await vc.disconnect()

#Блок валюта
@bot.command()
async def курс(ctx, base: str, other: str):
    curr1 = base #= input("First Currency: ")
    curr2 = other #= input("Second Currency: ")
    access_key = "dd44405658a1e71fd1d896a14a76f32d"
    res_b = requests.get("http://data.fixer.io/api/latest",
                         params={"access_key": access_key, "base": "EUR", "symbols": curr1})
    res_o = requests.get("http://data.fixer.io/api/latest",
                         params={"access_key": access_key, "base": "EUR", "symbols": curr2})
    if res_b.status_code != 200 or res_o.status_code != 200:
        raise Exception("ERROR: API request unsuccessful.")
    data_b = res_b.json()
    data_o = res_o.json()
    rate_b = data_b["rates"][curr1]
    rate_o = data_o["rates"][curr2]
    rate = round((rate_o / rate_b), 2)
    embed = discord.Embed(color = 0xB74BB9, title = f"Курс {curr1} к {curr2}") # Создание Embed'a
    embed.add_field(name="Валюта", value=f"**1{curr1}={rate}{curr2}**", inline=False)
    embed.set_footer(text=f"Requested by {ctx.author.name}")
    await ctx.send(embed = embed)

bot.run(settings['token'])  # Запускаем бота с помощью нашей библиотеки из файла config (опять же если он у вас есть)