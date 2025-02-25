from django.urls import path, include
from . import views

urlpatterns = [
    path('work/hourly-site-visits', views.AdminHourlySiteVisits, name='AdminHourlySiteVisits'),
    path('work/daily-site-visits', views.AdminDailySiteVisits, name='AdminDailySiteVisits'),
    path('work/weekly-site-visits', views.AdminWeeklySiteVisits, name='AdminWeeklySiteVisits'),
    path('work/monthly-site-visits', views.AdminMonthlySiteVisits, name='AdminMonthlySiteVisits'),
    path('work/yearly-site-visits', views.AdminYearlySiteVisits, name='AdminYearlySiteVisits'),

    path('work/visits-overview', views.AdminVisitsOverview, name='AdminVisitsOverview'),
    path('work/all-visitors', views.AdminAllVisitors, name='AdminAllVisitors'),
    path('work/view-visitor-profile/<str:code>', views.AdminViewVisitorProfile, name='AdminViewVisitorProfile'),
    path('work/view-visitor-logs/<str:code>', views.AdminViewVisitorLogs, name='AdminViewVisitorLogs'),
    path('work/delete-visitor-logs', views.AdminDeleteVisitor, name='AdminDeleteVisitor'),

    path('work/locations', views.AdminVisitLocations, name='AdminVisitLocations'),
    path('work/devices', views.AdminVisitDevices, name='AdminVisitDevices'),
    path('work/software', views.AdminVisitSoftware, name='AdminVisitSoftware'),

    path('work/all-visits', views.AdminAllVisits, name='AdminAllVisits'),
    path('work/view-visit-logs/<str:code>', views.AdminViewVisitLogs, name='AdminViewVisitLogs'),
    path('work/delete-visit-details', views.AdminDeleteVisit, name='AdminDeleteVisit'),

    
]