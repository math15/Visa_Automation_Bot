"""
Proxy Management CLI Tool
Easily add, update, remove, and list proxies for BLS registration
"""

import sys
from datetime import datetime
from sqlalchemy.orm import Session
from database.config import SessionLocal
from models.database import Proxy
from loguru import logger

def list_proxies(db: Session):
    """List all proxies in database"""
    proxies = db.query(Proxy).all()
    
    if not proxies:
        print("❌ No proxies found in database")
        return
    
    print(f"\n{'='*80}")
    print(f"📊 Total Proxies: {len(proxies)}")
    print(f"{'='*80}\n")
    
    for proxy in proxies:
        status_icon = "✅" if proxy.is_active else "❌"
        validation_icon = {
            "valid": "✅",
            "invalid": "❌",
            "pending": "⏳",
            "banned": "🚫"
        }.get(proxy.validation_status, "❓")
        
        auth = f"{proxy.username}:***" if proxy.username else "No Auth"
        last_validated = proxy.last_validated.strftime("%Y-%m-%d %H:%M") if proxy.last_validated else "Never"
        
        # Usage tracking (if available)
        usage_count = getattr(proxy, 'usage_count', 0) or 0
        last_used = getattr(proxy, 'last_used', None)
        last_used_str = last_used.strftime("%Y-%m-%d %H:%M") if last_used else "Never"
        
        print(f"{status_icon} ID: {proxy.id:3d} | {proxy.country:2s} | {proxy.host:30s}:{proxy.port:<5d}")
        print(f"   Auth: {auth:20s} | Status: {validation_icon} {proxy.validation_status:10s} | Last Check: {last_validated}")
        print(f"   Usage: {usage_count:3d} times | Last Used: {last_used_str}")
        print()

def add_proxy(db: Session, host: str, port: int, username: str = None, password: str = None, country: str = "DZ"):
    """Add a new proxy to database"""
    try:
        proxy = Proxy(
            host=host,
            port=port,
            username=username,
            password=password,
            country=country.upper(),
            is_active=True,
            validation_status="pending",
            created_at=datetime.utcnow()
        )
        
        db.add(proxy)
        db.commit()
        db.refresh(proxy)
        
        print(f"✅ Proxy added successfully!")
        print(f"   ID: {proxy.id}")
        print(f"   Host: {proxy.host}:{proxy.port}")
        print(f"   Country: {proxy.country}")
        print(f"   Auth: {'Yes' if username else 'No'}")
        
    except Exception as e:
        print(f"❌ Error adding proxy: {e}")
        db.rollback()

def remove_proxy(db: Session, proxy_id: int):
    """Remove a proxy from database"""
    try:
        proxy = db.query(Proxy).filter(Proxy.id == proxy_id).first()
        
        if not proxy:
            print(f"❌ Proxy with ID {proxy_id} not found")
            return
        
        print(f"🗑️  Removing proxy: {proxy.host}:{proxy.port}")
        db.delete(proxy)
        db.commit()
        print(f"✅ Proxy removed successfully")
        
    except Exception as e:
        print(f"❌ Error removing proxy: {e}")
        db.rollback()

def toggle_proxy(db: Session, proxy_id: int):
    """Toggle proxy active status"""
    try:
        proxy = db.query(Proxy).filter(Proxy.id == proxy_id).first()
        
        if not proxy:
            print(f"❌ Proxy with ID {proxy_id} not found")
            return
        
        proxy.is_active = not proxy.is_active
        status_text = "enabled" if proxy.is_active else "disabled"
        
        db.commit()
        print(f"✅ Proxy {proxy.host}:{proxy.port} {status_text}")
        
    except Exception as e:
        print(f"❌ Error toggling proxy: {e}")
        db.rollback()

def update_proxy_status(db: Session, proxy_id: int, status: str):
    """Update proxy validation status"""
    try:
        proxy = db.query(Proxy).filter(Proxy.id == proxy_id).first()
        
        if not proxy:
            print(f"❌ Proxy with ID {proxy_id} not found")
            return
        
        valid_statuses = ["valid", "invalid", "pending", "banned"]
        if status not in valid_statuses:
            print(f"❌ Invalid status. Choose from: {', '.join(valid_statuses)}")
            return
        
        proxy.validation_status = status
        proxy.last_validated = datetime.utcnow()
        
        db.commit()
        print(f"✅ Proxy {proxy.host}:{proxy.port} status updated to: {status}")
        
    except Exception as e:
        print(f"❌ Error updating proxy: {e}")
        db.rollback()

