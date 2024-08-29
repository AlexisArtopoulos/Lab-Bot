import discord
import aiohttp

import os
from keep_alive import keep_alive
from dotenv import load_dotenv
load_dotenv()

# Need to check what intents are later
intents = discord.Intents.default()
intents.message_content = True 
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print("I'm in")
    print(client.user)

async def getPokemonListFromApi():
    url = 'https://pokeapi.co/api/v2/pokemon?limit=10'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                pokemon_names = [pokemon['name'] for pokemon in data['results']]
                return '\n'.join(pokemon_names)
            else:
                return 'Error getting the list from Pokémons'


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!pokemons'):
        pokemon_list = await getPokemonListFromApi()
        await message.channel.send(pokemon_list)

#keeps the bot alive with a webserver from Flask
keep_alive()

token = os.environ.get("BOT_TOKEN")
if token:
  client.run(token)
else:
  print("Error: BOT_TOKEN .env variable not found.")