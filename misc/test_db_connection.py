"""
Test Database Connection Script
Run this to diagnose database connection issues
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
BASE_DIR = Path(__file__).parent
load_dotenv(dotenv_path=BASE_DIR / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")

print("=" * 60)
print("DATABASE CONNECTION TEST")
print("=" * 60)
print()

# Check if DATABASE_URL is set
if not DATABASE_URL:
    print("❌ ERROR: DATABASE_URL is not set in .env file")
    print()
    print("Please:")
    print("1. Copy .env.example to .env")
    print("2. Add your Supabase DATABASE_URL")
    print()
    sys.exit(1)

# Mask password in URL for display
masked_url = DATABASE_URL
if "@" in DATABASE_URL:
    parts = DATABASE_URL.split("@")
    if ":" in parts[0]:
        user_pass = parts[0].split(":")
        if len(user_pass) > 2:
            masked_url = f"{user_pass[0]}:{user_pass[1]}:****@{parts[1]}"

print(f"📍 Database URL: {masked_url[:80]}...")
print()

# Test DNS resolution
print("🔍 Testing DNS resolution...")
try:
    import socket
    # Extract hostname from DATABASE_URL
    if "@" in DATABASE_URL:
        host_part = DATABASE_URL.split("@")[1].split(":")[0]
        ip = socket.gethostbyname(host_part)
        print(f"✅ DNS Resolution successful: {host_part} → {ip}")
    else:
        print("⚠️  Could not extract hostname from DATABASE_URL")
except socket.gaierror as e:
    print(f"❌ DNS Resolution failed: {e}")
    print()
    print("Possible causes:")
    print("  - No internet connection")
    print("  - DNS server issues")
    print("  - Firewall blocking DNS")
    print()
    print("Try:")
    print("  1. Check your internet connection")
    print("  2. Flush DNS cache: ipconfig /flushdns")
    print("  3. Use Google DNS (8.8.8.8)")
    sys.exit(1)
except Exception as e:
    print(f"⚠️  Error during DNS test: {e}")

print()

# Test database connection
print("🔌 Testing database connection...")
try:
    import psycopg2
    
    conn = psycopg2.connect(DATABASE_URL, connect_timeout=10)
    print("✅ Database connection successful!")
    
    # Test a simple query
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    print(f"✅ PostgreSQL version: {version[0][:50]}...")
    
    cursor.close()
    conn.close()
    
    print()
    print("=" * 60)
    print("✅ ALL TESTS PASSED - Database is accessible!")
    print("=" * 60)
    print()
    print("You can now start your FastAPI server:")
    print("  uvicorn src.main:app --reload")
    
except psycopg2.OperationalError as e:
    print(f"❌ Database connection failed: {e}")
    print()
    print("Possible causes:")
    print("  1. No internet connection")
    print("  2. Supabase project is paused (free tier)")
    print("  3. Incorrect DATABASE_URL")
    print("  4. Firewall blocking port 5432")
    print("  5. VPN interfering with connection")
    print()
    print("Solutions:")
    print("  1. Check internet: ping google.com")
    print("  2. Login to Supabase dashboard and check project status")
    print("  3. Verify DATABASE_URL in .env file")
    print("  4. Check firewall settings")
    print("  5. Disable VPN temporarily")
    print()
    print("Get your DATABASE_URL:")
    print("  https://supabase.com/dashboard → Your Project → Settings → Database")
    sys.exit(1)
    
except ImportError:
    print("❌ psycopg2 not installed")
    print()
    print("Install it with:")
    print("  pip install psycopg2-binary")
    sys.exit(1)
    
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    print()
    print(f"Error type: {type(e).__name__}")
    sys.exit(1)
