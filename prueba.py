import discord
import aiohttp

import os
from keep_alive import keep_alive
from dotenv import load_dotenv
load_dotenv()

user_carts = {}

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



# Obtain list of productss
async def getProductListFromApi():
    url = 'https://fakestoreapi.com/products'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                product_names = [product['title'] for product in data]
                return '\n'.join(product_names)
            else:
                return 'Error getting the list of products'
            
# Obtain products by category         
async def getProductsByCategory(category):
    url = f'https://fakestoreapi.com/products/category/{category}'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                product_names = [product['title'] for product in data]
                return '\n'.join(product_names)
            else:
                return f'Error getting products from category {category}'
            


# Add products to cart
async def addToCart(user_id, product_id):
    if user_id not in user_carts:
        user_carts[user_id] = []

    product_info = await getProductById(product_id)
    if product_info != 'Error getting the product':
        user_carts[user_id].append(product_info)
        return f"Product {product_id} added to your cart!"
    return product_info
    
            

# Obtain specific product by Id
async def getProductById(product_id):
    url = f'https://fakestoreapi.com/products/{product_id}'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                product = await response.json()
                return f"Product: {product['title']}\nPrice: ${product['price']}\nDescription: {product['description']}"
            else:
                return 'Error getting the product'

# message event
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!pokemons'):
        pokemon_list = await getPokemonListFromApi()
        await message.channel.send(pokemon_list)

    elif message.content.startswith('!products'):
        product_list = await getProductListFromApi()
        await message.channel.send(product_list)

    elif message.content.startswith('!product'):
        try:
            product_id = int(message.content.split()[1])  # Obtiene el ID del mensaje
            product_info = await getProductById(product_id)
            await message.channel.send(product_info)
        except (IndexError, ValueError):
            await message.channel.send("Please provide a valid product ID, e.g., `!product 1`.")

    elif message.content.startswith('!category'):
        try:
            category = message.content.split()[1]  # Obtenemos la categoría
            products = await getProductsByCategory(category)
            await message.channel.send(products)
        except IndexError:
            await message.channel.send("Please provide a valid category, e.g., `!category electronics`.")

    elif message.content.startswith('!addtocart'):
        try:
            product_id = int(message.content.split()[1])
            response = await addToCart(message.author.id, product_id)
            await message.channel.send(response)
        except (IndexError, ValueError):
            await message.channel.send("Please provide a valid product ID, e.g., `!addtocart 1`.")

    elif message.content.startswith('!cart'):
        cart = user_carts.get(message.author.id, [])
        if cart:
            await message.channel.send('\n'.join(cart))
        else:
            await message.channel.send("Your cart is empty.")



#keeps the bot alive with a webserver from Flask
keep_alive()

token = os.environ.get("BOT_TOKEN")
if token:
  client.run(token)
else:
  print("Error: BOT_TOKEN .env variable not found.")