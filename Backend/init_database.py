"""
Database Initialization Script
Creates comprehensive database schema if it doesn't exist
"""

from sqlalchemy import create_engine, inspect
from models.database import Base, Account, TeslaConfig, Proxy, BLSAccount
from database.config import DATABASE_URL
from loguru import logger

def init_database():
    """Initialize database with comprehensive schema"""
    try:
        logger.info("🔧 Initializing database...")
        logger.info(f"📁 Database URL: {DATABASE_URL}")
        
        # Create engine
        engine = create_engine(
            DATABASE_URL,
            connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
        )
        
        # Check existing tables
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        if existing_tables:
            logger.info(f"📊 Found {len(existing_tables)} existing tables: {', '.join(existing_tables)}")
        else:
            logger.info("📊 No existing tables found - creating fresh database")
        
        # Create all tables from models
        Base.metadata.create_all(bind=engine)
        
        # Verify tables were created
        inspector = inspect(engine)
        all_tables = inspector.get_table_names()
        
        logger.info(f"✅ Database initialized successfully!")
        logger.info(f"📋 Total tables: {len(all_tables)}")
        for table in all_tables:
            columns = inspector.get_columns(table)
            logger.info(f"   • {table}: {len(columns)} columns")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}")
        return False

if __name__ == "__main__":
    init_database()

