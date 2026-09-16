import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import pool
from config import Config
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

connection_pool = None

def init_db():
    """Initialize database connection pool and create tables"""
    global connection_pool
    
    try:
        
        connection_pool = psycopg2.pool.SimpleConnectionPool(
            1, 20,
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            database=Config.DB_NAME,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD
        )
        
        if connection_pool:
            logger.info("Database connection pool created successfully")
            
            
            create_tables()
        else:
            logger.error("Failed to create connection pool")
            
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise

def get_db_connection():
    """Get a connection from the pool"""
    try:
        return connection_pool.getconn()
    except Exception as e:
        logger.error(f"Error getting connection from pool: {str(e)}")
        raise

def return_db_connection(conn):
    """Return a connection to the pool"""
    try:
        connection_pool.putconn(conn)
    except Exception as e:
        logger.error(f"Error returning connection to pool: {str(e)}")

def create_tables():
    """Create necessary database tables"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS uploads (
                id SERIAL PRIMARY KEY,
                filename VARCHAR(255) NOT NULL,
                file_path VARCHAR(500) NOT NULL,
                file_type VARCHAR(50) NOT NULL,
                file_size INTEGER NOT NULL,
                upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recognition_results (
                id SERIAL PRIMARY KEY,
                upload_id INTEGER REFERENCES uploads(id) ON DELETE CASCADE,
                recognized_text TEXT NOT NULL,
                confidence_score FLOAT,
                processing_time FLOAT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        logger.info("Database tables created successfully")
        
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Error creating tables: {str(e)}")
        raise
    finally:
        if conn:
            cursor.close()
            return_db_connection(conn)

def close_db_pool():
    """Close all connections in the pool"""
    global connection_pool
    if connection_pool:
        connection_pool.closeall()
        logger.info("Database connection pool closed")