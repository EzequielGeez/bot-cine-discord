import discord
from discord.ext import commands
import os
from keep_alive import keep_alive
# Importamos la librería de IMDb (cinemagoer)
from imdb import Cinemagoer

# --- CONFIGURACIÓN ---
# Render buscará esto en las "Environment Variables"
DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')

# Configuración del bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Iniciamos la herramienta de IMDb
ia = Cinemagoer()

@bot.event
async def on_ready():
    print(f'✅ Bot conectado como {bot.user.name}')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="películas gratis 🍿"))

@bot.command(name='peli')
async def buscar_peli(ctx, *, nombre):
    await ctx.send(f"🔎 Buscando **'{nombre}'**... dame unos segundos.")
    
    try:
        # 1. Buscar la película en IMDb
        busqueda = ia.search_movie(nombre)
        
        if not busqueda:
            await ctx.send("❌ No encontré nada con ese nombre. Intenta ser más específico.")
            return

        # Tomamos el primer resultado
        movie_result = busqueda[0]
        movie_id = movie_result.movieID
        
        # 2. Obtener datos completos (Sinopsis, cover, rating)
        # Esto tarda un poco porque descarga la info de IMDb
        movie = ia.get_movie(movie_id)
        
        titulo = movie.get('title', 'Sin título')
        year = movie.get('year', '????')
        rating = movie.get('rating', '?')
        
        # Manejo seguro de la sinopsis (plot)
        plot = "Sin descripción disponible."
        if 'plot outline' in movie:
            plot = movie['plot outline']
        elif 'plot' in movie:
            plot = movie['plot'][0]
            
        cover_url = movie.get('full-size cover url', None)

        # 3. Generar el Link de VidSrc (usando el ID de IMDb)
        # IMPORTANTE: VidSrc necesita el prefijo "tt" antes del número
        url_ver = f"https://vidsrc.xyz/embed/movie?imdb=tt{movie_id}"

        # 4. Crear la Tarjeta (Embed)
        embed = discord.Embed(title=f"🎬 {titulo} ({year})", description=plot[:300] + "...", color=0xf5c518) # Amarillo IMDb
        embed.add_field(name="⭐ Puntuación", value=f"{rating}/10", inline=True)
        embed.add_field(name="🍿 Ver Online", value=f"[Haz clic aquí para ver la película]({url_ver})", inline=False)
        
        if cover_url:
            embed.set_thumbnail(url=cover_url)
        
        embed.set_footer(text="Servidor: VidSrc | Datos: IMDb")

        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f"Ocurrió un error inesperado: {e}")
        print(f"Error: {e}")

# --- ARRANQUE ---
if DISCORD_TOKEN:
    keep_alive()
    bot.run(DISCORD_TOKEN)
else:
    print("❌ ERROR: No encontré el DISCORD_TOKEN en las variables de entorno.")
