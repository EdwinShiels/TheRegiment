# TheRegiment - Database Connection Module
# NeonDB connection with retry logic

import asyncio
import os
from typing import Optional
import asyncpg
from asyncpg import Connection, Pool
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Global connection pool
_connection_pool: Optional[Pool] = None


async def connect_to_db() -> Pool:
    """
    Establish connection to NeonDB with retry logic.
    
    Returns:
        asyncpg connection pool
        
    Raises:
        ConnectionError: If all retry attempts fail
        ValueError: If NEON_DB_URL is not configured
    """
    global _connection_pool
    
    if _connection_pool and not _connection_pool.is_closing():
        print("Using existing database connection pool")
        return _connection_pool
    
    database_url = os.getenv("NEON_DB_URL")
    if not database_url:
        error_msg = "NEON_DB_URL environment variable not set"
        print(error_msg)
        raise ValueError(error_msg)
    
    # Ensure SSL mode is required for NeonDB
    if "sslmode=require" not in database_url:
        database_url += "?sslmode=require" if "?" not in database_url else "&sslmode=require"
    
    max_retries = 3
    base_delay = 1.0  # seconds
    
    for attempt in range(1, max_retries + 1):
        try:
            print(
                f"Attempting database connection (attempt {attempt}/{max_retries})")
            
            # Create connection pool with optimized settings
            _connection_pool = await asyncpg.create_pool(
                database_url,
                min_size=2,
                max_size=10,
                command_timeout=30,
                server_settings={
                    'application_name': 'theregiment_backend',
                    'timezone': 'UTC'
                }
            )
            
            # Test the connection
            async with _connection_pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
            
            print(
                "Database connection established successfully")
            
            return _connection_pool
            
        except Exception as error:
            error_context = {
                "attempt": attempt,
                "max_retries": max_retries,
                "error_type": type(error).__name__,
                "database_url_masked": _mask_database_url(database_url)
            }
            
            if attempt < max_retries:
                delay = base_delay * (2 ** (attempt - 1))  # Exponential backoff
                print(
                    f"Database connection failed, retrying in {delay}s")
                await asyncio.sleep(delay)
            else:
                print(f"Failed to connect to database after {max_retries} attempts: {error}")
                raise ConnectionError(f"Failed to connect to database after {max_retries} attempts: {error}")


async def get_connection() -> Connection:
    """
    Get a database connection from the pool.
    
    Returns:
        Database connection
        
    Raises:
        ConnectionError: If no pool is available
    """
    if not _connection_pool:
        await connect_to_db()
    
    if not _connection_pool:
        raise ConnectionError("Database connection pool not available")
    
    return await _connection_pool.acquire()


async def release_connection(conn: Connection) -> None:
    """
    Release a database connection back to the pool.
    
    Args:
        conn: Database connection to release
    """
    if _connection_pool and conn:
        await _connection_pool.release(conn)


async def close_db_pool() -> None:
    """
    Close the database connection pool.
    """
    global _connection_pool
    
    if _connection_pool:
        print("Closing database connection pool")
        await _connection_pool.close()
        _connection_pool = None


def _mask_database_url(url: str) -> str:
    """
    Mask sensitive information in database URL for logging.
    
    Args:
        url: Database URL to mask
        
    Returns:
        Masked URL with credentials hidden
    """
    if not url:
        return "None"
    
    # Replace password with asterisks
    import re
    masked = re.sub(r'://([^:]+):([^@]+)@', r'://\1:***@', url)
    return masked


async def execute_query(query: str, *args, fetch_one: bool = False, fetch_all: bool = False) -> any:
    """
    Execute a database query with connection management.
    
    Args:
        query: SQL query to execute
        *args: Query parameters
        fetch_one: Whether to fetch one result
        fetch_all: Whether to fetch all results
        
    Returns:
        Query result or None
        
    Raises:
        Exception: Database execution errors
    """
    conn = None
    try:
        conn = await get_connection()
        
        if fetch_one:
            result = await conn.fetchrow(query, *args)
        elif fetch_all:
            result = await conn.fetch(query, *args)
        else:
            result = await conn.execute(query, *args)
        
        print(
            "Database query executed successfully")
        
        return result
        
    except Exception as error:
        print(f"Database execution error: {error}")
        raise
        
    finally:
        if conn:
            await release_connection(conn) 