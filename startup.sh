cd /home/site/wwwroot
gunicorn --bind=0.0.0.0 --timeout 600 src.app:app
