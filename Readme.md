# Descripcion del proyecto
Este es un bot de Discord desarrollado en Python que permite a los usuarios interactuar con la Fake Store API. Proporciona funciones como listar productos, ver detalles de productos específicos, agregar productos a un carrito personal, y almacenar productos en una base de datos PostgreSQL.


# Lista de tecnologías y bibliotecas:

Python 3.12

Discord.py para interactuar con Discord.

aiohttp para manejar las solicitudes HTTP de manera asíncrona.

PostgreSQL para almacenar información.

psycopg2-binary para la conexión con PostgreSQL.

dotenv para el manejo seguro de variables de entorno.



# Guía de instalacion:
- Clonar el repositorio
- Instalar las dependencias: pip install -r requirements.txt
- Configurar archivo .env:
  
BOT_TOKEN=tu_token_de_discord

DATABASE_URL=postgresql://usuario:contraseña@localhost/fakestore_bot



# Lista de Comandos:


!products: Lista todos los productos disponibles en la Fake Store API.

!product <id>: Muestra la información de un producto específico por su ID.

!category <nombre>: Muestra productos de una categoría específica.

!addtocart <id>: Añade un producto al carrito del usuario.

!cart: Muestra el contenido del carrito del usuario.

!addtodb <id>: Almacena el producto en la base de datos PostgreSQL.


### Ejemplos de Uso:

!product 3: Devuelve detalles del producto con ID 3.

!category electronics: Lista productos de la categoría "electronics".
