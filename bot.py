import discord
import aiohttp
import os
import psycopg2
import requests
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


async def ntfy(text):
    requests.post("https://ntfy.sh/FakeStoreBot",
    data=text.encode(encoding='utf-8'))


# Mensaje al iniciar el bot
@client.event
async def on_ready():
    await ntfy("FakeStoreBot is now running")
    print(f"Bot {client.user} is now running.")

async def add_user_to_db(user_id, username):
    """Agrega un usuario a la base de datos si no existe. Retorna True si se creó un nuevo usuario."""
    query = """
    INSERT INTO users (user_id, username)
    VALUES (%s, %s)
    ON CONFLICT (user_id) DO NOTHING
    RETURNING user_id;
    """
    try:
        cursor.execute(query, (user_id, username))
        new_user = cursor.fetchone()  # Verifica si se insertó un nuevo usuario
        conn.commit()
        return new_user is not None  # Retorna True si se creó un usuario, False si ya existía
    except Exception as e:
        conn.rollback()
        print(f"Error adding user to database: {e}")
        return False


async def get_or_create_cart(user_id, username):
    """Obtiene o crea un carrito para el usuario."""
    user_created = await add_user_to_db(user_id, username)
    if user_created:
        await ntfy(f"New user created: {username}")
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

async def add_product_to_cart(user_id, product_id, product_info, username):
    """Agrega un producto al carrito del usuario."""
    cart_id = await get_or_create_cart(user_id, username)  # Pasar username
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

async def search_meli(query):
    """Realiza una búsqueda en Mercado Libre y retorna el primer resultado."""
    search_url = f"https://api.mercadolibre.com/sites/MLA/search?q={query}"

    async with aiohttp.ClientSession() as session:
        async with session.get(search_url) as response:
            if response.status == 200:
                data = await response.json()
                if data.get("paging", {}).get("total", 0) == 0:
                    return None  # No se encontraron resultados
                return data["results"][0]  # Retornar el primer resultado
            else:
                raise Exception(f"Error: Mercado Libre API returned {response.status}")


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

async def get_cart_for_user(user_id, username):
    """Obtiene los productos en el carrito de un usuario."""
    cart_id = await get_or_create_cart(user_id, username)  # Ahora pasa 'username'
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

async def get_fake_store_product(product_id):
    """Obtiene un producto por ID desde la Fake Store API."""
    url = f"https://fakestoreapi.com/products/{product_id}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.json()
            else:
                return None  # Si no se encuentra el producto o hay un error

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

    username = message.author.display_name if isinstance(message.author, discord.Member) else message.author.name

    if message.content.startswith("!help"):
        help_message = """
**Bot Commands:**

1. `!products` - Lista todos los productos disponibles en la Fake Store API.
2. `!product <id>` - Muestra la información de un producto específico por su ID.
3. `!category <nombre>` - Lista productos de una categoría específica (ej. `electronics`, `jewelery`).
4. `!addtocart <id>` - Añade el producto con el ID especificado al carrito del usuario.
5. `!cart` - Muestra el contenido del carrito del usuario.
6. `!addtodb <id>` - Almacena el producto con el ID especificado en la base de datos PostgreSQL.
7. `!searchmeli <nombre del producto>` - Muestra la información de un producto específico por su nombre en mercado libre.

**Ejemplos de Uso:**
- `!product 5`: Muestra los detalles del producto con ID 5.
- `!category electronics`: Lista productos de la categoría "electronics".
- `!addtocart 3`: Agrega el producto con ID 3 al carrito.
- `!cart`: Muestra los productos actualmente en el carrito.
"""
        await message.channel.send(help_message)

    if message.content.startswith("!products"):
        products = await fetch_products_from_api()
        response = "\n".join([f"{product['id']}: {product['title']}" for product in products])
        await message.channel.send(response if response else "No products found.")

    elif message.content.startswith("!product"):
        try:
            # Obtener el ID del producto después del comando
            product_id = int(message.content.split()[1])

            # Llamar a la función para obtener el producto
            product = await get_fake_store_product(product_id)
            if not product:
                await message.channel.send("No se encontró el producto en la Fake Store API.")
                return

            # Crear el embed para mostrar el resultado
            embed = discord.Embed(
                title=product["title"],
                url=product.get("url", "https://fakestoreapi.com"),  # Fake Store no tiene enlaces directos
                description=f"💰 ***{product['price']} USD***\n\n"
                            f"❔ ***{product['category'].capitalize()}***\n\n"
                            f":clipboard: ***{product['description']}***"
            )
            embed.set_author(name="Fake Store API Result")
            embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/a/a3/Fake_Store_Logo.png")
            embed.set_image(url=product["image"])
            embed.set_footer(text="Powered by Fake Store API")
            embed.timestamp = discord.utils.utcnow()
            await message.channel.send(embed=embed)

        except (IndexError, ValueError):
            await message.channel.send("Por favor, proporciona un ID válido de producto, e.g., `!fakeproduct 5`.")
        except Exception as e:
            print(f"Error en el comando !fakeproduct: {e}")
            await message.channel.send("Hubo un error al obtener el producto. Inténtalo más tarde.")

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
                response = await add_product_to_cart(message.author.id, product_id, product, username)
                await message.channel.send(response)
            else:
                await message.channel.send("Product not found.")
        except (IndexError, ValueError):
            await message.channel.send("Please provide a valid product ID, e.g., `!addtocart 1`.")

    elif message.content.startswith("!cart"):
        username = message.author.display_name if isinstance(message.author, discord.Member) else message.author.name
        response = await get_cart_for_user(message.author.id, username)
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

    elif message.content.startswith("!searchmeli"):
        try:
            # Obtener el texto de búsqueda después del comando
            query = message.content[len("!searchmeli "):].strip()
            if not query:
                await message.channel.send("Por favor, proporciona un término de búsqueda, e.g., `!search PlayStation`.")
                return

            # Llamar a la función para buscar en Mercado Libre
            result = await search_meli(query)
            if not result:
                await message.channel.send("No puedo buscar esas cosas 😢")
                return

            # Crear el embed para mostrar el resultado
            embed = discord.Embed(
                title=result["title"],
                url=result["permalink"],
                description=f"💰 ***{result['price']}*** {result['currency_id']}\n"
                            f"{'✅' if result['shipping']['free_shipping'] else '❌'} Free shipping\n\n"
                            f"❔ ***{result['condition'].upper()}***\n\n"
            )
            embed.set_author(name=f'Resultados para "{query}"')
            embed.set_thumbnail(url="https://www.expoknews.com/wp-content/uploads/2020/03/1200px-MercadoLibre.svg-1.png")
            embed.set_image(url=result["thumbnail"])
            embed.set_footer(text="Powered by Mercado Libre")
            embed.timestamp = discord.utils.utcnow()

            await message.channel.send(embed=embed)

        except Exception as e:
            print(f"Error en el comando !search: {e}")
            await message.channel.send("Hubo un error al realizar la búsqueda. Inténtalo más tarde.")

# Iniciar el bot
if BOT_TOKEN:
    client.run(BOT_TOKEN)
else:
    print("Error: BOT_TOKEN not found in .env.")
