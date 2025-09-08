from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from django.contrib import messages
from django.db.models import Q, Count, Avg
from datetime import date, timedelta
from .models import IPO, Company, MarketData, FinancialMetrics, IPONews
from .services import finnhub_service
import json
import random

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize API clients
try:
    # OpenAI client (existing)
    from openai import OpenAI
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if openai_api_key:
        openai_client = OpenAI(api_key=openai_api_key)
    else:
        openai_client = None
except Exception as e:
    openai_client = None
    print(f"OpenAI initialization error: {e}")


try:
    # Gemini client (new)
    import google.generativeai as genai
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if gemini_api_key and gemini_api_key != "YOUR_GEMINI_API_KEY_HERE":
        genai.configure(api_key=gemini_api_key)
        gemini_model = genai.GenerativeModel('gemini-1.5-flash')
    else:
        gemini_model = None
except Exception as e:
    gemini_model = None
    print(f"Gemini initialization error: {e}")

def dashboard(request):
    """Main dashboard view with overview of all IPO data"""
    
    # Get real IPO data from database
    today = date.today()
    
    # Upcoming IPOs (opening in the future)
    upcoming_ipos = IPO.objects.filter(
        open_date__gt=today,
        status='upcoming'
    ).select_related('company').order_by('open_date')[:5]
    
    # Ongoing IPOs (currently open)
    ongoing_ipos = IPO.objects.filter(
        open_date__lte=today,
        close_date__gte=today,
        status='ongoing'
    ).select_related('company').order_by('close_date')[:5]
    
    # Recently completed IPOs
    past_ipos = IPO.objects.filter(
        close_date__lt=today,
        status='completed'
    ).select_related('company').order_by('-close_date')[:5]
    
    # Get statistics
    total_ipos = IPO.objects.count()
    active_ipos = IPO.objects.filter(status__in=['upcoming', 'ongoing']).count()
    completed_ipos = IPO.objects.filter(status='completed').count()
    total_companies = Company.objects.count()
    
    # Calculate average subscription rate for completed IPOs
    avg_subscription = IPO.objects.filter(
        status='completed',
        subscription_rate__isnull=False
    ).aggregate(avg_sub=Avg('subscription_rate'))['avg_sub'] or 0
    
    # Get recent news
    recent_news = IPONews.objects.select_related('ipo__company').order_by('-published_date')[:3]
    
    context = {
        'upcoming_ipos': upcoming_ipos,
        'ongoing_ipos': ongoing_ipos,
        'past_ipos': past_ipos,
        'total_ipos': total_ipos,
        'active_ipos': active_ipos,
        'completed_ipos': completed_ipos,
        'total_companies': total_companies,
        'avg_subscription': round(avg_subscription, 2),
        'recent_news': recent_news,
        'finnhub_configured': finnhub_service.is_configured(),
    }
    return render(request, 'ipo_app/dashboard.html', context)

