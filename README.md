# Pothole Pilot - Smart Civic Reporting System

A full-stack Django web application for reporting and tracking potholes in your community. Users can report potholes with images and GPS coordinates, vote on reports, and municipalities can track and update the status of repairs.

## Features

### User Features
- **User Authentication**: Register, login, and manage your account
- **Report Potholes**: Submit pothole reports with images and auto-captured GPS location
- **Community Feed**: View all community-reported potholes
- **Voting System**: Upvote pothole reports to help verify them
- **Truth Score**: Earn reputation points for accurate reports
- **Notifications**: Get updates when your reports are being fixed
- **Map View**: See all potholes on an interactive Google Map
- **User Profile**: Track your reports and truth score

### Admin/Municipality Features
- **Admin Dashboard**: View all pothole reports in a dashboard
- **Status Management**: Update pothole status (Pending, In Progress, Fixed, Invalid)
- **Worker Assignment**: Assign repair workers to potholes
- **Completion Tracking**: Upload images when repairs are complete
- **Notifications**: Automatically notify reporters of status updates
- **Statistics**: View counts and metrics of all potholes

## Tech Stack

- **Backend**: Django 4.2.5
- **Frontend**: HTML5, CSS3, Bootstrap 5, JavaScript
- **Database**: SQLite
- **Maps**: Google Maps JavaScript API
- **Location**: Browser Geolocation API
- **Image Processing**: Pillow

## Project Structure

```
pothole/
├── pothole_project/          # Django project settings
│   ├── __init__.py
│   ├── settings.py          # Django settings
│   ├── urls.py              # Main URL configuration
│   └── wsgi.py
├── potholes/                 # Django app
│   ├── models.py            # Database models
│   ├── views.py             # View logic
│   ├── forms.py             # Django forms
│   ├── urls.py              # App URL routing
│   ├── admin.py             # Django admin configuration
│   ├── apps.py              # App configuration
│   ├── signals.py           # Django signals
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css    # Main stylesheet
│   │   └── js/
│   │       └── map.js       # Map functionality
│   └── templates/potholes/  # HTML templates
│       ├── base.html
│       ├── home.html
│       ├── register.html
│       ├── login.html
│       ├── report_pothole.html
│       ├── community_feed.html
│       ├── user_dashboard.html
│       ├── user_profile.html
│       ├── notifications.html
│       ├── pothole_detail.html
│       ├── map.html
│       ├── admin_dashboard.html
│       └── update_pothole.html
├── media/                    # User-uploaded files
├── manage.py                # Django management script
├── db.sqlite3               # SQLite database
└── requirements.txt         # Python dependencies
```

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Git

### Step 1: Clone the Repository
```bash
cd pothole
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Apply Database Migrations
```bash
python manage.py migrate
```

### Step 5: Create Superuser (Admin Account)
```bash
python manage.py createsuperuser
```
Follow the prompts to create your admin account.

### Step 6: Collect Static Files (Optional for Development)
```bash
python manage.py collectstatic --noinput
```

## Configuration

### Google Maps API Key
To use the map feature, you need a Google Maps API key:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable Google Maps JavaScript API
4. Create an API key for web application
5. Replace `YOUR_GOOGLE_MAPS_API_KEY_HERE` in:
   - `pothole_project/settings.py` (GOOGLE_MAPS_API_KEY variable)
   - `potholes/templates/potholes/map.html` (script src)

## Running the Application

### Start the Development Server
```bash
python manage.py runserver
```

The application will be available at `http://localhost:8000`

### Access Admin Panel
Navigate to `http://localhost:8000/admin/` and login with your superuser credentials.

## Usage

### For Users

1. **Register**: Click "Register" and create a new account
2. **Login**: Login with your credentials
3. **Report a Pothole**:
   - Click "Report Pothole"
   - Take or upload an image
   - Click "Get Current Location" to capture your GPS coordinates
   - Enter a description and select severity level
   - Submit the report

4. **View Community Feed**: See all reported potholes
5. **Vote on Reports**: Upvote potholes to verify them
6. **Check Notifications**: Monitor updates on your reports
7. **View Your Profile**: Track your truth score and total reports

### For Admins

1. **Login as Admin**: Use your superuser account
2. **Access Admin Dashboard**: Navigate to `/admin/dashboard/`
3. **Review Reports**: Scroll through all submitted pothole reports
4. **Update Status**: 
   - Click update icon next to a pothole
   - Change status (Pending → In Progress → Fixed/Invalid)
   - Assign a worker
   - Upload completion image if fixed
5. **Track Statistics**: View counts on the dashboard

## Models

### UserProfile
```python
- user: OneToOne with User
- truth_score: Integer (default: 0)
- total_reports: Integer (default: 0)
- created_at: DateTime
```

### Pothole
```python
- user: ForeignKey to User
- image: ImageField
- latitude: FloatField
- longitude: FloatField
- description: TextField
- severity: CharField (Low, Medium, High)
- status: CharField (Pending, In Progress, Fixed, Invalid)
- vote_count: Integer
- assigned_worker: CharField
- completion_image: ImageField
- created_at/updated_at: DateTime
```

### Vote
```python
- user: ForeignKey to User
- pothole: ForeignKey to Pothole
- created_at: DateTime
- Unique constraint: (user, pothole)
```

### Notification
```python
- user: ForeignKey to User
- pothole: ForeignKey to Pothole
- notification_type: CharField
- message: TextField
- is_read: BooleanField
- created_at: DateTime
```

## Truth Score System

- **+1**: When someone upvotes your report
- **-1**: When someone removes their upvote
- **+5**: When your report is marked as "In Progress"
- **+10**: When your report is marked as "Fixed"
- **-10**: When your report is marked as "Invalid"

## API Endpoints

- `GET /api/potholes/` - List all potholes as JSON (for map)
- `POST /pothole/<id>/upvote/` - Upvote a pothole

## Templates Overview

| Template | Purpose |
|----------|---------|
| base.html | Base template with navigation |
| home.html | Landing page |
| register.html | User registration form |
| login.html | User login form |
| report_pothole.html | Pothole reporting form |
| community_feed.html | List of all potholes |
| user_dashboard.html | User's personal dashboard |
| user_profile.html | User profile and statistics |
| notifications.html | User's notifications |
| pothole_detail.html | Single pothole detail page |
| map.html | Interactive map view |
| admin_dashboard.html | Admin report list |
| update_pothole.html | Admin update status form |

## Troubleshooting

### Database Issues
```bash
# Reset database (WARNING: loses all data)
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

### Static Files Not Loading
```bash
python manage.py collectstatic --noinput
```

### Module Not Found Errors
```bash
pip install -r requirements.txt
```

### Geolocation Not Working
- Ensure the website is served over HTTPS (except localhost)
- Check browser permissions for location access
- Some browsers require HTTPS for security

## Browser Compatibility

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Security Notes

1. **Change SECRET_KEY** in `settings.py` before production
2. **Use HTTPS** in production (with secure cookies)
3. **Update DEBUG = False** in production
4. **Use a production database** (PostgreSQL recommended)
5. **Implement rate limiting** for API endpoints
6. **Validate user uploads** more strictly

## Features Not Implemented (Future Enhancements)

- Email notifications
- Advanced analytics and reporting
- Image compression and optimization
- Comments and discussions
- Pothole categories/types
- Multi-language support
- Mobile app

## License

This project is open source and available under the MIT License.

## Support

For issues or questions, please create an issue in the repository or contact the development team.

---

**Happy Pothole Hunting!** 🛣️

Pothole Pilot v1.0 - 2026
