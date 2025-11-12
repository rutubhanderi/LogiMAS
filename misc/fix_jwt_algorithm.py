"""
Script to fix JWT_ALGORITHM typo in .env file
Changes HS26 to HS256
"""
from pathlib import Path

env_file = Path(__file__).parent / ".env"

if not env_file.exists():
    print("❌ .env file not found!")
    exit(1)

# Read the file
content = env_file.read_text()

# Check for the typo
if "JWT_ALGORITHM=HS26" in content:
    print("🔍 Found typo: JWT_ALGORITHM=HS26")
    
    # Fix it
    fixed_content = content.replace("JWT_ALGORITHM=HS26", "JWT_ALGORITHM=HS256")
    
    # Write back
    env_file.write_text(fixed_content)
    
    print("✅ Fixed! Changed to JWT_ALGORITHM=HS256")
    print("\n⚠️  Please restart the server:")
    print("   uvicorn src.main:app --reload")
elif "JWT_ALGORITHM=HS256" in content:
    print("✅ JWT_ALGORITHM is already correct (HS256)")
else:
    print("⚠️  JWT_ALGORITHM not found in .env file")
    print("   Add this line: JWT_ALGORITHM=HS256")
