#!/usr/bin/env python3
"""
Import proxies from proxy.txt file
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.database import Proxy
import os

# Create database connection (using same DB as main app)
engine = create_engine('sqlite:///./tesla_config.db')
Session = sessionmaker(bind=engine)
db = Session()

# Read proxy file
proxy_file = '../proxy.txt'

if not os.path.exists(proxy_file):
    print(f"❌ Error: {proxy_file} not found!")
    exit(1)

print("=" * 80)
print("IMPORTING PROXIES FROM proxy.txt")
print("=" * 80)

with open(proxy_file, 'r') as f:
    lines = f.readlines()

print(f"\n📄 Found {len(lines)} proxies in file")
print("\nFormat detected: host:port:username:password")
print()

added = 0
skipped = 0
errors = 0

for line_num, line in enumerate(lines, 1):
    line = line.strip()
    if not line:
        continue
    
    try:
        # Parse: host:port:username:password
        parts = line.split(':')
        if len(parts) != 4:
            print(f"❌ Line {line_num}: Invalid format (expected host:port:username:password)")
            errors += 1
            continue
        
        host, port, username, password = parts
        port = int(port)
        
        # Extract country from username (region-ES means Spain)
        country = 'ES' if 'region-ES' in username else 'DZ'
        
        # Check if proxy already exists (by host, port, username)
        existing = db.query(Proxy).filter(
            Proxy.host == host,
            Proxy.port == port,
            Proxy.username == username
        ).first()
        
        if existing:
            print(f"⏭️  Line {line_num}: Skipped (already exists) - session: {username.split('session-')[1].split('-')[0] if 'session-' in username else 'N/A'}")
            skipped += 1
            continue
        
        # Create new proxy
        proxy = Proxy(
            host=host,
            port=port,
            username=username,
            password=password,
            country=country,
            is_active=True,
            validation_status="pending"
        )
        
        db.add(proxy)
        
        # Extract session ID for display
        session_id = username.split('session-')[1].split('-')[0] if 'session-' in username else 'N/A'
        print(f"✅ Line {line_num}: Added - {host}:{port} (session: {session_id}, region: {country})")
        added += 1
        
    except Exception as e:
        print(f"❌ Line {line_num}: Error - {e}")
        errors += 1

# Commit all changes
try:
    db.commit()
    print("\n" + "=" * 80)
    print(f"✅ DATABASE UPDATED SUCCESSFULLY!")
    print("=" * 80)
    print(f"\n📊 SUMMARY:")
    print(f"   ✅ Added:   {added}")
    print(f"   ⏭️  Skipped: {skipped}")
    print(f"   ❌ Errors:  {errors}")
    print(f"   📝 Total:   {len(lines)}")
    
    # Show unique session IDs
    all_proxies = db.query(Proxy).filter(Proxy.is_active == True).all()
    unique_sessions = set()
    for p in all_proxies:
        if p.username and 'session-' in p.username:
            session = p.username.split('session-')[1].split('-')[0]
            unique_sessions.add(session)
    
    print(f"\n🎲 PROXY ROTATION:")
    print(f"   Total active proxies: {len(all_proxies)}")
    print(f"   Unique session IDs:   {len(unique_sessions)}")
    print(f"   🌍 Each session ID = Different IP address!")
    
    # Group by country
    from collections import Counter
    countries = Counter(p.country for p in all_proxies)
    print(f"\n📍 PROXIES BY REGION:")
    for country, count in countries.items():
        print(f"   {country or 'Unknown'}: {count} proxies")
    
    print(f"\n💡 NOTE: These are SESSION-BASED rotating proxies")
    print(f"   Same hostname but different session IDs = Different IPs")
    print(f"   Your system will randomly select from {len(unique_sessions)} different IPs! ✅")
    print()
    print("=" * 80)
    
except Exception as e:
    print(f"\n❌ Error committing to database: {e}")
    db.rollback()
finally:
    db.close()

