from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import date


class Company(models.Model):
    """Model representing a company going public"""
    name = models.CharField(max_length=200, help_text="Company name")
    symbol = models.CharField(max_length=10, unique=True, help_text="Stock symbol")
    description = models.TextField(help_text="Company description")
    industry = models.CharField(max_length=100, help_text="Industry sector")
    founded_year = models.IntegerField(null=True, blank=True, help_text="Year company was founded")
    headquarters = models.CharField(max_length=200, help_text="Headquarters location")
    website = models.URLField(blank=True, help_text="Company website")
    ceo = models.CharField(max_length=100, blank=True, help_text="CEO name")
    employees = models.IntegerField(null=True, blank=True, help_text="Number of employees")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Companies"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.symbol})"


class IPO(models.Model):
    """Model representing an IPO offering"""
    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    EXCHANGE_CHOICES = [
        ('NSE', 'National Stock Exchange'),
        ('BSE', 'Bombay Stock Exchange'),
        ('BOTH', 'Both NSE & BSE'),
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='ipos')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming')
    exchange = models.CharField(max_length=10, choices=EXCHANGE_CHOICES, default='BOTH')
    
    # Price information
    price_band_min = models.DecimalField(max_digits=10, decimal_places=2, help_text="Minimum price per share")
    price_band_max = models.DecimalField(max_digits=10, decimal_places=2, help_text="Maximum price per share")
    final_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Final listing price")
    
    # Dates
    open_date = models.DateField(help_text="IPO opening date")
    close_date = models.DateField(help_text="IPO closing date")
    listing_date = models.DateField(null=True, blank=True, help_text="Stock listing date")
    
    # Share information
    total_shares = models.BigIntegerField(help_text="Total number of shares offered")
    lot_size = models.IntegerField(default=1, help_text="Minimum number of shares to apply")
    
    # Financial details
    issue_size = models.DecimalField(max_digits=15, decimal_places=2, help_text="Total issue size in crores")
    market_cap = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="Market cap at upper price band")
    
    # Performance metrics
    subscription_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Subscription rate (times)")
    listing_gains = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Listing gains percentage")
    
    # Additional info
    lead_managers = models.TextField(help_text="Lead managers/underwriters")
    registrar = models.CharField(max_length=200, blank=True, help_text="Registrar name")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-open_date']
        verbose_name = "IPO"
        verbose_name_plural = "IPOs"

    def __str__(self):
        return f"{self.company.name} IPO - {self.status.title()}"

    @property
    def price_range_display(self):
        """Display price range in formatted string"""
        return f"₹{self.price_band_min} - ₹{self.price_band_max}"

    @property
    def is_active(self):
        """Check if IPO is currently active"""
        today = date.today()
        return self.open_date <= today <= self.close_date and self.status == 'ongoing'

    @property
    def days_to_close(self):
        """Calculate days remaining to close"""
        if self.status == 'ongoing':
            today = date.today()
            if today <= self.close_date:
                return (self.close_date - today).days
        return None


class FinancialMetrics(models.Model):
    """Model for company financial data"""
    company = models.OneToOneField(Company, on_delete=models.CASCADE, related_name='financials')
    
    # Revenue data (in crores)
    revenue_fy1 = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text="Revenue FY-1")
    revenue_fy2 = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text="Revenue FY-2")
    revenue_fy3 = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text="Revenue FY-3")
    
    # Profit data (in crores)
    profit_fy1 = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text="Net profit FY-1")
    profit_fy2 = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text="Net profit FY-2")
    profit_fy3 = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text="Net profit FY-3")
    
    # Key ratios
    pe_ratio = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, help_text="Price to Earnings ratio")
    roe = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Return on Equity (%)")
    debt_to_equity = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Debt to Equity ratio")
    
    # Book value
    book_value_per_share = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, help_text="Book value per share")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Financial Metrics"
        verbose_name_plural = "Financial Metrics"

    def __str__(self):
        return f"{self.company.name} - Financial Metrics"


class MarketData(models.Model):
    """Model for real-time market data and analysis"""
    ipo = models.OneToOneField(IPO, on_delete=models.CASCADE, related_name='market_data')
    
    # Subscription data
    retail_subscription = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Retail subscription (times)")
    hni_subscription = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="HNI subscription (times)")
    institutional_subscription = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Institutional subscription (times)")
    
    # Market sentiment
    grey_market_premium = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, help_text="Grey market premium")
    analyst_rating = models.CharField(max_length=20, choices=[
        ('strong_buy', 'Strong Buy'),
        ('buy', 'Buy'),
        ('hold', 'Hold'),
        ('avoid', 'Avoid'),
    ], null=True, blank=True)
    
    # Risk assessment
    risk_score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        null=True, blank=True,
        help_text="Risk score (1-10, where 10 is highest risk)"
    )
    
    # Additional metrics
    application_count = models.BigIntegerField(null=True, blank=True, help_text="Total applications received")
    amount_collected = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="Total amount collected (crores)")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Market Data"
        verbose_name_plural = "Market Data"

    def __str__(self):
        return f"{self.ipo.company.name} - Market Data"


class IPONews(models.Model):
    """Model for IPO-related news and updates"""
    ipo = models.ForeignKey(IPO, on_delete=models.CASCADE, related_name='news')
    title = models.CharField(max_length=300, help_text="News headline")
    content = models.TextField(help_text="News content")
    source = models.CharField(max_length=100, help_text="News source")
    published_date = models.DateTimeField(help_text="Publication date")
    url = models.URLField(blank=True, help_text="Source URL")
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-published_date']
        verbose_name = "IPO News"
        verbose_name_plural = "IPO News"

    def __str__(self):
        return f"{self.ipo.company.name} - {self.title[:50]}..."
