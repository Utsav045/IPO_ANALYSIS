"""
Services for external API integrations and business logic
"""
import os
import finnhub
import requests
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from django.conf import settings
from .models import Company, IPO

logger = logging.getLogger(__name__)


class FinnhubService:
    """Service for integrating with Finnhub API to fetch real-time IPO data"""
    
    def __init__(self):
        self.api_key = os.getenv('FINNHUB_API_KEY')
        if not self.api_key or self.api_key == 'your_finnhub_api_key_here':
            logger.warning("Finnhub API key not configured")
            self.client = None
        else:
            self.client = finnhub.Client(api_key=self.api_key)
    
    def is_configured(self) -> bool:
        """Check if Finnhub API is properly configured"""
        return self.client is not None
    
    def get_ipo_calendar(self, from_date: str = None, to_date: str = None) -> List[Dict]:
        """
        Fetch IPO calendar data from Finnhub
        
        Args:
            from_date: Start date in YYYY-MM-DD format
            to_date: End date in YYYY-MM-DD format
            
        Returns:
            List of IPO data dictionaries
        """
        if not self.is_configured():
            logger.error("Finnhub API not configured")
            return []
        
        try:
            # If no dates provided, get data for next 30 days
            if not from_date:
                from_date = datetime.now().strftime('%Y-%m-%d')
            if not to_date:
                to_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
            
            # Fetch IPO calendar data
            ipo_data = self.client.ipo_calendar(from_date, to_date)
            
            logger.info(f"Fetched {len(ipo_data.get('ipoCalendar', []))} IPO records from Finnhub")
            return ipo_data.get('ipoCalendar', [])
            
        except Exception as e:
            logger.error(f"Error fetching IPO data from Finnhub: {str(e)}")
            return []
    
    def get_company_profile(self, symbol: str) -> Optional[Dict]:
        """
        Fetch company profile data from Finnhub
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Company profile dictionary or None
        """
        if not self.is_configured():
            return None
        
        try:
            profile = self.client.company_profile2(symbol=symbol)
            return profile if profile else None
        except Exception as e:
            logger.error(f"Error fetching company profile for {symbol}: {str(e)}")
            return None
    
    def process_ipo_data(self, ipo_data: List[Dict]) -> List[Dict]:
        """
        Process and clean IPO data from Finnhub
        
        Args:
            ipo_data: Raw IPO data from Finnhub
            
        Returns:
            Processed IPO data
        """
        processed_data = []
        
        for ipo in ipo_data:
            try:
                # Extract and clean data
                processed_ipo = {
                    'symbol': ipo.get('symbol', ''),
                    'name': ipo.get('name', ''),
                    'date': ipo.get('date', ''),
                    'exchange': ipo.get('exchange', ''),
                    'price_min': ipo.get('priceMin', 0),
                    'price_max': ipo.get('priceMax', 0),
                    'shares': ipo.get('shares', 0),
                    'status': ipo.get('status', 'upcoming')
                }
                
                # Skip if essential data is missing
                if not processed_ipo['symbol'] or not processed_ipo['name']:
                    continue
                
                processed_data.append(processed_ipo)
                
            except Exception as e:
                logger.error(f"Error processing IPO data: {str(e)}")
                continue
        
        return processed_data
    
    def create_or_update_ipo(self, ipo_data: Dict) -> Optional[IPO]:
        """
        Create or update IPO record in database
        
        Args:
            ipo_data: Processed IPO data
            
        Returns:
            IPO instance or None
        """
        try:
            # Get or create company
            company, created = Company.objects.get_or_create(
                symbol=ipo_data['symbol'],
                defaults={
                    'name': ipo_data['name'],
                    'industry': 'Technology',  # Default, will be updated later
                    'description': f"Company going public: {ipo_data['name']}",
                    'headquarters': 'India'  # Assuming Indian IPOs
                }
            )
            
            if created:
                logger.info(f"Created new company: {company.name}")
            
            # Parse date
            try:
                ipo_date = datetime.strptime(ipo_data['date'], '%Y-%m-%d').date()
            except (ValueError, TypeError):
                ipo_date = datetime.now().date()
            
            # Determine status based on date
            today = datetime.now().date()
            if ipo_date > today:
                status = 'upcoming'
            elif ipo_date == today:
                status = 'ongoing'
            else:
                status = 'completed'
            
            # Get or create IPO
            ipo, created = IPO.objects.get_or_create(
                company=company,
                defaults={
                    'status': status,
                    'exchange': 'NSE' if 'NSE' in ipo_data.get('exchange', '') else 'BSE',
                    'price_band_min': max(ipo_data.get('price_min', 0), 1),
                    'price_band_max': max(ipo_data.get('price_max', 0), ipo_data.get('price_min', 1)),
                    'open_date': ipo_date,
                    'close_date': ipo_date + timedelta(days=3),  # Typical IPO duration
                    'total_shares': max(ipo_data.get('shares', 1000000), 1000000),
                    'lot_size': 100,  # Default lot size
                    'issue_size': max(ipo_data.get('price_max', 100) * ipo_data.get('shares', 1000000) / 10000000, 100),  # In crores
                    'lead_managers': 'TBD',
                }
            )
            
            if created:
                logger.info(f"Created new IPO: {ipo.company.name}")
            else:
                # Update existing IPO with new data
                ipo.status = status
                ipo.price_band_min = max(ipo_data.get('price_min', 0), 1)
                ipo.price_band_max = max(ipo_data.get('price_max', 0), ipo_data.get('price_min', 1))
                ipo.save()
                logger.info(f"Updated IPO: {ipo.company.name}")
            
            return ipo
            
        except Exception as e:
            logger.error(f"Error creating/updating IPO: {str(e)}")
            return None
    
    def sync_ipo_data(self) -> Dict[str, int]:
        """
        Sync IPO data from Finnhub to database
        
        Returns:
            Dictionary with sync statistics
        """
        stats = {
            'fetched': 0,
            'processed': 0,
            'created': 0,
            'updated': 0,
            'errors': 0
        }
        
        try:
            # Fetch IPO calendar data
            raw_data = self.get_ipo_calendar()
            stats['fetched'] = len(raw_data)
            
            if not raw_data:
                logger.warning("No IPO data fetched from Finnhub")
                return stats
            
            # Process the data
            processed_data = self.process_ipo_data(raw_data)
            stats['processed'] = len(processed_data)
            
            # Create/update IPO records
            for ipo_data in processed_data:
                ipo = self.create_or_update_ipo(ipo_data)
                if ipo:
                    if ipo.created_at == ipo.updated_at:
                        stats['created'] += 1
                    else:
                        stats['updated'] += 1
                else:
                    stats['errors'] += 1
            
            logger.info(f"IPO sync completed: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Error during IPO sync: {str(e)}")
            stats['errors'] += 1
            return stats


# Global instance
finnhub_service = FinnhubService()