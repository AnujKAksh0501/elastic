from django.urls import path
from . import views

urlpatterns = [
    path('work/all-leads', views.AdminAllLeads, name='AdminAllLeads'),
    path('work/all-normal-leads', views.AdminNormalLeads, name='AdminNormalLeads'),
    path('work/all-premium-leads', views.AdminPremiumLeads, name='AdminPremiumLeads'),
    path('work/create-new-lead', views.AdminCreateLead, name='AdminCreateLead'),
    path('work/view-lead-details/<str:code>', views.AdminViewLeadDetails, name='AdminViewLeadDetails'),
    path('work/send-single-lead-email', views.AdminSingleLeadEmail, name='AdminSingleLeadEmail'),
    path('work/fetch-email-transactions-by-lead', views.AdminFetchEmailTransactions, name='AdminFetchEmailTransactions'),
    path('work/update-lead-details', views.AdminUpdateLeadDetails, name='AdminUpdateLeadDetails'),
    path('work/delete-lead', views.AdminDeleteLead, name='AdminDeleteLead'),

    path('work/all-contacts', views.AdminAllContacts, name='AdminAllContacts'),
    path('work/create-new-contact', views.AdminCreateContact, name='AdminCreateContact'),
    path('work/view-contact-details/<str:code>', views.AdminViewContactDetails, name='AdminViewContactDetails'),
    path('work/update-contact-details', views.AdminUpdateContactDetails, name='AdminUpdateContactDetails'),
    path('work/delete-contact', views.AdminDeleteContact, name='AdminDeleteContact'),

    
]