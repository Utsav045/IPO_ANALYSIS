from django.contrib import admin
from .models import Company, IPO, FinancialMetrics, MarketData, IPONews


class FinancialMetricsInline(admin.StackedInline):
    model = FinancialMetrics
    extra = 0
    fieldsets = (
        ('Revenue (in Crores)', {
            'fields': ('revenue_fy3', 'revenue_fy2', 'revenue_fy1')
        }),
        ('Profit (in Crores)', {
            'fields': ('profit_fy3', 'profit_fy2', 'profit_fy1')
        }),
        ('Key Ratios', {
            'fields': ('pe_ratio', 'roe', 'debt_to_equity', 'book_value_per_share')
        })
    )


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'symbol', 'industry', 'founded_year', 'headquarters', 'created_at']
    list_filter = ['industry', 'founded_year']
    search_fields = ['name', 'symbol', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    inlines = [FinancialMetricsInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'symbol', 'description', 'industry')
        }),
        ('Company Details', {
            'fields': ('founded_year', 'headquarters', 'website', 'ceo', 'employees')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


class MarketDataInline(admin.StackedInline):
    model = MarketData
    extra = 0
    fieldsets = (
        ('Subscription Data', {
            'fields': ('retail_subscription', 'hni_subscription', 'institutional_subscription')
        }),
        ('Market Analysis', {
            'fields': ('grey_market_premium', 'analyst_rating', 'risk_score')
        }),
        ('Application Metrics', {
            'fields': ('application_count', 'amount_collected')
        })
    )


class IPONewsInline(admin.TabularInline):
    model = IPONews
    extra = 1
    fields = ['title', 'source', 'published_date', 'url']
    readonly_fields = ['created_at']


@admin.register(IPO)
class IPOAdmin(admin.ModelAdmin):
    list_display = ['company', 'status', 'exchange', 'price_range_display', 'open_date', 'close_date', 'subscription_rate']
    list_filter = ['status', 'exchange', 'open_date', 'listing_date']
    search_fields = ['company__name', 'company__symbol']
    readonly_fields = ['created_at', 'updated_at', 'price_range_display', 'is_active', 'days_to_close']
    date_hierarchy = 'open_date'
    
    inlines = [MarketDataInline, IPONewsInline]
    
    fieldsets = (
        ('Company & Status', {
            'fields': ('company', 'status', 'exchange')
        }),
        ('Pricing Information', {
            'fields': ('price_band_min', 'price_band_max', 'final_price', 'price_range_display')
        }),
        ('Important Dates', {
            'fields': ('open_date', 'close_date', 'listing_date', 'is_active', 'days_to_close')
        }),
        ('Share Details', {
            'fields': ('total_shares', 'lot_size', 'issue_size', 'market_cap')
        }),
        ('Performance Metrics', {
            'fields': ('subscription_rate', 'listing_gains')
        }),
        ('Additional Information', {
            'fields': ('lead_managers', 'registrar'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('company')


@admin.register(FinancialMetrics)
class FinancialMetricsAdmin(admin.ModelAdmin):
    list_display = ['company', 'revenue_fy1', 'profit_fy1', 'pe_ratio', 'roe']
    list_filter = ['pe_ratio', 'roe']
    search_fields = ['company__name', 'company__symbol']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Company', {
            'fields': ('company',)
        }),
        ('Revenue Data (Crores)', {
            'fields': ('revenue_fy3', 'revenue_fy2', 'revenue_fy1')
        }),
        ('Profit Data (Crores)', {
            'fields': ('profit_fy3', 'profit_fy2', 'profit_fy1')
        }),
        ('Key Financial Ratios', {
            'fields': ('pe_ratio', 'roe', 'debt_to_equity', 'book_value_per_share')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(MarketData)
class MarketDataAdmin(admin.ModelAdmin):
    list_display = ['ipo', 'analyst_rating', 'risk_score', 'grey_market_premium', 'retail_subscription']
    list_filter = ['analyst_rating', 'risk_score']
    search_fields = ['ipo__company__name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('IPO Reference', {
            'fields': ('ipo',)
        }),
        ('Subscription Analysis', {
            'fields': ('retail_subscription', 'hni_subscription', 'institutional_subscription')
        }),
        ('Market Assessment', {
            'fields': ('grey_market_premium', 'analyst_rating', 'risk_score')
        }),
        ('Application Statistics', {
            'fields': ('application_count', 'amount_collected')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(IPONews)
class IPONewsAdmin(admin.ModelAdmin):
    list_display = ['ipo', 'title', 'source', 'published_date', 'created_at']
    list_filter = ['source', 'published_date', 'ipo__company__name']
    search_fields = ['title', 'content', 'source']
    readonly_fields = ['created_at']
    date_hierarchy = 'published_date'
    
    fieldsets = (
        ('News Information', {
            'fields': ('ipo', 'title', 'content')
        }),
        ('Source Details', {
            'fields': ('source', 'published_date', 'url')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )


# Customize admin site headers
admin.site.site_header = "IPO Compass Administration"
admin.site.site_title = "IPO Compass Admin"
admin.site.index_title = "Welcome to IPO Compass Administration"
