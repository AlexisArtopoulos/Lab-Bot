import discord
import aiohttp
import os
import psycopg2
from psycopg2 import OperationalError
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")

# Conexión a la base de datos
try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
except OperationalError as e:
    print(f"Error connecting to database: {e}")
    exit()

# Configuración del bot
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Mensaje al iniciar el bot
@client.event
async def on_ready():
    print(f"Bot {client.user} is now running.")

# Funciones relacionadas con la base de datos
async def add_user_to_db(user_id, username):
    """Agrega un usuario a la base de datos si no existe."""
    query = """
    INSERT INTO users (user_id, username)
    VALUES (%s, %s)
    ON CONFLICT (user_id) DO NOTHING;
    """
    try:
        cursor.execute(query, (user_id, username))
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Error adding user to database: {e}")

async def get_or_create_cart(user_id):
    """Obtiene o crea un carrito para el usuario."""
    await add_user_to_db(user_id, "user")
    query_cart = """
    SELECT cart_id FROM carts WHERE user_id = %s;
    """
    cursor.execute(query_cart, (user_id,))
    cart = cursor.fetchone()

    if not cart:
        query_create_cart = """
        INSERT INTO carts (user_id) VALUES (%s) RETURNING cart_id;
        """
        cursor.execute(query_create_cart, (user_id,))
        cart = cursor.fetchone()

    conn.commit()
    return cart[0]

async def add_product_to_cart(user_id, product_id, product_info):
    """Agrega un producto al carrito del usuario."""
    cart_id = await get_or_create_cart(user_id)
    query = """
    INSERT INTO cart_items (cart_id, product_id, title, price, quantity)
    VALUES (%s, %s, %s, %s, 1)
    ON CONFLICT (cart_id, product_id) DO UPDATE SET quantity = cart_items.quantity + 1;
    """
    try:
        cursor.execute(query, (cart_id, product_info['id'], product_info['title'], product_info['price']))
        conn.commit()
        return f"Product '{product_info['title']}' added to your cart."
    except Exception as e:
        conn.rollback()
        print(f"Error adding product to cart: {e}")
        return "Error adding product to cart."

async def store_product_in_db(product):
    """Guarda un producto en la base de datos."""
    query = """
    INSERT INTO cart_items (product_id, title, price)
    VALUES (%s, %s, %s)
    ON CONFLICT (product_id) DO NOTHING;
    """
    try:
        cursor.execute(query, (product['id'], product['title'], product['price']))
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Error storing product: {e}")

async def get_cart_for_user(user_id):
    """Obtiene los productos en el carrito de un usuario."""
    cart_id = await get_or_create_cart(user_id)
    query = """
    SELECT title, price, quantity
    FROM cart_items
    WHERE cart_id = %s;
    """
    cursor.execute(query, (cart_id,))
    items = cursor.fetchall()

    if items:
        return "\n".join([f"**Product:** {item[0]}, **Price:** ${item[1]}, **Quantity:** {item[2]}" for item in items])
    else:
        return "Your cart is empty."

# Funciones relacionadas con la API
async def fetch_product_from_api(product_id):
    """Obtiene un producto de la Fake Store API por su ID."""
    url = f"https://fakestoreapi.com/products/{product_id}"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return None
        except aiohttp.ClientError as e:
            print(f"Error fetching product: {e}")
            return None

async def fetch_products_from_api():
    """Obtiene todos los productos de la Fake Store API."""
    url = "https://fakestoreapi.com/products"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return []
        except aiohttp.ClientError as e:
            print(f"Error fetching products: {e}")
            return []

async def fetch_products_by_category(category):
    """Obtiene productos de una categoría específica."""
    url = f"https://fakestoreapi.com/products/category/{category}"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return []
        except aiohttp.ClientError as e:
            print(f"Error fetching category products: {e}")
            return []

# Comandos del bot
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("!products"):
        products = await fetch_products_from_api()
        response = "\n".join([f"{product['id']}: {product['title']}" for product in products])
        await message.channel.send(response if response else "No products found.")

    elif message.content.startswith("!product"):
        try:
            product_id = int(message.content.split()[1])
            product = await fetch_product_from_api(product_id)
            if product:
                await message.channel.send(f"**Product:** {product['title']}\n**Price:** ${product['price']}\n**Description:** {product['description']}")
            else:
                await message.channel.send("Product not found.")
        except (IndexError, ValueError):
            await message.channel.send("Please provide a valid product ID, e.g., `!product 1`.")

    elif message.content.startswith("!category"):
        try:
            category = message.content.split()[1]
            products = await fetch_products_by_category(category)
            response = "\n".join([f"{product['id']}: {product['title']}" for product in products])
            await message.channel.send(response if response else f"No products found in category '{category}'.")
        except IndexError:
            await message.channel.send("Please provide a valid category, e.g., `!category electronics`.")

    elif message.content.startswith("!addtocart"):
        try:
            product_id = int(message.content.split()[1])
            product = await fetch_product_from_api(product_id)
            if product:
                response = await add_product_to_cart(message.author.id, product_id, product)
                await message.channel.send(response)
            else:
                await message.channel.send("Product not found.")
        except (IndexError, ValueError):
            await message.channel.send("Please provide a valid product ID, e.g., `!addtocart 1`.")

    elif message.content.startswith("!cart"):
        response = await get_cart_for_user(message.author.id)
        await message.channel.send(response)

    elif message.content.startswith("!addtodb"):
        try:
            product_id = int(message.content.split()[1])
            product = await fetch_product_from_api(product_id)
            if product:
                await store_product_in_db(product)
                await message.channel.send(f"Product '{product['title']}' added to the database.")
            else:
                await message.channel.send("Product not found.")
        except (IndexError, ValueError):
            await message.channel.send("Please provide a valid product ID, e.g., `!addtodb 1`.")

# Iniciar el bot
if BOT_TOKEN:
    client.run(BOT_TOKEN)
else:
    print("Error: BOT_TOKEN not found in .env.")
