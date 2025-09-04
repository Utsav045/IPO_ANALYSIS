# IPO Compass - Django Web Application Setup Guide

## Project Overview
IPO Compass is a Django web application for IPO analysis with AI-powered insights. The application provides real-time data, market analysis, and expert recommendations for informed investment decisions.

## Project Structure
```
ipo_compass/
├── .env                      # Environment variables
├── .gitignore                # Git ignore file
├── Procfile                  # Heroku deployment configuration
├── README.md                 # Project documentation
├── db.sqlite3                # SQLite database
├── manage.py                 # Django management script
├── requirements.txt          # Python dependencies
├── runtime.txt               # Python runtime version
├── setup.md                  # This setup guide
│
├── ipo_app/                  # Main Django application
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   ├── views.py
│   ├── migrations/
│   │   └── __init__.py
│   ├── static/
│   │   ├── script.js
│   │   └── styles.css
│   └── templates/
│       └── ipo_app/
│           ├── home.html
│           └── index.html
│
├── ipo_compass/              # Django project settings
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   ├── styles.css
│   └── templates/
│       └── home.html
│
├── static/                   # Static files
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
│
└── templates/                # Project templates
    └── ipo_app/
        └── index.html
```

## Prerequisites
- Python 3.13
- Django 5.0.2
- Node.js (for frontend asset compilation)
- Git (for version control)

## Local Development Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd ipo_compass
```

### 2. Create Virtual Environment
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Variables
Create a `.env` file in the project root with the following variables:
```env
OPENAI_API_KEY=your_openai_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
SECRET_KEY=your_django_secret_key_here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 5. Database Setup
```bash
python manage.py migrate
```

### 6. Run Development Server
```bash
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/`

## Production Deployment

### Heroku Deployment

#### 1. Install Heroku CLI
Download and install from: https://devcenter.heroku.com/articles/heroku-cli

#### 2. Login to Heroku
```bash
heroku login
```

#### 3. Create Heroku App
```bash
heroku create your-app-name
```

#### 4. Set Environment Variables
```bash
heroku config:set SECRET_KEY=your-secret-key-here
heroku config:set DEBUG=False
heroku config:set ALLOWED_HOSTS=your-app-name.herokuapp.com
heroku config:set OPENAI_API_KEY=your-openai-api-key
heroku config:set GEMINI_API_KEY=your-gemini-api-key
```

#### 5. Deploy Application
```bash
git push heroku master
```

#### 6. Run Database Migrations
```bash
heroku run python manage.py migrate
```

#### 7. Open Application
```bash
heroku open
```

### Alternative Deployment Options

#### PythonAnywhere
1. Create an account at pythonanywhere.com
2. Upload your code via Git or file upload
3. Configure the web app to point to your Django project
4. Set environment variables in the dashboard

#### AWS Elastic Beanstalk
1. Install AWS CLI and EB CLI
2. Initialize your application: `eb init`
3. Create environment: `eb create`
4. Deploy: `eb deploy`

#### Google Cloud Platform
1. Install Google Cloud SDK
2. Use Google App Engine:
   ```bash
   gcloud app deploy
   ```

## File Descriptions

### Core Django Files
- `manage.py`: Django command-line utility
- `requirements.txt`: Python package dependencies
- `Procfile`: Heroku deployment configuration
- `runtime.txt`: Python runtime version specification
- `.env`: Environment variables (not committed to version control)
- `.gitignore`: Files and directories to exclude from version control

### Settings Files
- `ipo_compass/settings.py`: Django project settings
- `ipo_compass/urls.py`: Main URL configuration
- `ipo_compass/wsgi.py`: WSGI application entry point

### Application Files
- `ipo_app/views.py`: View functions and logic
- `ipo_app/urls.py`: Application URL patterns
- `ipo_app/models.py`: Database models
- `ipo_app/templates/`: HTML templates

### Static Files
- `static/css/style.css`: Custom CSS styles
- `static/js/main.js`: JavaScript functionality

## API Integration

### OpenAI API
The application uses OpenAI for chatbot functionality. Set the `OPENAI_API_KEY` environment variable with your API key.

### Google Gemini API
The application uses Google Gemini as the primary AI provider with OpenAI as fallback. Set the `GEMINI_API_KEY` environment variable with your API key.

To get your Gemini API key:
1. Go to https://ai.google.dev/
2. Create an account or sign in
3. Navigate to API keys section
4. Create a new API key
5. Add it to your environment variables

## Database
The application uses SQLite for development. For production, consider using PostgreSQL or MySQL.

## Troubleshooting

### Common Issues
1. **Missing Dependencies**: Run `pip install -r requirements.txt`
2. **Environment Variables**: Ensure all required variables are set in `.env`
3. **Database Migrations**: Run `python manage.py migrate`
4. **Static Files**: Run `python manage.py collectstatic` for production

### Debugging
- Check server logs for error messages
- Verify environment variables are correctly set
- Ensure all dependencies are installed
- Confirm database migrations have been run

## Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a pull request

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Support
For support, please open an issue on the repository or contact the development team.