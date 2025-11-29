# Database Migration Guide

## Quick Start - First Time Setup

If you get error: `no such table: posts`, you need to run database migrations!

### Step 1: Run Migrations

```bash
# Make sure you're in the project directory
cd /path/to/login-instangram

# Run migrations to create the posts table
flask db migrate -m "Add Post model"
flask db upgrade
```

### Step 2: Verify

```bash
# Check if migration was successful
flask db current

# You should see the migration ID
```

### Step 3: Restart Server

```bash
# Stop the current server (Ctrl+C)
# Start again
python main.py
```

## Common Issues

### Error: "flask: command not found"

Make sure you're in the virtual environment:

```bash
# Activate virtual environment
source venv/bin/activate  # On Mac/Linux
# or
venv\Scripts\activate  # On Windows

# Then try again
flask db upgrade
```

### Error: "No changes detected"

This is fine if the migration already ran. Just run:

```bash
flask db upgrade
```

### Want to start fresh?

```bash
# Delete the database
rm instance/site.db

# Delete migration versions (keep the migrations folder)
rm migrations/versions/*.py

# Create new migrations
flask db migrate -m "Initial migration"
flask db upgrade
```

## Migration Commands Reference

```bash
# Create a new migration
flask db migrate -m "Description of changes"

# Apply migrations
flask db upgrade

# Rollback last migration
flask db downgrade

# Show current migration
flask db current

# Show migration history
flask db history
```

## Database Schema

After running migrations, you should have these tables:

1. **users**
   - id (primary key)
   - username (unique)
   - fullname
   - password (hashed)

2. **posts**
   - id (primary key)
   - caption
   - image_url
   - created_at
   - user_id (foreign key to users)

## Need Help?

If migrations fail, make sure:
- [ ] You're in the project directory
- [ ] Virtual environment is activated
- [ ] Flask is installed (`pip install -r requirements.txt`)
- [ ] Database folder exists (`mkdir -p instance`)
