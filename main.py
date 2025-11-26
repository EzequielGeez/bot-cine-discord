import discord
from discord.ext import commands
import os
import re
from keep_alive import keep_alive
# Importamos la búsqueda de Google
from googlesearch import search

# CONFIGURACIÓN
DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'✅ Bot conectado como {bot.user.name}')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="películas 🍿"))

@bot.command(name='peli')
async def buscar_peli(ctx, *, nombre):
    await ctx.send(f"🔎 Buscando **'{nombre}'** en Google...")
    
    try:
        # 1. Buscamos en Google
        # "Nombre pelicula site:imdb.com" nos da la ficha exacta
        query = f"site:imdb.com/title {nombre} movie"
        
        # Buscamos 1 resultado
        resultados = list(search(query, num_results=1, advanced=True))
        
        if not resultados:
            await ctx.send("❌ Google no encontró nada. Prueba con el nombre en inglés o el año.")
            return

        # Tomamos el primer resultado
        resultado = resultados[0]
        url_imdb = resultado.url
        
        # Limpiamos el título
        titulo = resultado.title.replace(" - IMDb", "").replace("IMDb", "")
        descripcion = resultado.description
        
        # 2. Extraer el ID de IMDb (tt1234567) de la URL
        match = re.search(r'tt\d+', url_imdb)
        
        if not match:
            await ctx.send("❌ Encontré la web pero no el ID de la película.")
            return
            
        imdb_id = match.group(0)
        
        # 3. Construimos el link de VidSrc
        url_ver = f"https://vidsrc.xyz/embed/movie?imdb={imdb_id}"

        # 4. Crear la tarjeta
        embed = discord.Embed(title=f"🎬 {titulo}", description=descripcion[:200] + "...", color=0xDB4437) # Rojo Google
        embed.add_field(name="🆔 ID IMDb", value=imdb_id, inline=True)
        embed.add_field(name="🍿 Ver Online", value=f"[Haz clic aquí para ver la película]({url_ver})", inline=False)
        embed.set_footer(text="Búsqueda vía Google + VidSrc")
        
        await ctx.send(embed=embed)

    except Exception as e:
        print(f"Error: {e}")
        await ctx.send(f"Error técnico: {e}")

if DISCORD_TOKEN:
    keep_alive()
    bot.run(DISCORD_TOKEN)
