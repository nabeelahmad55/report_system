# check_simple.py
import os
import sys
from pathlib import Path

print("🔍 SIMPLE PROJECT CHECK")
print("="*50)

# 1. Check .env
print("\n1. Checking .env file:")
env = Path(".env")
if env.exists():
    try:
        with open(env, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                if 'EMAIL' in line:
                    print(f"   {line.strip()}")
    except:
        print("   Could not read .env file")

# 2. Check if email service loads
print("\n2. Checking email service import:")
try:
    from app.email_service import send_email
    print("   ✅ email_service.py imports successfully")
except Exception as e:
    print(f"   ❌ Import error: {e}")

# 3. Check database
print("\n3. Checking database:")
db = Path("reports.db")
if db.exists():
    size = db.stat().st_size
    print(f"   ✅ Database exists ({size} bytes)")
else:
    print("   ❌ Database not found")

# 4. Test environment variables
print("\n4. Testing environment variables:")
from dotenv import load_dotenv
load_dotenv()

sender = os.getenv("EMAIL_SENDER")
password = os.getenv("EMAIL_PASSWORD")

if sender:
    print(f"   ✅ SENDER: {sender}")
else:
    print("   ❌ EMAIL_SENDER not set")

if password:
    # Check for spaces
    if ' ' in password:
        print(f"   ❌ PASSWORD HAS SPACES: '{password}'")
        print(f"   ⚠️ Remove spaces: '{password.replace(' ', '')}'")
    else:
        print(f"   ✅ PASSWORD: {password[:4]}... (16 chars)" if len(password) == 16 else f"   ⚠️ PASSWORD: {len(password)} chars")
else:
    print("   ❌ EMAIL_PASSWORD not set")

print("\n" + "="*50)
print("📋 QUICK FIXES TO TRY:")
print("1. Delete .env and create fresh:")
print('   echo EMAIL_SENDER=nab.ahmad55@gmail.com > .env')
print('   echo EMAIL_PASSWORD=wuslfrjowbljerol >> .env')
print("\n2. Test email directly:")
print('   python -c "')
print('   import os')
print('   os.environ[\"EMAIL_SENDER\"] = \"nab.ahmad55@gmail.com\"')
print('   os.environ[\"EMAIL_PASSWORD\"] = \"wuslfrjowbljerol\"')
print('   from app.email_service import send_email')
print('   result = send_email(\"hafiz.nabeelahmad55@gmail.com\", \"Test\", \"Body\", \"test.pdf\")')
print('   print(f\"Email result: {result}\")')
print('   "')