from datetime import datetime
from pytz import timezone
from django.utils.timezone import now, timedelta
from django.db.models import Count
from django.db.models.functions import TruncHour, TruncDate, TruncWeek, TruncMonth, TruncYear
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.core.paginator import Paginator
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK
)
from django.contrib import messages 
from .models import *
from .serializer import *
from django.db.models import Q

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def AdminHourlySiteVisits(request):
    now_time = datetime.now(timezone('Asia/Kolkata'))  # Get the correct local time
    start_time = now_time - timedelta(hours=11)  # Last 12 hours including current

    # Fetch visit data grouped by hour
    data = (
        Sitevisit.objects.filter(created_at__gte=start_time)
        .annotate(visit_hour=TruncHour('created_at'))
        .values('visit_hour')
        .annotate(total_visits=Count('id'))
        .order_by('visit_hour')
    )

    # Convert DB results into a dictionary {HH: count}
    data_dict = {entry['visit_hour'].strftime('%I %p'): entry['total_visits'] for entry in data}

    # Generate last 12 hours in HH AM/PM format
    last_12_hours = [
        (start_time + timedelta(hours=i)).strftime('%I %p') for i in range(12)
    ]

    result = [
        {"hour": hour, "total_visits": data_dict.get(hour, 0)}
        for hour in last_12_hours
    ]

    return JsonResponse(result, safe=False)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def AdminDailySiteVisits(request):
    today = datetime.now(timezone('Asia/Kolkata')).date()
    last_10_days = [today - timedelta(days=i) for i in range(9, -1, -1)]  # Last 10 days

    # Fetch actual visit data from DB
    data = (
        Sitevisit.objects.filter(created_at__date__gte=last_10_days[0])  # Start from oldest
        .annotate(visit_date=TruncDate('created_at'))
        .values('visit_date')
        .annotate(total_visits=Count('id'))
        .order_by('visit_date')
    )

    # Convert DB results into a dictionary {YYYY-MM-DD: count}
    data_dict = {str(entry['visit_date']): entry['total_visits'] for entry in data}

    # Ensure every day in last 10 days is included (fill missing days with 0)
    result = [
        {"visit_date": str(day), "total_visits": data_dict.get(str(day), 0)}
        for day in last_10_days
    ]

    return JsonResponse(result, safe=False)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def AdminWeeklySiteVisits(request):
    today = datetime.now(timezone('Asia/Kolkata')).date()
    first_day_of_current_week = today - timedelta(days=today.weekday())  # Get Monday of the current week
    start_date = first_day_of_current_week - timedelta(weeks=9)  # Go back 9 more weeks (total 10 weeks including this one)

    # Fetch data grouped by week (starting from Monday)
    data = (
        Sitevisit.objects.filter(created_at__date__gte=start_date)
        .annotate(visit_week=TruncWeek('created_at'))
        .values('visit_week')
        .annotate(total_visits=Count('id'))
        .order_by('visit_week')
    )

    # Convert to dictionary {YYYY-MM-DD (Monday): count}
    data_dict = {entry['visit_week'].strftime('%Y-%m-%d'): entry['total_visits'] for entry in data}

    # Generate last 10 weeks (starting Mondays)
    last_10_weeks = [
        (start_date + timedelta(weeks=i)).strftime('%Y-%m-%d')
        for i in range(10)
    ]

    # Format output as "Week 1", "Week 2", ..., "Week 10"
    result = [
        {"week": f"Week {i+1}", "total_visits": data_dict.get(week, 0)}
        for i, week in enumerate(last_10_weeks)
    ]

    return JsonResponse(result, safe=False)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def AdminMonthlySiteVisits(request):
    today = datetime.now(timezone('Asia/Kolkata')).date()
    first_day_of_current_month = today.replace(day=1)
    start_date = first_day_of_current_month - timedelta(days=30 * 9)  # 10 months back from current month

    data = (
        Sitevisit.objects.filter(created_at__date__gte=start_date)
        .annotate(visit_month=TruncMonth('created_at'))
        .values('visit_month')
        .annotate(total_visits=Count('id'))
        .order_by('visit_month')
    )

    # Convert to dictionary {YYYY-MM: count}
    data_dict = {entry['visit_month'].strftime('%Y-%m'): entry['total_visits'] for entry in data}

    # Generate list of last 10 months including current month
    last_10_months = [
        (first_day_of_current_month - timedelta(days=30 * i)).strftime('%Y-%m')
        for i in range(9, -1, -1)
    ]

    result = [
        {"visit_month": month, "total_visits": data_dict.get(month, 0)}
        for month in last_10_months
    ]

    return JsonResponse(result, safe=False)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def AdminYearlySiteVisits(request):
    current_year = datetime.now(timezone('Asia/Kolkata')).year
    start_year = current_year - 9  # 10 years ago

    # Fetch visit data grouped by year
    data = (
        Sitevisit.objects.filter(created_at__year__gte=start_year)
        .annotate(visit_year=TruncYear('created_at'))
        .values('visit_year')
        .annotate(total_visits=Count('id'))
        .order_by('visit_year')
    )

    # Convert DB results into a dictionary {YYYY: count}
    data_dict = {str(entry['visit_year'].year): entry['total_visits'] for entry in data}

    # Generate last 10 years (YYYY) with missing years as 0
    last_10_years = [str(year) for year in range(start_year, current_year + 1)]

    result = [
        {"visit_year": year, "total_visits": data_dict.get(year, 0)}
        for year in last_10_years
    ]

    return JsonResponse(result, safe=False)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def AdminVisitsOverview(request):
    return render(request, 'work/visits/overview.html')

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def AdminAllVisitors(request):
    today = now().date()
    todays_visitors = Sitevisitor.objects.filter(created_at__date=today).order_by('-created_at')
    paginator1 = Paginator(todays_visitors, 15)  # Show 15 leads per page
    page_number1 = request.GET.get('page')  # Get page number from URL
    page_obj1 = paginator1.get_page(page_number1)  # Get the correct page

    yesterday = now().date() - timedelta(days=1)
    yesterdays_visitors = Sitevisitor.objects.filter(created_at__date=yesterday).order_by('-created_at')
    paginator2 = Paginator(yesterdays_visitors, 15)  # Show 15 leads per page
    page_number2 = request.GET.get('page')  # Get page number from URL
    page_obj2 = paginator2.get_page(page_number2)  # Get the correct page

    start_of_week = today - timedelta(days=today.weekday())  # Get Monday of the current week
    curweek_visitors = Sitevisitor.objects.filter(created_at__date__gte=start_of_week).order_by('-created_at')
    paginator3 = Paginator(curweek_visitors, 15)  # Show 15 leads per page
    page_number3 = request.GET.get('page')  # Get page number from URL
    page_obj3 = paginator3.get_page(page_number3)  # Get the correct page

    start_of_current_week = today - timedelta(days=today.weekday())  # Get Monday of the current week
    start_of_previous_week = start_of_current_week - timedelta(weeks=1)  # Previous Monday
    end_of_previous_week = start_of_current_week - timedelta(days=1)  # Last Sunday
    prevweek_visitors = Sitevisitor.objects.filter(created_at__date__gte=start_of_previous_week, created_at__date__lte=end_of_previous_week).order_by('-created_at')
    paginator4 = Paginator(prevweek_visitors, 15)  # Show 15 leads per page
    page_number4 = request.GET.get('page')  # Get page number from URL
    page_obj4 = paginator4.get_page(page_number4)  # Get the correct page

    start_of_month = today.replace(day=1)  # First day of current month
    curmonth_visitors = Sitevisitor.objects.filter(created_at__date__gte=start_of_month).order_by('-created_at')
    paginator5 = Paginator(curmonth_visitors, 15)  # Show 15 leads per page
    page_number5 = request.GET.get('page')  # Get page number from URL
    page_obj5 = paginator5.get_page(page_number5)  # Get the correct page

    start_of_current_month = today.replace(day=1)  # First day of current month
    end_of_previous_month = start_of_current_month - timedelta(days=1)  # Last day of previous month
    start_of_previous_month = end_of_previous_month.replace(day=1)  # First day of previous month
    prevmonth_visitors = Sitevisitor.objects.filter(created_at__date__gte=start_of_previous_month, created_at__date__lte=end_of_previous_month).order_by('-created_at')
    paginator6 = Paginator(prevmonth_visitors, 15)  # Show 15 leads per page
    page_number6 = request.GET.get('page')  # Get page number from URL
    page_obj6 = paginator6.get_page(page_number6)  # Get the correct page

    context = {
        'todays' : page_obj1,
        'yesterdays' : page_obj2,
        'current_weeks' : page_obj3,
        'previous_weeks' : page_obj4,
        'current_months' : page_obj5,
        'previous_months' : page_obj6,
    }
    return render(request, 'work/visits/visitor-all.html', context)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def AdminViewVisitorProfile(request, code):
    data = Sitevisitor.objects.filter(visitor_id=code).first()
    visits = Sitevisit.objects.filter(visitor_id=data.id).all()

    flags = {
        'Afghanistan': 'flag-icon flag-icon-af',
        'Aland Islands': 'flag-icon flag-icon-ax',
        'Albania': 'flag-icon flag-icon-al',
        'Algeria': 'flag-icon flag-icon-dz',
        'American Samoa': 'flag-icon flag-icon-as',
        'Andorra': 'flag-icon flag-icon-ad',
        'Angola': 'flag-icon flag-icon-ao',
        'Anguilla': 'flag-icon flag-icon-ai',
        'Antarctica': 'flag-icon flag-icon-aq',
        'Antigua and Barbuda': 'flag-icon flag-icon-ag',
        'Argentina': 'flag-icon flag-icon-ar',
        'Armenia': 'flag-icon flag-icon-am',
        'Aruba': 'flag-icon flag-icon-aw',
        'Australia': 'flag-icon flag-icon-au',
        'Austria': 'flag-icon flag-icon-at',
        'Azerbaijan': 'flag-icon flag-icon-az',
        'Bahamas': 'flag-icon flag-icon-bs',
        'Bahrain': 'flag-icon flag-icon-bh',
        'Bangladesh': 'flag-icon flag-icon-bd',
        'Barbados': 'flag-icon flag-icon-bb',
        'Belarus': 'flag-icon flag-icon-by',
        'Belgium': 'flag-icon flag-icon-be',
        'Belize': 'flag-icon flag-icon-bz',
        'Benin': 'flag-icon flag-icon-bj',
        'Bermuda': 'flag-icon flag-icon-bm',
        'Bhutan': 'flag-icon flag-icon-bt',
        'Bolivia': 'flag-icon flag-icon-bo',
        'Bonaire, Sint Eustatius and Saba': 'flag-icon flag-icon-bq',
        'Bosnia and Herzegovina': 'flag-icon flag-icon-ba',
        'Botswana': 'flag-icon flag-icon-bw',
        'Bouvet Island': 'flag-icon flag-icon-bv',
        'Brazil': 'flag-icon flag-icon-bz',
        'British Indian Ocean Territory': 'flag-icon flag-icon-io',
        'Brunei Darussalam': 'flag-icon flag-icon-bn',
        'Bulgaria': 'flag-icon flag-icon-bg',
        'urkina Faso': 'flag-icon flag-icon-bf',
        'Burundi': 'flag-icon flag-icon-bi',
        'Cabo Verde': 'flag-icon flag-icon-cv',
        'Cambodia': 'flag-icon flag-icon-kh',
        'Cameroon': 'flag-icon flag-icon-cm',
        'Canada': 'flag-icon flag-icon-ca',
        'Cayman Islands': 'flag-icon flag-icon-ky',
        'Central African Republic': 'flag-icon flag-icon-cf',
        'Chad': 'flag-icon flag-icon-td',
        'Chile': 'flag-icon flag-icon-cl',
        'China': 'flag-icon flag-icon-cn',
        'Christmas Island': 'flag-icon flag-icon-cx',
        'Cocos (Keeling) Islands': 'flag-icon flag-icon-cc',
        'Colombia': 'flag-icon flag-icon-co',
        'Comoros': 'flag-icon flag-icon-km',
        'Cook Islands': 'flag-icon flag-icon-ck',
        'Costa Rica': 'flag-icon flag-icon-cr',
        'Croatia': 'flag-icon flag-icon-hr',
        'Cuba': 'flag-icon flag-icon-cu',
        'Curaçao': 'flag-icon flag-icon-cw',
        'Cyprus': 'flag-icon flag-icon-cy',
        'Czech Republic': 'flag-icon flag-icon-cz',
        'Côte d\'Ivoire': 'flag-icon flag-icon-ci',
        'Democratic Republic of Congo': 'flag-icon flag-icon-cd',
        'Denmark': 'flag-icon flag-icon-dk',
        'Djibouti': 'flag-icon flag-icon-dj',
        'Dominica': 'flag-icon flag-icon-dm',
        'Dominican Republic': 'flag-icon flag-icon-do',
        'Ecuador': 'flag-icon flag-icon-ec',
        'Egypt': 'flag-icon flag-icon-eg',
        'El Salvador': 'flag-icon flag-icon-sv',
        'Equatorial Guinea': 'flag-icon flag-icon-gq',
        'Eritrea': 'flag-icon flag-icon-er',
        'Estonia': 'flag-icon flag-icon-ee',
        'Eswatini': 'flag-icon flag-icon-sz',
        'Ethiopia': 'flag-icon flag-icon-et',
        'Falkland Islands': 'flag-icon flag-icon-fk',
        'Faroe Islands': 'flag-icon flag-icon-fo',
        'Federated States of Micronesia': 'flag-icon flag-icon-fm',
        'Fiji': 'flag-icon flag-icon-fj',
        'Finland': 'flag-icon flag-icon-fi',
        'France': 'flag-icon flag-icon-fr',
        'French Guiana': 'flag-icon flag-icon-gf',
        'French Polynesia': 'flag-icon flag-icon-pf',
        'French Southern Territories': 'flag-icon flag-icon-tf',
        'Gabon': 'flag-icon flag-icon-ga',
        'Gambia': 'flag-icon flag-icon-gm',
        'Georgia': 'flag-icon flag-icon-ge',
        'Germany': 'flag-icon flag-icon-de',
        'Ghana': 'flag-icon flag-icon-gh',
        'Gibraltar': 'flag-icon flag-icon-gi',
        'Greece': 'flag-icon flag-icon-gr',
        'Greenland': 'flag-icon flag-icon-gl',
        'Grenada': 'flag-icon flag-icon-gd',
        'Guadeloupe': 'flag-icon flag-icon-gp',
        'Guam': 'flag-icon flag-icon-gu',
        'Guatemala': 'flag-icon flag-icon-gt',
        'Guernsey': 'flag-icon flag-icon-gg',
        'Guinea': 'flag-icon flag-icon-gn',
        'Guinea-Bissau': 'flag-icon flag-icon-gw',
        'Guyana': 'flag-icon flag-icon-gy',
        'Haiti': 'flag-icon flag-icon-ht',
        'Heard Island and McDonald Islands': 'flag-icon flag-icon-hm',
        'Holy See': 'flag-icon flag-icon-va',
        'Honduras': 'flag-icon flag-icon-hn',
        'Hong Kong': 'flag-icon flag-icon-hk',
        'Hungary': 'flag-icon flag-icon-hu',
        'Iceland': 'flag-icon flag-icon-is',
        'India': 'flag-icon flag-icon-in',
        'Indonesia': 'flag-icon flag-icon-id',
        'Iran': 'flag-icon flag-icon-ir',
        'Iraq': 'flag-icon flag-icon-iq',
        'Ireland': 'flag-icon flag-icon-ie',
        'Isle of Man': 'flag-icon flag-icon-im',
        'Israel': 'flag-icon flag-icon-il',
        'Italy': 'flag-icon flag-icon-it',
        'Jamaica': 'flag-icon flag-icon-jm',
        'Japan': 'flag-icon flag-icon-jp',
        'Jersey': 'flag-icon flag-icon-je',
        'Jordan': 'flag-icon flag-icon-jo',
        'Kazakhstan': 'flag-icon flag-icon-kz',
        'Kenya': 'flag-icon flag-icon-ke',
        'Kiribati': 'flag-icon flag-icon-ki',
        'Kuwait': 'flag-icon flag-icon-kw',
        'Kyrgyzstan': 'flag-icon flag-icon-kg',
        'Laos': 'flag-icon flag-icon-la',
        'Latvia': 'flag-icon flag-icon-lv',
        'Lebanon': 'flag-icon flag-icon-lb',
        'Lesotho': 'flag-icon flag-icon-ls',
        'Liberia': 'flag-icon flag-icon-lr',
        'Libya': 'flag-icon flag-icon-ly',
        'Liechtenstein': 'flag-icon flag-icon-li',
        'Lithuania': 'flag-icon flag-icon-lt',
        'Luxembourg': 'flag-icon flag-icon-lu',
        'Macau': 'flag-icon flag-icon-mo',
        'Madagascar': 'flag-icon flag-icon-mg',
        'Malawi': 'flag-icon flag-icon-mw',
        'Malaysia': 'flag-icon flag-icon-my',
        'Maldives': 'flag-icon flag-icon-mv',
        'Mali': 'flag-icon flag-icon-ml',
        'Malta': 'flag-icon flag-icon-mt',
        'Marshall Islands': 'flag-icon flag-icon-mh',
        'Martinique': 'flag-icon flag-icon-mq',
        'Mauritania': 'flag-icon flag-icon-mr',
        'Mauritius': 'flag-icon flag-icon-mu',
        'Mayotte': 'flag-icon flag-icon-yt',
        'Mexico': 'flag-icon flag-icon-mx',
        'Moldova': 'flag-icon flag-icon-md',
        'Monaco': 'flag-icon flag-icon-mc',
        'Mongolia': 'flag-icon flag-icon-mn',
        'Montenegro': 'flag-icon flag-icon-me',
        'Montserrat': 'flag-icon flag-icon-ms',
        'Morocco': 'flag-icon flag-icon-ma',
        'Mozambique': 'flag-icon flag-icon-mz',
        'Myanmar': 'flag-icon flag-icon-mm',
        'Namibia': 'flag-icon flag-icon-na',
        'Nauru': 'flag-icon flag-icon-nr',
        'Nepal': 'flag-icon flag-icon-np',
        'Netherlands': 'flag-icon flag-icon-nl',
        'New Caledonia': 'flag-icon flag-icon-nc',
        'New Zealand': 'flag-icon flag-icon-nz',
        'Nicaragua': 'flag-icon flag-icon-ni',
        'Niger': 'flag-icon flag-icon-ne',
        'Nigeria': 'flag-icon flag-icon-ng',
        'Niue': 'flag-icon flag-icon-nu',
        'Norfolk Island': 'flag-icon flag-icon-nf',
        'North Korea': 'flag-icon flag-icon-kp',
        'North Macedonia': 'flag-icon flag-icon-mk',
        'Northern Mariana Islands': 'flag-icon flag-icon-mp',
        'Norway': 'flag-icon flag-icon-no',
        'Oman': 'flag-icon flag-icon-om',
        'Pakistan': 'flag-icon flag-icon-pk',
        'Palau': 'flag-icon flag-icon-pw',
        'Panama': 'flag-icon flag-icon-pa',
        'Papua New Guinea': 'flag-icon flag-icon-pg',
        'Paraguay': 'flag-icon flag-icon-py',
        'Peru': 'flag-icon flag-icon-pe',
        'Philippines': 'flag-icon flag-icon-ph',
        'Pitcairn': 'flag-icon flag-icon-pn',
        'Poland': 'flag-icon flag-icon-pl',
        'Portugal': 'flag-icon flag-icon-pt',
        'Puerto Rico': 'flag-icon flag-icon-pr',
        'Qatar': 'flag-icon flag-icon-qa',
        'Republic of the Congo': 'flag-icon flag-icon-cg',
        'Romania': 'flag-icon flag-icon-ro',
        'Russia': 'flag-icon flag-icon-ru',
        'Rwanda': 'flag-icon flag-icon-rw',
        'Réunion': 'flag-icon flag-icon-re',
        'Saint Barthélemy': 'flag-icon flag-icon-bl',
        'Saint Helena, Ascension and Tristan da Cunha': 'flag-icon flag-icon-sh',
        'Saint Kitts and Nevis': 'flag-icon flag-icon-kn',
        'Saint Lucia': 'flag-icon flag-icon-lc',
        'Saint Martin': 'flag-icon flag-icon-mf',
        'Saint Pierre and Miquelon': 'flag-icon flag-icon-pm',
        'Saint Vincent and the Grenadines': 'flag-icon flag-icon-vc',
        'Samoa': 'flag-icon flag-icon-ws',
        'San Marino': 'flag-icon flag-icon-sm',
        'Sao Tome and Principe': 'flag-icon flag-icon-st',
        'Saudi Arabia': 'flag-icon flag-icon-sa',
        'Senegal': 'flag-icon flag-icon-sn',
        'Serbia': 'flag-icon flag-icon-rs',
        'Seychelles': 'flag-icon flag-icon-sc',
        'Sierra Leone': 'flag-icon flag-icon-sl',
        'Singapore': 'flag-icon flag-icon-sg',
        'Sint Maarten': 'flag-icon flag-icon-sx',
        'Slovakia': 'flag-icon flag-icon-sk',
        'Slovenia': 'flag-icon flag-icon-si',
        'Solomon Islands': 'flag-icon flag-icon-sb',
        'Somalia': 'flag-icon flag-icon-so',
        'South Africa': 'flag-icon flag-icon-za',
        'South Georgia and the South Sandwich Islands': 'flag-icon flag-icon-g',
        'South Korea': 'flag-icon flag-icon-kr',
        'South Sudan': 'flag-icon flag-icon-ss',
        'Spain': 'flag-icon flag-icon-es',
        'Sri Lanka': 'flag-icon flag-icon-lk',
        'State of Palestine': 'flag-icon flag-icon-ps',
        'Sudan': 'flag-icon flag-icon-sd',
        'Suriname': 'flag-icon flag-icon-sr',
        'Svalbard and Jan Mayen': 'flag-icon flag-icon-sj',
        'Sweden': 'flag-icon flag-icon-se',
        'Switzerland': 'flag-icon flag-icon-ch',
        'Syria': 'flag-icon flag-icon-sy',
        'Taiwan': 'flag-icon flag-icon-tw',
        'Tajikistan': 'flag-icon flag-icon-tj',
        'Tanzania': 'flag-icon flag-icon-tz',
        'Thailand': 'flag-icon flag-icon-th',
        'Timor-Leste': 'flag-icon flag-icon-tl',
        'Togo': 'flag-icon flag-icon-tg',
        'Tokelau': 'flag-icon flag-icon-tk',
        'Tonga': 'flag-icon flag-icon-to',
        'Trinidad and Tobago': 'flag-icon flag-icon-tt',
        'Tunisia': 'flag-icon flag-icon-tn',
        'Turkmenistan': 'flag-icon flag-icon-tm',
        'Turks and Caicos Islands': 'flag-icon flag-icon-tc',
        'Tuvalu': 'flag-icon flag-icon-tv',
        'Türkiye': 'flag-icon flag-icon-tr',
        'Uganda': 'flag-icon flag-icon-ug',
        'Ukraine': 'flag-icon flag-icon-ua',
        'United Arab Emirates': 'flag-icon flag-icon-ae',
        'United Kingdom': 'flag-icon flag-icon-gb',
        'United States Minor Outlying Islands': 'flag-icon flag-icon-um',
        'United States': 'flag-icon flag-icon-us', #USA
        'Uruguay': 'flag-icon flag-icon-uy',
        'Uzbekistan': 'flag-icon flag-icon-uz',
        'Vanuatu': 'flag-icon flag-icon-vu',
        'Venezuela': 'flag-icon flag-icon-ve',
        'Vietnam': 'flag-icon flag-icon-vn',
        'Virgin Islands (British)': 'flag-icon flag-icon-vg',
        'Virgin Islands (U.S.)': 'flag-icon flag-icon-vi',
        'Wallis and Futuna': 'flag-icon flag-icon-wf',
        'Western Sahara': 'flag-icon flag-icon-eh',
        'Yemen': 'flag-icon flag-icon-ye',
        'Zambia': 'flag-icon flag-icon-zm',
        'Zimbabwe': 'flag-icon flag-icon-zw',
    }

    browsers = {
        'Firefox': 'fa-brands fa-firefox text-warning',
        'Chrome': 'fa-brands fa-chrome text-primary',
        'Safari': 'fa-brands fa-safari text-info',
        'Microsoft Edge': 'fa-brands fa-edge text-success',
        'Internet Explorer': 'fa-brands fa-internet-explorer text-teal',
        'Opera': 'fa-brands fa-opera text-danger',
        'Brave': 'fa-brands fa-brave text-danger',
        'Tor': 'fa-solid fa-t text-dark',
        'Unknown': 'fa-brands fa-octopus-deploy text-dark',
    }

    oss = {
        'Windows': 'fa-brands fa-windows text-primary',
        'Linux': 'fa-brands fa-linux text-primary',
        'macOS': 'fa-brands fa-apple text-danger',
        'Android': 'fa-brands fa-android text-danger',
        'iOS': 'fa-brands fa-apple text-danger',
        'Unknown OS': 'fa-solid fa-globe text-info',
    }

    visitor = {
        'visitor_id': data.visitor_id,
        'visitor_ip': data.visitor_ip,
        'device': data.device,
        'device_brand': data.device_brand,
        'device_model': data.device_model,
        'device_screen': data.device_screen,
        'platform': data.platform,
        'platform_version': data.platform_version,
        'browser': data.browser,
        'language': data.language,
        'continent': data.continent,
        'continent_code': data.continent_code,
        'country': data.country,
        'country_code': data.country_code,
        'region': data.region,
        'region_code': data.region_code,
        'city': data.city,
        'district': data.district,
        'zip': data.zip,
        'lat': data.lat,
        'lon': data.lon,
        'timezone': data.timezone,
        'currency': data.currency,
        'dialing_code': data.dialing_code,
        'source': data.source,
        'flag': flags.get(data.country),
        'browser_icon': browsers.get(data.browser, browsers['Unknown']),
        'os_icon': oss.get(data.platform, oss['Unknown OS'])
    }
    
    context = {
        'visitor': visitor,
        'visits': visits
    }
    return render(request, 'work/visits/visitor-profile.html', context)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def AdminViewVisitorLogs(request, code):
    visitor = Sitevisitor.objects.filter(visitor_id=code).first()
    visits = Sitevisit.objects.filter(visitor_id=visitor.id).all()
    
    context = {
        'visitor': visitor,
        'visits': visits
    }
    return render(request, 'work/visits/visitor-logs.html', context)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def AdminDeleteVisitor(request, code):
    try:
        if not request.POST['dvisitorid']:
            messages.error(request, "Visitor ID is required.")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        visitor = Sitevisitor.objects.filter(visitor_id=request.POST['dvisitorid']).first()

        if not visitor:
            messages.error(request, "Visitor not found.")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        
        visitor.delete()

        messages.success(request, "Visitor's records deleted successfully!")
    except KeyError as e:
        messages.error(request, f"Missing parameter: {str(e)}")
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def AdminAllVisits(request):
    today = now().date()
    todays_visits = Sitevisit.objects.filter(created_at__date=today).order_by('-created_at')
    paginator1 = Paginator(todays_visits, 15)  # Show 15 leads per page
    page_number1 = request.GET.get('page')  # Get page number from URL
    page_obj1 = paginator1.get_page(page_number1)  # Get the correct page

    yesterday = now().date() - timedelta(days=1)
    yesterdays_visits = Sitevisit.objects.filter(created_at__date=yesterday).order_by('-created_at')
    paginator2 = Paginator(yesterdays_visits, 15)  # Show 15 leads per page
    page_number2 = request.GET.get('page')  # Get page number from URL
    page_obj2 = paginator2.get_page(page_number2)  # Get the correct page

    start_of_week = today - timedelta(days=today.weekday())  # Get Monday of the current week
    curweek_visits = Sitevisit.objects.filter(created_at__date__gte=start_of_week).order_by('-created_at')
    paginator3 = Paginator(curweek_visits, 15)  # Show 15 leads per page
    page_number3 = request.GET.get('page')  # Get page number from URL
    page_obj3 = paginator3.get_page(page_number3)  # Get the correct page

    start_of_current_week = today - timedelta(days=today.weekday())  # Get Monday of the current week
    start_of_previous_week = start_of_current_week - timedelta(weeks=1)  # Previous Monday
    end_of_previous_week = start_of_current_week - timedelta(days=1)  # Last Sunday
    prevweek_visits = Sitevisit.objects.filter(created_at__date__gte=start_of_previous_week, created_at__date__lte=end_of_previous_week).order_by('-created_at')
    paginator4 = Paginator(prevweek_visits, 15)  # Show 15 leads per page
    page_number4 = request.GET.get('page')  # Get page number from URL
    page_obj4 = paginator4.get_page(page_number4)  # Get the correct page

    start_of_month = today.replace(day=1)  # First day of current month
    curmonth_visits = Sitevisit.objects.filter(created_at__date__gte=start_of_month).order_by('-created_at')
    paginator5 = Paginator(curmonth_visits, 15)  # Show 15 leads per page
    page_number5 = request.GET.get('page')  # Get page number from URL
    page_obj5 = paginator5.get_page(page_number5)  # Get the correct page

    start_of_current_month = today.replace(day=1)  # First day of current month
    end_of_previous_month = start_of_current_month - timedelta(days=1)  # Last day of previous month
    start_of_previous_month = end_of_previous_month.replace(day=1)  # First day of previous month
    prevmonth_visits = Sitevisit.objects.filter(created_at__date__gte=start_of_previous_month, created_at__date__lte=end_of_previous_month).order_by('-created_at')
    paginator6 = Paginator(prevmonth_visits, 15)  # Show 15 leads per page
    page_number6 = request.GET.get('page')  # Get page number from URL
    page_obj6 = paginator6.get_page(page_number6)  # Get the correct page

    context = {
        'todays' : page_obj1,
        'yesterdays' : page_obj2,
        'current_weeks' : page_obj3,
        'previous_weeks' : page_obj4,
        'current_months' : page_obj5,
        'previous_months' : page_obj6,
    }
    return render(request, 'work/visits/visit-all.html', context)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def AdminViewVisitLogs(request, code):
    visit = Sitevisit.objects.filter(visit_id=code).first()
    
    context = {
        'visit': visit
    }
    return render(request, 'work/visits/visit-logs.html', context)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def AdminVisitLocations(request):
    today = now().date()
    yesterday = today - timedelta(days=1)

    # Get start of the current and previous weeks (Monday as start of the week)
    current_week_start = today - timedelta(days=today.weekday())
    previous_week_start = current_week_start - timedelta(weeks=1)
    previous_week_end = current_week_start - timedelta(days=1)

    # Get start of the current and previous months
    current_month_start = today.replace(day=1)
    previous_month_end = current_month_start - timedelta(days=1)
    previous_month_start = previous_month_end.replace(day=1)

    date_filters = {
        "today": {"created_at__date": today},
        "yesterday": {"created_at__date": yesterday},
        "current_week": {"created_at__date__gte": current_week_start},
        "previous_week": {"created_at__date__range": [previous_week_start, previous_week_end]},
        "current_month": {"created_at__date__gte": current_month_start},
        "previous_month": {"created_at__date__range": [previous_month_start, previous_month_end]},
    }

    columns = ["language", "continent", "country", "region", "city", "district", "zip", "timezone"]
    result = {}

    for key, date_filter in date_filters.items():
        result[key] = {}
        for column in columns:
            data = (
                Sitevisitor.objects.filter(**date_filter)
                .values(column)
                .annotate(count=Count("visitor_id", distinct=True))
                .order_by("-count")
            )
            result[key][column] = list(data)

    context = {
        'result': result
    }
    return render(request, 'work/visits/visit-locations.html', context)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def AdminVisitDevices(request):
    today = now().date()
    yesterday = today - timedelta(days=1)

    # Get start of the current and previous weeks (Monday as start of the week)
    current_week_start = today - timedelta(days=today.weekday())
    previous_week_start = current_week_start - timedelta(weeks=1)
    previous_week_end = current_week_start - timedelta(days=1)

    # Get start of the current and previous months
    current_month_start = today.replace(day=1)
    previous_month_end = current_month_start - timedelta(days=1)
    previous_month_start = previous_month_end.replace(day=1)

    date_filters = {
        "today": {"created_at__date": today},
        "yesterday": {"created_at__date": yesterday},
        "current_week": {"created_at__date__gte": current_week_start},
        "previous_week": {"created_at__date__range": [previous_week_start, previous_week_end]},
        "current_month": {"created_at__date__gte": current_month_start},
        "previous_month": {"created_at__date__range": [previous_month_start, previous_month_end]},
    }

    columns = ["device", "device_brand", "device_model", "device_screen"]
    result = {}

    for key, date_filter in date_filters.items():
        result[key] = {}
        for column in columns:
            data = (
                Sitevisitor.objects.filter(**date_filter)
                .values(column)
                .annotate(count=Count("visitor_id", distinct=True))
                .order_by("-count")
            )
            result[key][column] = list(data)

    context = {
        'result': result
    }
    return render(request, 'work/visits/visit-devices.html', context)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def AdminVisitSoftware(request):
    today = now().date()
    yesterday = today - timedelta(days=1)

    # Get start of the current and previous weeks (Monday as start of the week)
    current_week_start = today - timedelta(days=today.weekday())
    previous_week_start = current_week_start - timedelta(weeks=1)
    previous_week_end = current_week_start - timedelta(days=1)

    # Get start of the current and previous months
    current_month_start = today.replace(day=1)
    previous_month_end = current_month_start - timedelta(days=1)
    previous_month_start = previous_month_end.replace(day=1)

    date_filters = {
        "today": {"created_at__date": today},
        "yesterday": {"created_at__date": yesterday},
        "current_week": {"created_at__date__gte": current_week_start},
        "previous_week": {"created_at__date__range": [previous_week_start, previous_week_end]},
        "current_month": {"created_at__date__gte": current_month_start},
        "previous_month": {"created_at__date__range": [previous_month_start, previous_month_end]},
    }

    columns = ["platform", "platform_version", "browser", "browser_engine", "browser_configuration"]
    result = {}

    for key, date_filter in date_filters.items():
        result[key] = {}
        for column in columns:
            data = (
                Sitevisitor.objects.filter(**date_filter)
                .values(column)
                .annotate(count=Count("visitor_id", distinct=True))
                .order_by("-count")
            )
            result[key][column] = list(data)

    context = {
        'result': result
    }
    return render(request, 'work/visits/visit-software.html', context)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def AdminDeleteVisit(request, code):
    try:
        if not request.POST['dvisitid']:
            messages.error(request, "Visit ID is required.")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        visit = Sitevisit.objects.filter(visit_id=request.POST['dvisitid']).first()

        if not visit:
            messages.error(request, "Visit not found.")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        
        visit.delete()

        messages.success(request, "Visit's records deleted successfully!")
    except KeyError as e:
        messages.error(request, f"Missing parameter: {str(e)}")
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
