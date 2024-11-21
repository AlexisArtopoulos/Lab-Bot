# Discord Bot - Fake Store API Integration

## Descripción

Este bot de Discord, desarrollado en Python, permite a los usuarios interactuar con la **Fake Store API**. Ofrece funcionalidades avanzadas como listar productos, ver detalles específicos, agregar productos a un carrito personal persistente, y almacenar datos en una base de datos PostgreSQL. Su diseño se centra en la simplicidad y escalabilidad, utilizando bibliotecas modernas y prácticas de desarrollo sólidas.

---

## Tecnologías Utilizadas

El bot utiliza las siguientes tecnologías y bibliotecas:

- **Python 3.12**: Lenguaje base para el desarrollo.
- **discord.py**: Biblioteca para interactuar con la API de Discord.
- **aiohttp**: Cliente HTTP asíncrono para realizar solicitudes a la Fake Store API.
- **PostgreSQL**: Base de datos para almacenar usuarios, carritos y productos.
- **psycopg2-binary**: Conector de Python para PostgreSQL.
- **python-dotenv**: Manejo seguro de variables de entorno.
- **Flask**: Usado para mantener el bot activo.

---

## Funcionalidades

- **Listar Productos**: Muestra todos los productos disponibles en la Fake Store API.
- **Ver Detalles de Productos**: Obtiene información detallada de un producto específico por su ID.
- **Filtrar por Categorías**: Lista productos según la categoría seleccionada.
- **Carrito de Compras Persistente**:
  - Agregar productos al carrito.
  - Mostrar el contenido del carrito.
  - Manejar cantidades de productos.
  - Eliminar productos del carrito.
- **Guardar Productos en la Base de Datos**: Permite almacenar productos directamente en PostgreSQL.

---

## Instalación

### 1. Clonar el Repositorio

```bash
git clone https://github.com/tu-usuario/tu-repositorio.git
cd tu-repositorio
pip install -r requirements.txt

COMANDOS:

!products	Lista todos los productos disponibles en la Fake Store API.
!product <id>	Muestra la información de un producto específico por su ID.
!category <nombre>	Lista productos de una categoría específica (ej. electronics, jewelery).
!addtocart <id>	Añade el producto con el ID especificado al carrito del usuario.
!cart	Muestra el contenido del carrito del usuario.
!addtodb <id>	Almacena el producto con el ID especificado en la base de datos PostgreSQL.
!removefromcart <id>	Elimina el producto con el ID especificado del carrito del usuario.


Ejemplos de Uso
!products: Muestra todos los productos disponibles.
!product 5: Devuelve detalles del producto con ID 5.
!category electronics: Lista productos de la categoría "electronics".
!addtocart 3: Agrega el producto con ID 3 al carrito del usuario.
!cart: Muestra los productos en el carrito.
!removefromcart 3: Elimina el producto con ID 3 del carrito.

Estructura del proyecto
├── bot.py               # Archivo principal del bot
├── keep_alive.py        # Módulo para mantener el bot activo NO FUNCIONA EN VSC, SOLO REPLIT
├── requirements.txt     # Dependencias del proyecto
├── .env                 # Variables de entorno
├── README.md            # Documentación técnica