def add_bulk_proxies(db: Session):
    """Add multiple proxies interactively"""
    print("\n📝 Bulk Proxy Addition")
    print("Enter proxies in format: host:port:username:password:country")
    print("Example: proxy.example.com:8080:user123:pass456:DZ")
    print("For no auth: proxy.example.com:8080:::ES")
    print("Type 'done' when finished\n")
    
    added_count = 0
    
    while True:
        line = input("Proxy: ").strip()
        
        if line.lower() == 'done':
            break
        
        if not line:
            continue
        
        parts = line.split(':')
        
        if len(parts) < 2:
            print("❌ Invalid format. Need at least host:port")
            continue
        
        host = parts[0]
        try:
            port = int(parts[1])
        except ValueError:
            print("❌ Port must be a number")
            continue
        
        username = parts[2] if len(parts) > 2 and parts[2] else None
        password = parts[3] if len(parts) > 3 and parts[3] else None
        country = parts[4].upper() if len(parts) > 4 and parts[4] else "DZ"
        
        add_proxy(db, host, port, username, password, country)
        added_count += 1
    
    print(f"\n✅ Added {added_count} proxies")

def print_usage():
    """Print usage instructions"""
    print("""
🔧 Proxy Management Tool
========================

Commands:
  list                          - List all proxies
  add <host> <port> [user] [pass] [country]  - Add a new proxy
  remove <id>                   - Remove proxy by ID
  toggle <id>                   - Enable/disable proxy
  status <id> <valid|invalid|pending|banned> - Update proxy status
  bulk                          - Add multiple proxies interactively
  stats                         - Show proxy statistics
  
Examples:
  python manage_proxies.py list
  python manage_proxies.py add proxy.example.com 8080 user123 pass456 DZ
  python manage_proxies.py add 123.45.67.89 3128 "" "" ES
  python manage_proxies.py remove 5
  python manage_proxies.py toggle 3
  python manage_proxies.py status 2 banned
  python manage_proxies.py bulk
  python manage_proxies.py stats
""")

def show_stats(db: Session):
    """Show proxy statistics"""
    total = db.query(Proxy).count()
    active = db.query(Proxy).filter(Proxy.is_active == True).count()
    inactive = total - active
    
    valid = db.query(Proxy).filter(Proxy.validation_status == "valid").count()
    invalid = db.query(Proxy).filter(Proxy.validation_status == "invalid").count()
    pending = db.query(Proxy).filter(Proxy.validation_status == "pending").count()
    banned = db.query(Proxy).filter(Proxy.validation_status == "banned").count()
    
    # Count by country
    countries = db.query(Proxy.country).distinct().all()
    country_counts = {}
    for (country,) in countries:
        count = db.query(Proxy).filter(Proxy.country == country).count()
        country_counts[country] = count
    
    print(f"\n📊 Proxy Statistics")
    print(f"{'='*50}")
    print(f"Total Proxies:     {total}")
    print(f"  Active:          {active} ✅")
    print(f"  Inactive:        {inactive} ❌")
    print()
    print(f"Validation Status:")
    print(f"  Valid:           {valid} ✅")
    print(f"  Invalid:         {invalid} ❌")
    print(f"  Pending:         {pending} ⏳")
    print(f"  Banned:          {banned} 🚫")
    print()
    print(f"By Country:")
    for country, count in sorted(country_counts.items()):
        print(f"  {country}:              {count}")
    print(f"{'='*50}\n")

def main():
    if len(sys.argv) < 2:
        print_usage()
        return
    
    command = sys.argv[1].lower()
    db = SessionLocal()
    
    try:
        if command == "list":
            list_proxies(db)
        
        elif command == "add":
            if len(sys.argv) < 4:
                print("❌ Usage: add <host> <port> [username] [password] [country]")
                return
            
            host = sys.argv[2]
            port = int(sys.argv[3])
            username = sys.argv[4] if len(sys.argv) > 4 and sys.argv[4] else None
            password = sys.argv[5] if len(sys.argv) > 5 and sys.argv[5] else None
            country = sys.argv[6] if len(sys.argv) > 6 else "DZ"
            
            add_proxy(db, host, port, username, password, country)
        
        elif command == "remove":
            if len(sys.argv) < 3:
                print("❌ Usage: remove <proxy_id>")
                return
            
            proxy_id = int(sys.argv[2])
            remove_proxy(db, proxy_id)
        
        elif command == "toggle":
            if len(sys.argv) < 3:
                print("❌ Usage: toggle <proxy_id>")
                return
            
            proxy_id = int(sys.argv[2])
            toggle_proxy(db, proxy_id)
        
        elif command == "status":
            if len(sys.argv) < 4:
                print("❌ Usage: status <proxy_id> <valid|invalid|pending|banned>")
                return
            
            proxy_id = int(sys.argv[2])
            status = sys.argv[3]
            update_proxy_status(db, proxy_id, status)
        
        elif command == "bulk":
            add_bulk_proxies(db)
        
        elif command == "stats":
            show_stats(db)
        
        else:
            print(f"❌ Unknown command: {command}")
            print_usage()
    
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        db.close()

if __name__ == "__main__":
    main()

