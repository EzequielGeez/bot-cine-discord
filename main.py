import discord
from discord.ext import commands
import os
import re
from keep_alive import keep_alive
# Usamos la nueva librería de búsqueda
from duckduckgo_search import DDGS

# CONFIGURACIÓN
DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'✅ Bot conectado como {bot.user.name}')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="películas gratis 🍿"))

@bot.command(name='peli')
async def buscar_peli(ctx, *, nombre):
    await ctx.send(f"🔎 Buscando enlaces para **'{nombre}'**...")
    
    try:
        # Usamos DuckDuckGo para buscar el link de IMDb de la película
        # El truco es buscar "site:imdb.com/title [nombre pelicula]"
        results = DDGS().text(f"site:imdb.com/title {nombre} movie", max_results=1)
        
        if not results:
            await ctx.send("❌ No encontré esa película. Prueba poniendo el nombre en inglés o el año.")
            return

        # Tomamos el primer resultado
        resultado = results[0]
        url_imdb = resultado['href']
        titulo_encontrado = resultado['title'].replace(" - IMDb", "")
        
        # Extraer el ID de IMDb (ejemplo: tt1234567) usando expresiones regulares
        match = re.search(r'tt\d+', url_imdb)
        
        if not match:
            await ctx.send("❌ Encontré un enlace, pero no pude sacar el ID. Intenta otra.")
            return
            
        imdb_id = match.group(0)
        
        # Construimos el link de VidSrc
        url_ver = f"https://vidsrc.xyz/embed/movie?imdb={imdb_id}"

        # Creamos la tarjeta
        embed = discord.Embed(title=f"🎬 {titulo_encontrado}", description=f"Encontrado en IMDb: {imdb_id}", color=0x00ff00)
        embed.add_field(name="🍿 Ver Online", value=f"[Haz clic aquí para ver la película]({url_ver})", inline=False)
        embed.set_footer(text="Fuente: DuckDuckGo + VidSrc")
        
        await ctx.send(embed=embed)

    except Exception as e:
        print(f"Error: {e}")
        await ctx.send(f"Ocurrió un error técnico: {e}")

if DISCORD_TOKEN:
    keep_alive()
    bot.run(DISCORD_TOKEN)
