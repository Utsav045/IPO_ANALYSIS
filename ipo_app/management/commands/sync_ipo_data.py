"""
Management command to sync IPO data from Finnhub API
"""
import logging
from django.core.management.base import BaseCommand
from django.utils import timezone
from ipo_app.services import finnhub_service

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Sync IPO data from Finnhub API to local database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--from-date',
            type=str,
            help='Start date for IPO data in YYYY-MM-DD format',
        )
        parser.add_argument(
            '--to-date',
            type=str,
            help='End date for IPO data in YYYY-MM-DD format',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force sync even if API key is not configured',
        )

    def handle(self, *args, **options):
        """Execute the IPO data sync command"""
        
        self.stdout.write(
            self.style.SUCCESS('Starting IPO data sync from Finnhub...')
        )
        
        # Check if Finnhub is configured
        if not finnhub_service.is_configured():
            if not options['force']:
                self.stdout.write(
                    self.style.ERROR(
                        'Finnhub API key not configured. '
                        'Please set FINNHUB_API_KEY in your .env file.\n'
                        'Use --force flag to continue anyway (will use sample data).'
                    )
                )
                return
            else:
                self.stdout.write(
                    self.style.WARNING(
                        'Finnhub API not configured. Creating sample IPO data...'
                    )
                )
                self._create_sample_data()
                return
        
        # Perform the sync
        start_time = timezone.now()
        
        try:
            # Get date parameters
            from_date = options.get('from_date')
            to_date = options.get('to_date')
            
            # Perform sync
            stats = finnhub_service.sync_ipo_data()
            
            # Calculate duration
            duration = timezone.now() - start_time
            
            # Display results
            self.stdout.write(
                self.style.SUCCESS(
                    f'\\n✅ IPO sync completed successfully!\\n'
                    f'Duration: {duration.total_seconds():.2f} seconds\\n'
                    f'Statistics:'
                )
            )
            
            for key, value in stats.items():
                color = self.style.SUCCESS if key != 'errors' else self.style.ERROR
                self.stdout.write(f'  • {key.title()}: {color(str(value))}')
            
            if stats['errors'] > 0:
                self.stdout.write(
                    self.style.WARNING(
                        f'\\n⚠️  {stats["errors"]} errors occurred during sync. '
                        'Check logs for details.'
                    )
                )
        
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error during IPO sync: {str(e)}')
            )
            logger.error(f'IPO sync command failed: {str(e)}')
    
    def _create_sample_data(self):
        """Create sample IPO data when API is not configured"""
        from ipo_app.models import Company, IPO, MarketData, FinancialMetrics
        from datetime import date, timedelta
        import random
        
        try:
            # Sample Indian IPO data
            sample_ipos = [
                {
                    'company_name': 'Tech Innovators Ltd',
                    'symbol': 'TECHINNO',
                    'industry': 'Information Technology',
                    'price_min': 120,
                    'price_max': 130,
                    'open_date': date.today() + timedelta(days=5),
                    'close_date': date.today() + timedelta(days=8),
                    'status': 'upcoming'
                },
                {
                    'company_name': 'Green Energy Solutions',
                    'symbol': 'GREENSOL',
                    'industry': 'Renewable Energy', 
                    'price_min': 250,
                    'price_max': 270,
                    'open_date': date.today() + timedelta(days=10),
                    'close_date': date.today() + timedelta(days=13),
                    'status': 'upcoming'
                },
                {
                    'company_name': 'FinTech Payments Pro',
                    'symbol': 'FINPAY',
                    'industry': 'Financial Services',
                    'price_min': 500,
                    'price_max': 520,
                    'open_date': date.today() - timedelta(days=2),
                    'close_date': date.today() + timedelta(days=1),
                    'status': 'ongoing'
                },
                {
                    'company_name': 'Digital Healthcare Corp',
                    'symbol': 'DIGHEALTH',
                    'industry': 'Healthcare Technology',
                    'price_min': 300,
                    'price_max': 320,
                    'open_date': date.today() + timedelta(days=15),
                    'close_date': date.today() + timedelta(days=18),
                    'status': 'upcoming'
                }
            ]
            
            created_count = 0
            
            for ipo_data in sample_ipos:
                # Create or get company
                company, company_created = Company.objects.get_or_create(
                    symbol=ipo_data['symbol'],
                    defaults={
                        'name': ipo_data['company_name'],
                        'industry': ipo_data['industry'],
                        'description': f"Sample company in {ipo_data['industry']} sector providing innovative solutions.",
                        'headquarters': 'Mumbai, India',
                        'founded_year': 2015,
                        'employees': 1000,
                        'website': f"https://{ipo_data['symbol'].lower()}.com",
                        'ceo': 'Sample CEO Name'
                    }
                )
                
                # Create IPO if it doesn't exist
                ipo, ipo_created = IPO.objects.get_or_create(
                    company=company,
                    defaults={
                        'status': ipo_data['status'],
                        'exchange': 'BOTH',
                        'price_band_min': ipo_data['price_min'],
                        'price_band_max': ipo_data['price_max'],
                        'open_date': ipo_data['open_date'],
                        'close_date': ipo_data['close_date'],
                        'total_shares': 10000000,
                        'lot_size': 100,
                        'issue_size': ipo_data['price_max'] * 10000000 / 10000000,  # In crores
                        'lead_managers': 'ICICI Securities, Kotak Mahindra Capital',
                        'registrar': 'Link Intime India Private Limited'
                    }
                )
                
                if ipo_created:
                    created_count += 1
                    
                    # Create market data for the IPO
                    MarketData.objects.get_or_create(
                        ipo=ipo,
                        defaults={
                            'retail_subscription': round(random.uniform(1.2, 4.5), 1),
                            'hni_subscription': round(random.uniform(0.8, 6.2), 1),
                            'institutional_subscription': round(random.uniform(2.1, 8.5), 1),
                            'grey_market_premium': round(random.uniform(-50, 150), 0),
                            'analyst_rating': random.choice(['strong_buy', 'buy', 'hold']),
                            'risk_score': random.randint(3, 8),
                            'application_count': random.randint(50000, 500000),
                            'amount_collected': round(random.uniform(100, 2000), 1)
                        }
                    )
                    
                    # Create financial metrics
                    FinancialMetrics.objects.get_or_create(
                        company=company,
                        defaults={
                            'revenue_fy1': round(random.uniform(100, 1000), 1),
                            'revenue_fy2': round(random.uniform(80, 800), 1),
                            'revenue_fy3': round(random.uniform(60, 600), 1),
                            'profit_fy1': round(random.uniform(10, 100), 1),
                            'profit_fy2': round(random.uniform(8, 80), 1),
                            'profit_fy3': round(random.uniform(5, 60), 1),
                            'pe_ratio': round(random.uniform(15, 35), 1),
                            'roe': round(random.uniform(8, 25), 1),
                            'debt_to_equity': round(random.uniform(0.1, 2.5), 2),
                            'book_value_per_share': round(random.uniform(50, 300), 1)
                        }
                    )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Created {created_count} sample IPO records'
                )
            )
        
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error creating sample data: {str(e)}')
            )