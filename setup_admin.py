import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pothole.settings')
django.setup()

from django.contrib.auth.models import User

# Admin credentials (you can change these)
ADMIN_USERNAME = 'admin'
ADMIN_EMAIL = 'admin@potholepilot.com'
ADMIN_PASSWORD = 'Admin123@'

# Check if admin already exists
if User.objects.filter(username=ADMIN_USERNAME).exists():
    print(f"⚠️  Admin user '{ADMIN_USERNAME}' already exists!")
else:
    # Create superuser
    User.objects.create_superuser(ADMIN_USERNAME, ADMIN_EMAIL, ADMIN_PASSWORD)
    print(f"""
✅ Superuser Created Successfully!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📧 Email:    {ADMIN_EMAIL}
👤 Username: {ADMIN_USERNAME}
🔐 Password: {ADMIN_PASSWORD}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Login at: http://127.0.0.1:8000/admin/
    """)