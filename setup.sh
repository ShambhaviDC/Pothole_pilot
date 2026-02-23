#!/bin/bash
# Setup script for Pothole Pilot Django Application

echo "=========================================="
echo "Pothole Pilot - Setup Script"
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "Error: Python is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✓ Python found: $(python --version)"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
python -m venv venv
echo "✓ Virtual environment created"
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate 2>/dev/null || venv\Scripts\activate 2>/dev/null
echo "✓ Virtual environment activated"
echo ""

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
echo "✓ Dependencies installed"
echo ""

# Run migrations
echo "Running database migrations..."
python manage.py migrate
echo "✓ Database migrations completed"
echo ""

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput
echo "✓ Static files collected"
echo ""

# Create superuser prompt
echo "=========================================="
echo "Creating Admin Account"
echo "=========================================="
python manage.py createsuperuser
echo ""

echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "To start the development server, run:"
echo "  python manage.py runserver"
echo ""
echo "Then visit:"
echo "  http://localhost:8000/"
echo ""
echo "Admin panel is at:"
echo "  http://localhost:8000/admin/"
echo ""