def get_response(request):
    """Get AI response for chatbot"""
    user_message = request.GET.get('message', '').strip()
    
    if not user_message:
        return JsonResponse({"response": "Please enter a message to get started!"})
    
    # Determine which API to use (default to Gemini if available)
    use_gemini = gemini_model is not None
    
    try:
        if use_gemini:
            # Use Gemini API
            if not gemini_api_key or gemini_api_key == "YOUR_GEMINI_API_KEY_HERE":
                bot_response = "⚠️ I'm not fully configured yet. Please set up the GEMINI_API_KEY in your .env file to enable AI responses. For now, I can provide some basic IPO guidance!"
            else:
                # Generate response using Gemini with IPO-focused context
                prompt = f"""You are Nexa AI, a helpful and knowledgeable IPO analysis assistant. 
                You specialize in Indian IPO markets and provide clear, actionable insights.
                
                Guidelines for responses:
                - Be professional yet friendly
                - Provide specific, actionable advice when possible
                - Use bullet points or numbered lists for clarity
                - Include relevant financial metrics when discussing IPOs
                - Always remind users to do their own research
                
                User query: {user_message}
                
                Provide a helpful response:"""
                
                response = gemini_model.generate_content(prompt)
                bot_response = response.text.strip()
        else:
            # Fallback to OpenAI API
            if not openai_client:
                # Provide helpful response even without API
                if any(keyword in user_message.lower() for keyword in ['ipo', 'invest', 'stock', 'market']):
                    bot_response = """I'd be happy to help with IPO analysis! Here are some general tips:
                    
                    📊 **Key IPO Evaluation Factors:**
                    • Company fundamentals and financial health
                    • Market conditions and sector performance  
                    • Valuation and price band analysis
                    • Management team track record
                    • Competitive positioning
                    
                    💡 **Before Investing:**
                    • Read the prospectus carefully
                    • Check subscription rates and demand
                    • Analyze grey market premiums
                    • Consider your risk tolerance
                    
                    🔍 Use our Market Analysis and Risk Assessment tools for deeper insights!
                    
                    ⚠️ For personalized AI responses, please configure the API keys."""
                else:
                    bot_response = """Hello! I'm Nexa AI, your IPO analysis assistant. 
                    
                    I can help you with:
                    • IPO analysis and recommendations
                    • Market trends and insights
                    • Risk assessment guidance
                    • Investment strategies
                    
                    Try asking me about:
                    - "How to evaluate an IPO?"
                    - "Current market trends"
                    - "Risk factors to consider"
                    
                    ⚠️ For advanced AI responses, please configure the API keys in your .env file."""
            else:
                # Call OpenAI API
                response = openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": """You are Nexa AI, a helpful IPO analysis assistant specializing in Indian markets. 
                        Provide clear, actionable insights about IPOs, market trends, and investment strategies. 
                        Always remind users to do their own research."""},
                        {"role": "user", "content": user_message}
                    ],
                    max_tokens=500,
                    temperature=0.7
                )
                bot_response = response.choices[0].message.content.strip()

    except Exception as e:
        print(f"AI API Error: {str(e)}")  # For debugging
        bot_response = f"""I encountered a technical issue, but I can still help! 
        
        If you're asking about IPOs, here are some quick insights:
        
        📈 **Current Market Status:** Use our Dashboard to see live IPO data
        📊 **Analysis Tools:** Check out our Market Analysis section
        🛡️ **Risk Assessment:** Use our Risk Assessment tool
        💼 **Portfolio:** Track your investments in the Portfolio section
        
        Error details: {str(e)}"""

    return JsonResponse({"response": bot_response})


def sync_ipo_data(request):
    """API endpoint to manually trigger IPO data sync"""
    if request.method == 'POST':
        try:
            # Import management command to trigger sync
            from django.core.management import call_command
            import io
            import sys
            
            # Capture command output
            old_stdout = sys.stdout
            sys.stdout = captured_output = io.StringIO()
            
            try:
                # Call the sync command with force flag to create sample data if API not configured
                call_command('sync_ipo_data', '--force')
                output = captured_output.getvalue()
                
                # Check if sample data was created or real sync happened
                if 'Created' in output and 'sample IPO records' in output:
                    # Sample data was created
                    import re
                    match = re.search(r'Created (\d+) sample IPO records', output)
                    created_count = int(match.group(1)) if match else 0
                    
                    return JsonResponse({
                        'status': 'success',
                        'message': f'Sample IPO data created successfully! Created {created_count} IPO records.',
                        'stats': {
                            'created': created_count,
                            'type': 'sample_data'
                        }
                    })
                else:
                    # Real sync happened or other success
                    return JsonResponse({
                        'status': 'success', 
                        'message': 'IPO data sync completed successfully!',
                        'stats': {
                            'synced': True,
                            'type': 'api_sync'
                        }
                    })
                    
            finally:
                sys.stdout = old_stdout
        
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Error during IPO sync: {str(e)}'
            }, status=500)
    
    return JsonResponse({
        'status': 'error',
        'message': 'Only POST method allowed'
    }, status=405)


def api_status(request):
    """API endpoint to check the status of external integrations"""
    status = {
        'finnhub': {
            'configured': finnhub_service.is_configured(),
            'last_sync': 'Never',  # TODO: Add last sync timestamp
        },
        'gemini': {
            'configured': gemini_model is not None,
        },
        'openai': {
            'configured': openai_client is not None,
        },
        'database': {
            'total_companies': Company.objects.count(),
            'total_ipos': IPO.objects.count(),
            'upcoming_ipos': IPO.objects.filter(status='upcoming').count(),
            'ongoing_ipos': IPO.objects.filter(status='ongoing').count(),
        }
    }
    
    return JsonResponse(status)


def ipo_list(request):
    """Complete list of all IPOs with filtering and search"""
    
    # Get filter parameters
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('search', '')
    exchange_filter = request.GET.get('exchange', '')
    
    # Base queryset
    ipos = IPO.objects.select_related('company').order_by('-open_date')
    
    # Apply filters
    if status_filter:
        ipos = ipos.filter(status=status_filter)
    
    if exchange_filter:
        ipos = ipos.filter(exchange=exchange_filter)
    
    if search_query:
        ipos = ipos.filter(
            Q(company__name__icontains=search_query) |
            Q(company__symbol__icontains=search_query) |
            Q(company__industry__icontains=search_query)
        )
    
    # Get filter options
    status_choices = IPO.STATUS_CHOICES
    exchange_choices = IPO.EXCHANGE_CHOICES
    
    context = {
        'ipos': ipos,
        'status_filter': status_filter,
        'search_query': search_query,
        'exchange_filter': exchange_filter,
        'status_choices': status_choices,
        'exchange_choices': exchange_choices,
    }
    return render(request, 'ipo_app/ipo_list.html', context)


def ipo_detail(request, ipo_id):
    """Detailed view of a specific IPO"""
    
    ipo = get_object_or_404(IPO, id=ipo_id)
    
    # Get related data
    try:
        market_data = ipo.market_data
    except MarketData.DoesNotExist:
        market_data = None
    
    try:
        financials = ipo.company.financials
    except FinancialMetrics.DoesNotExist:
        financials = None
    
    # Get related news
    news = ipo.news.order_by('-published_date')[:5]
    
    context = {
        'ipo': ipo,
        'market_data': market_data,
        'financials': financials,
        'news': news,
    }
    return render(request, 'ipo_app/ipo_detail.html', context)


def ai_chat(request):
    """Dedicated AI Chat page"""
    return render(request, 'ipo_app/ai_chat.html')


def market_analysis(request):
    """Market Analysis page with charts and insights"""
    
    # Get market statistics
    today = date.today()
    
    # IPO performance data
    completed_ipos = IPO.objects.filter(status='completed')
    total_ipos = IPO.objects.count()
    
    # Calculate average listing gains
    avg_listing_gains = completed_ipos.aggregate(
        avg_gains=Avg('listing_gains')
    )['avg_gains'] or 0
    
    # Monthly IPO counts for the last 12 months
    monthly_data = []
    for i in range(12):
        month_date = today.replace(day=1) - timedelta(days=30*i)
        month_end = month_date + timedelta(days=30)
        count = IPO.objects.filter(
            open_date__gte=month_date,
            open_date__lt=month_end
        ).count()
        monthly_data.append({
            'month': month_date.strftime('%b %Y'),
            'count': count if count > 0 else random.randint(1, 8)  # Sample data for demo
        })
    
    monthly_data.reverse()
    
    # Industry distribution with sample data if no real data
    industry_data = list(Company.objects.values('industry').annotate(
        count=Count('id')
    ).order_by('-count')[:10])
    
    # Add sample data if no real data exists
    if not industry_data:
        import random
        sample_industries = [
            'Information Technology', 'Financial Services', 'Healthcare',
            'Manufacturing', 'Energy', 'Consumer Goods', 'Real Estate',
            'Telecommunications', 'Retail', 'Pharmaceuticals'
        ]
        industry_data = [
            {'industry': industry, 'count': random.randint(2, 15)}
            for industry in sample_industries[:8]
        ]
    
    # Subscription vs listing gains data (sample for demo)
    subscription_data = []
    if completed_ipos.exists():
        for ipo in completed_ipos[:20]:  # Limit to 20 for chart readability
            subscription_data.append({
                'subscription_rate': float(ipo.subscription_rate or random.uniform(1.5, 5.0)),
                'listing_gains': float(ipo.listing_gains or random.uniform(-10, 30)),
                'company__name': ipo.company.name
            })
    else:
        # Sample data for demonstration
        sample_companies = [
            'Tech Innovators Ltd', 'Green Energy Solutions', 'FinTech Payments Pro',
            'Digital Healthcare Corp', 'Smart Manufacturing Inc', 'E-commerce Hub',
            'Renewable Power Co', 'AI Robotics Ltd', 'BioTech Research', 'Logistics Pro'
        ]
        for company in sample_companies:
            subscription_data.append({
                'subscription_rate': round(random.uniform(1.2, 6.5), 1),
                'listing_gains': round(random.uniform(-8, 35), 1),
                'company__name': company
            })
    
    context = {
        'total_ipos': total_ipos if total_ipos > 0 else 45,  # Sample data
        'avg_listing_gains': avg_listing_gains if avg_listing_gains else 12.5,  # Sample data
        'monthly_data': json.dumps(monthly_data),
        'industry_data': json.dumps(industry_data),
        'subscription_data': json.dumps(subscription_data),
    }
    return render(request, 'ipo_app/market_analysis.html', context)
    
    # Subscription rate analysis
    subscription_data = IPO.objects.filter(
        subscription_rate__isnull=False
    ).values('subscription_rate', 'company__name', 'listing_gains')
    
    context = {
        'monthly_data': monthly_data,
        'industry_data': industry_data,
        'subscription_data': list(subscription_data),
        'total_ipos': IPO.objects.count(),
        'avg_listing_gains': completed_ipos.aggregate(
            avg_gains=Avg('listing_gains')
        )['avg_gains'] or 0,
    }
    return render(request, 'ipo_app/market_analysis.html', context)


def risk_assessment(request):
    """Risk Assessment tool"""
    
    if request.method == 'POST':
        # Get form data
        investment_amount = float(request.POST.get('investment_amount', 0))
        risk_tolerance = request.POST.get('risk_tolerance', 'medium')
        investment_horizon = request.POST.get('investment_horizon', 'medium')
        
        # Simple risk calculation
        risk_score = calculate_risk_score(
            investment_amount, risk_tolerance, investment_horizon
        )
        
        # Get IPO recommendations based on risk profile
        recommendations = get_ipo_recommendations(risk_score)
        
        context = {
            'risk_score': risk_score,
            'recommendations': recommendations,
            'investment_amount': investment_amount,
            'risk_tolerance': risk_tolerance,
            'investment_horizon': investment_horizon,
        }
        return render(request, 'ipo_app/risk_assessment.html', context)
    
    return render(request, 'ipo_app/risk_assessment.html')


def portfolio(request):
    """Portfolio tracking page"""
    
    # This would typically be user-specific, but for demo purposes
    # we'll show sample portfolio data
    
    sample_portfolio = [
        {
            'ipo': 'TechNova Ltd',
            'quantity': 100,
            'buy_price': 125,
            'current_price': 140,
            'gain_loss': 15,
            'gain_loss_percent': 12.0
        },
        {
            'ipo': 'GreenEnergy Corp',
            'quantity': 50,
            'buy_price': 260,
            'current_price': 245,
            'gain_loss': -15,
            'gain_loss_percent': -5.77
        }
    ]
    
    total_investment = sum([item['quantity'] * item['buy_price'] for item in sample_portfolio])
    current_value = sum([item['quantity'] * item['current_price'] for item in sample_portfolio])
    total_gain_loss = current_value - total_investment
    
    context = {
        'portfolio': sample_portfolio,
        'total_investment': total_investment,
        'current_value': current_value,
        'total_gain_loss': total_gain_loss,
        'total_gain_loss_percent': (total_gain_loss / total_investment * 100) if total_investment > 0 else 0
    }
    return render(request, 'ipo_app/portfolio.html', context)


def news(request):
    """News and updates page"""
    
    # Get all IPO news
    news_list = IPONews.objects.select_related('ipo__company').order_by('-published_date')
    
    # Filter by IPO if specified
    ipo_filter = request.GET.get('ipo')
    if ipo_filter:
        news_list = news_list.filter(ipo_id=ipo_filter)
    
    # Get unique IPOs for filter dropdown
    ipos_with_news = IPO.objects.filter(
        news__isnull=False
    ).distinct().order_by('company__name')
    
    context = {
        'news_list': news_list,
        'ipos_with_news': ipos_with_news,
        'ipo_filter': ipo_filter,
    }
    return render(request, 'ipo_app/news.html', context)


# Utility functions
def calculate_risk_score(investment_amount, risk_tolerance, investment_horizon):
    """Calculate risk score based on user inputs"""
    
    score = 5  # Base score
    
    # Adjust based on investment amount
    if investment_amount > 100000:
        score += 1
    elif investment_amount < 10000:
        score -= 1
    
    # Adjust based on risk tolerance
    risk_map = {'low': -2, 'medium': 0, 'high': 2}
    score += risk_map.get(risk_tolerance, 0)
    
    # Adjust based on investment horizon
    horizon_map = {'short': -1, 'medium': 0, 'long': 1}
    score += horizon_map.get(investment_horizon, 0)
    
    return max(1, min(10, score))  # Keep between 1-10


def get_ipo_recommendations(risk_score):
    """Get IPO recommendations based on risk score"""
    
    if risk_score <= 3:
        # Low risk - recommend stable, established companies
        ipos = IPO.objects.filter(
            status__in=['upcoming', 'ongoing']
        ).select_related('company').order_by('price_band_min')[:3]
    elif risk_score <= 7:
        # Medium risk - balanced recommendations
        ipos = IPO.objects.filter(
            status__in=['upcoming', 'ongoing']
        ).select_related('company').order_by('-issue_size')[:3]
    else:
        # High risk - growth companies
        ipos = IPO.objects.filter(
            status__in=['upcoming', 'ongoing'],
            company__industry__in=['Technology', 'Fintech', 'Biotech']
        ).select_related('company')[:3]
    
    return ipos