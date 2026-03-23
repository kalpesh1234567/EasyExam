@echo off
echo ============================================
echo   EasyExam - ASAE Setup (Windows)
echo ============================================

echo.
echo [1/4] Installing Django...
pip install Django

echo.
echo [2/4] Running migrations...
python manage.py makemigrations classroom
python manage.py migrate

echo.
echo [3/4] Creating admin user...
python -c "import django; import os; os.environ['DJANGO_SETTINGS_MODULE']='asae.settings'; django.setup(); from django.contrib.auth.models import User; User.objects.create_superuser('admin','admin@asae.com','admin123') if not User.objects.filter(username='admin').exists() else None"

echo.
echo [4/4] Starting server...
echo.
echo ============================================
echo   Running at: http://127.0.0.1:8000
echo   Admin:      http://127.0.0.1:8000/admin
echo   admin / admin123
echo ============================================
python manage.py runserver
pause
