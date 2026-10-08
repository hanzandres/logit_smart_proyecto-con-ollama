# ============================================================
# CONEXIÓN A MONGODB ATLAS (Clúster del Profesor)
# ============================================================

from pymongo import MongoClient
import os

# Credenciales proporcionadas
MONGO_USER = "hector1985"
MONGO_PASSWORD = "Aime131985"
MONGO_CLUSTER = "utvt.qqqotrr.mongodb.net"
DB_NAME = "HanzAG_D73"

# Construcción de la URI de conexión segura con Atlas
MONGO_URI = f"mongodb+srv://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_CLUSTER}/?retryWrites=true&w=majority"

def obtener_conexion_db():
    """
    Establece y devuelve la conexión a la base de datos MongoDB Atlas.
    """
    try:
        # Inicializar cliente de PyMongo con un timeout de 5 segundos
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        
        # Comprobar conexión con un comando ping
        client.admin.command('ping')
        
        db = client[DB_NAME]
        print(f"✅ ¡Conexión exitosa a MongoDB Atlas! Base de datos activa: '{DB_NAME}'")
        return db
        
    except Exception as e:
        print(f"❌ Error al conectar a MongoDB Atlas: {e}")
        return None

if __name__ == "__main__":
    db = obtener_conexion_db()
    if db is not None:
        print("📁 Colecciones existentes en el clúster:", db.list_collection_names())