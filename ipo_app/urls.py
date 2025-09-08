from django.urls import path
from . import views

urlpatterns = [
    # Main dashboard
    path('', views.dashboard, name='dashboard'),
    
    # IPO related pages
    path('ipos/', views.ipo_list, name='ipo_list'),
    path('ipo/<int:ipo_id>/', views.ipo_detail, name='ipo_detail'),
    
    # Feature pages
    path('ai-chat/', views.ai_chat, name='ai_chat'),
    path('market-analysis/', views.market_analysis, name='market_analysis'),
    path('risk-assessment/', views.risk_assessment, name='risk_assessment'),
    path('portfolio/', views.portfolio, name='portfolio'),
    path('news/', views.news, name='news'),
    
    # API endpoints
    path('get-response/', views.get_response, name='get_response'),
    path('api/sync-ipo-data/', views.sync_ipo_data, name='sync_ipo_data'),
    path('api/status/', views.api_status, name='api_status'),
]
