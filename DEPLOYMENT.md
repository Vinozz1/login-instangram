# Instagram Clone - VPS Deployment Guide

## Prerequisites
- Ubuntu/Debian VPS
- Python 3.12+
- Nginx (web server)
- Domain atau IP address

## Step 1: Persiapan VPS

```bash
# Update sistem
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install python3 python3-pip python3-venv nginx supervisor -y
```

## Step 2: Clone & Setup Project

```bash
# Clone project
cd /var/www/
git clone https://github.com/Vinozz1/login-instangram.git
cd login-instangram

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Step 3: Setup Environment Variables

```bash
# Create .env file
nano .env
```

Isi dengan:
```env
FLASK_DEBUG=False
SECRET_KEY=your-secret-key-here-change-this
DATABASE_URL=sqlite:///instance/site.db
```

Generate SECRET_KEY:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

## Step 4: Setup Database

```bash
# Activate venv jika belum
source venv/bin/activate

# Run migrations
flask db upgrade
```

## Step 5: Test Gunicorn

```bash
# Test run dengan gunicorn
gunicorn --bind 0.0.0.0:8000 wsgi:app

# Jika berhasil, tekan Ctrl+C untuk stop
```

## Step 6: Setup Supervisor (Process Manager)

```bash
# Create supervisor config
sudo nano /etc/supervisor/conf.d/instagram-clone.conf
```

Isi dengan:
```ini
[program:instagram-clone]
directory=/var/www/login-instangram
command=/var/www/login-instangram/venv/bin/gunicorn --workers 3 --bind unix:instagram-clone.sock -m 007 wsgi:app
user=www-data
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
stderr_logfile=/var/log/instagram-clone/error.log
stdout_logfile=/var/log/instagram-clone/access.log
```

```bash
# Create log directory
sudo mkdir -p /var/log/instagram-clone
sudo chown -R www-data:www-data /var/log/instagram-clone

# Set permissions
sudo chown -R www-data:www-data /var/www/login-instangram

# Start supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start instagram-clone
sudo supervisorctl status instagram-clone
```

## Step 7: Setup Nginx

```bash
# Create nginx config
sudo nano /etc/nginx/sites-available/instagram-clone
```

Isi dengan:
```nginx
server {
    listen 80;
    server_name your-domain.com;  # Ganti dengan domain/IP kamu

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/login-instangram/instagram-clone.sock;
    }

    location /static {
        alias /var/www/login-instangram/app/static;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/instagram-clone /etc/nginx/sites-enabled/

# Test nginx config
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx
```

## Step 8: Firewall (Optional)

```bash
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
sudo ufw enable
```

## Step 9: SSL dengan Let's Encrypt (Optional tapi Recommended)

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

## Maintenance Commands

### Update aplikasi
```bash
cd /var/www/login-instangram
git pull
source venv/bin/activate
pip install -r requirements.txt
flask db upgrade
sudo supervisorctl restart instagram-clone
```

### View logs
```bash
# Error logs
sudo tail -f /var/log/instagram-clone/error.log

# Access logs
sudo tail -f /var/log/instagram-clone/access.log

# Nginx logs
sudo tail -f /var/log/nginx/error.log
```

### Restart services
```bash
sudo supervisorctl restart instagram-clone
sudo systemctl restart nginx
```

## Troubleshooting

### Jika aplikasi tidak jalan:
1. Check supervisor status: `sudo supervisorctl status`
2. Check logs: `sudo tail -f /var/log/instagram-clone/error.log`
3. Check nginx: `sudo nginx -t`
4. Check permissions: `/var/www/login-instangram` harus owned by www-data

### Database issues:
```bash
cd /var/www/login-instangram
source venv/bin/activate
flask db upgrade
```

### Port sudah dipakai:
```bash
sudo lsof -i :8000
sudo kill -9 [PID]
```

## Production Checklist
- [ ] SECRET_KEY sudah diganti
- [ ] FLASK_DEBUG=False
- [ ] Database migrations sudah dijalankan
- [ ] Supervisor running
- [ ] Nginx configured
- [ ] Firewall setup
- [ ] SSL/HTTPS (optional)
- [ ] Domain pointing ke VPS IP

## Quick Commands Reference

```bash
# Start/Stop/Restart
sudo supervisorctl start instagram-clone
sudo supervisorctl stop instagram-clone
sudo supervisorctl restart instagram-clone

# Status
sudo supervisorctl status

# Logs
sudo tail -f /var/log/instagram-clone/error.log
```

---
**Note:** Ganti `your-domain.com` dengan domain atau IP VPS kamu!
