# IPO Compass

A Django web application for IPO analysis with AI-powered insights.

## Overview
IPO Compass is a professional IPO analysis platform that provides real-time data, AI insights, and expert recommendations for informed investment decisions. The application features an AI assistant powered by Google Gemini and OpenAI APIs, comprehensive IPO tracking, market analysis tools, and a user-friendly interface.

## Features
- **AI-Powered Assistant**: Get instant answers to your IPO questions with our AI assistant
- **IPO Tracking**: Monitor upcoming, ongoing, and past IPOs with detailed analytics
- **Market Analysis**: Access real-time data and expert insights
- **Risk Assessment**: Comprehensive risk analysis for each IPO opportunity
- **Portfolio Tools**: Track and optimize your IPO investments
- **Responsive Design**: Works on all devices with a modern, clean interface

## Technologies Used
- **Backend**: Django 5.0.2 with Python 3.13
- **Frontend**: HTML5, CSS3, Bootstrap 5, JavaScript
- **Database**: SQLite (development), PostgreSQL/MySQL (production)
- **AI APIs**: Google Gemini and OpenAI
- **Deployment**: Heroku, PythonAnywhere, AWS, or GCP

## Quick Setup
1. Clone the repository
2. Create a virtual environment
3. Install dependencies: `pip install -r requirements.txt`
4. Set environment variables in `.env`
5. Run migrations: `python manage.py migrate`
6. Start the server: `python manage.py runserver`

## Deployment
See [setup.md](setup.md) for detailed deployment instructions.

## API Keys Required
- Google Gemini API Key (primary)
- OpenAI API Key (fallback)

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Support
For support, please open an issue on the repository.