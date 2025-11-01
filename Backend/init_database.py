"""
Database Initialization Script
Creates comprehensive database schema if it doesn't exist
Auto-migrates existing tables to add missing columns
"""

from sqlalchemy import create_engine, inspect, text
from models.database import Base, Account, TeslaConfig, Proxy, BLSAccount
from database.config import DATABASE_URL
from loguru import logger

def init_database():
    """Initialize database with comprehensive schema and auto-migration"""
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
            
            # Auto-migrate proxies table if it exists but is missing columns
            if 'proxies' in existing_tables:
                _migrate_proxies_table(engine, inspector)
        else:
            logger.info("📊 No existing tables found - creating fresh database")
        
        # Create all tables from models (only creates missing tables)
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

def _migrate_proxies_table(engine, inspector):
    """Auto-migrate proxies table to add missing columns"""
    try:
        # Get current columns
        columns = inspector.get_columns('proxies')
        column_names = [col['name'] for col in columns]
        
        logger.info(f"🔍 Checking proxies table schema ({len(column_names)} columns)...")
        
        # Check for missing columns
        migrations_needed = []
        
        if 'usage_count' not in column_names:
            migrations_needed.append('usage_count')
        
        if 'last_used' not in column_names:
            migrations_needed.append('last_used')
        
        if not migrations_needed:
            logger.info("✅ Proxies table schema is up to date")
            return
        
        # Run migrations
        logger.info(f"🔄 Adding missing columns to proxies table: {', '.join(migrations_needed)}")
        
        with engine.connect() as conn:
            for column in migrations_needed:
                if column == 'usage_count':
                    conn.execute(text("ALTER TABLE proxies ADD COLUMN usage_count INTEGER DEFAULT 0"))
                    conn.execute(text("UPDATE proxies SET usage_count = 0 WHERE usage_count IS NULL"))
                    logger.info("✅ Added 'usage_count' column")
                
                elif column == 'last_used':
                    conn.execute(text("ALTER TABLE proxies ADD COLUMN last_used TIMESTAMP NULL"))
                    logger.info("✅ Added 'last_used' column")
            
            conn.commit()
        
        logger.info("✅ Proxies table migration completed successfully!")
        
    except Exception as e:
        logger.warning(f"⚠️ Could not auto-migrate proxies table: {e}")
        logger.info("💡 You may need to run 'python fix_proxy_table.py' manually")

if __name__ == "__main__":
    init_database()

