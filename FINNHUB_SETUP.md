# Finnhub IPO Integration Setup Guide

## Getting Your Finnhub API Key

1. **Visit Finnhub.io**
   - Go to [https://finnhub.io/](https://finnhub.io/)
   - Click "Sign Up" or "Get API Key"

2. **Create an Account**
   - Sign up with your email address
   - Verify your email if required
   - Complete the registration process

3. **Get Your API Key**
   - After logging in, go to the Dashboard
   - Find your API key in the "API Key" section
   - Copy the API key (it looks like: `c123456789abcdef123456789abcdef`)

4. **Add to Your Environment**
   - Open your `.env` file in the project root
   - Replace `your_finnhub_api_key_here` with your actual API key:
     ```
     FINNHUB_API_KEY=c123456789abcdef123456789abcdef
     ```

## Features Implemented

### 🔄 Real-time IPO Data Integration
- **Automatic Data Sync**: Fetches latest IPO data from Finnhub API
- **Smart Categorization**: Automatically categorizes IPOs as upcoming, ongoing, or completed
- **Indian Market Focus**: Optimized for Indian IPO market data

### 📊 Data Management
- **Database Integration**: Stores IPO data in your local database
- **Duplicate Prevention**: Avoids creating duplicate entries
- **Data Enrichment**: Enhances basic IPO data with additional fields

### ⚡ Management Commands
```bash
# Sync IPO data manually
python manage.py sync_ipo_data

# Force sync even without API key (creates sample data)
python manage.py sync_ipo_data --force

# Sync with custom date range
python manage.py sync_ipo_data --from-date 2025-01-01 --to-date 2025-12-31
```

### 🌐 API Endpoints
- **`/api/sync-ipo-data/`**: Manual sync trigger (POST)
- **`/api/status/`**: Check integration status (GET)

### 🕒 Automatic Updates
- **Scheduler Module**: Built-in task scheduling for automatic updates
- **Cron Job Support**: Easy setup with system cron jobs
- **Windows Task Scheduler**: Compatible with Windows scheduling

## Usage Examples

### Manual Sync
```python
from ipo_app.services import finnhub_service

# Trigger manual sync
stats = finnhub_service.sync_ipo_data()
print(f"Synced {stats['created']} new IPOs")
```

### Check API Status
```bash
curl http://localhost:8000/api/status/
```

### Setup Automatic Updates (Linux/Mac)
```bash
# Edit crontab
crontab -e

# Add this line for updates every 6 hours
0 */6 * * * cd /path/to/project && python manage.py sync_ipo_data
```

## Data Structure

The integration creates and manages:

- **Companies**: Basic company information
- **IPOs**: Detailed IPO information including dates, pricing, and status
- **Financial Metrics**: Company financial data (when available)
- **Market Data**: Subscription rates, analyst ratings, risk scores
- **IPO News**: Related news and updates

## Free Tier Limits

Finnhub free tier includes:
- **60 API calls/minute**
- **Basic IPO calendar data**
- **Company profiles**
- **Real-time stock prices**

For higher usage, consider upgrading to a paid plan.

## Troubleshooting

### Common Issues

1. **"Finnhub API key not configured"**
   - Check your `.env` file
   - Ensure the key is correct and not the placeholder text

2. **"No IPO data fetched"**
   - Check your internet connection
   - Verify API key is valid
   - Check Finnhub service status

3. **Database errors**
   - Run migrations: `python manage.py migrate`
   - Check database permissions

### Support

For issues with:
- **Finnhub API**: Contact Finnhub support
- **This Integration**: Check the Django logs for detailed error messages

## Next Steps

1. Get your Finnhub API key and add it to `.env`
2. Run `python manage.py sync_ipo_data` to test the integration
3. Set up automatic updates using cron jobs or task scheduler
4. Customize the data fields and display as needed

The integration is now ready to provide real-time Indian IPO data to your IPO Compass application!