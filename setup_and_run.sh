#!/bin/bash
# ============================================================
#  ASAE - Subjective Answer Evaluation System - Setup Script
# ============================================================
echo "============================================"
echo "  EasyExam – ASAE Setup"
echo "============================================"

# 1. Install Django
echo ""
echo "[1/4] Installing Django..."
pip install Django --break-system-packages -q || pip install Django -q
echo "✓ Django installed"

# 2. Migrations
echo ""
echo "[2/4] Running migrations..."
python manage.py makemigrations classroom
python manage.py migrate
echo "✓ Database ready"

# 3. Create superuser (optional)
echo ""
echo "[3/4] Creating admin superuser..."
echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@asae.com', 'admin123') if not User.objects.filter(username='admin').exists() else None" | python manage.py shell
echo "✓ Admin user: admin / admin123"

# 4. Run server
echo ""
echo "[4/4] Starting development server..."
echo ""
echo "============================================"
echo "  ✅ Server running at: http://127.0.0.1:8000"
echo "  📋 Admin panel:       http://127.0.0.1:8000/admin"
echo "  Username: admin | Password: admin123"
echo "============================================"
echo ""
python manage.py runserver
