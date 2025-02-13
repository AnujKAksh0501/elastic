from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.Welcome, name='Welcome'),

    path('sign-in', views.SignIn, name='SignIn'),
    path('sign-up', views.SignUp, name='SignUp'),
    path('sign-out', views.SignOut, name='SignOut'),
    path('verify-account/<str:code>', views.VerifyAccount, name='VerifyAccount'),
    path('forgot-password', views.ForgotPassword, name='ForgotPassword'),
    path('verify-email/<str:code>', views.VerifyEmail, name='VerifyEmail'),
    path('reset-password', views.ResetPassword, name='ResetPassword'),

    path('work/fetch-states-by-country', views.FetchStates, name='FetchStates'),
    path('work/dashboard', views.AdminDashboard, name='AdminDashboard'),

    path('work/all-companies', views.AdminAllCompanies, name='AdminAllCompanies'),
    path('work/create-new-company', views.AdminCreateCompany, name='AdminCreateCompany'),
    path('work/view-company-leads/<str:code>', views.AdminViewCompanyLeads, name='AdminViewCompanyLeads'),
    path('work/view-company-lead-details/<str:code>', views.AdminViewCompanyLeadDetails, name='AdminViewCompanyLeadDetails'),
    path('work/update-company-lead-details', views.AdminUpdateCompanyLeadDetails, name='AdminUpdateCompanyLeadDetails'),
    path('work/delete-company-lead', views.AdminDeleteCompanyLead, name='AdminDeleteCompanyLead'),
    path('work/edit-company-details/<str:code>', views.AdminEditCompanyDetails, name='AdminEditCompanyDetails'),
    path('work/update-company-details', views.AdminUpdateCompanyDetails, name='AdminUpdateCompanyDetails'),
    path('work/delete-company', views.AdminDeleteCompany, name='AdminDeleteCompany'),

    path('work/all-company-users/<str:code>', views.AdminAllCompanyUser, name='AdminAllCompanyUser'),
    path('work/add-new-company-user/<str:code>', views.AdminAddNewCompanyUser, name='AdminAddNewCompanyUser'),
    path('work/create-new-company-user', views.AdminCreateNewCompanyUser, name='AdminCreateNewCompanyUser'),
    path('work/view-user-details/<str:code>', views.AdminViewUserDetails, name='AdminViewUserDetails'),
    path('work/update-company-user-details', views.AdminUpdateCompanyUserDetails, name='AdminUpdateCompanyUserDetails'),
    path('work/delete-company-user', views.AdminDeleteCompanyUser, name='AdminDeleteCompanyUser'),

    path('work/all-groups', views.AdminAllGroups, name='AdminAllGroups'),
    path('work/create-new-group', views.AdminCreateNewGroup, name='AdminCreateNewGroup'),
    path('work/view-group-details/<str:code>', views.AdminViewGroupDetails, name='AdminViewGroupDetails'),
    path('work/update-group-details', views.AdminUpdateGroupDetails, name='AdminUpdateGroupDetails'),
    path('work/group-companies/<str:code>', views.AdminGroupCompanies, name='AdminGroupCompanies'),
    path('work/add-company-in-group', views.AdminCompanyInGroup, name='AdminCompanyInGroup'),
    path('work/delete-company-from-group', views.AdminDeleteCompanyFromGroup, name='AdminDeleteCompanyFromGroup'),
    path('work/delete-group', views.AdminDeleteGroup, name='AdminDeleteGroup'),

    path('work/all-websites', views.AdminAllWebsite, name='AdminAllWebsite'),
    path('work/add-new-website', views.AdminAddNewWebsite, name='AdminAddNewWebsite'),
    path('work/fetch-website-by-id', views.AdminFetchWebsite, name='AdminFetchWebsite'),
    path('work/update-website', views.AdminUpdateWebsite, name='AdminUpdateWebsite'),
    path('work/delete-website', views.AdminDeleteWebsite, name='AdminDeleteWebsite'),
    
    path('work/security-settings', views.AdminSecuritySettings, name='AdminSecuritySettings'),
    path('work/update-password', views.AdminUpdatePassword, name='AdminUpdatePassword'),
    path('work/enable-otp-authentication', views.AdminEnableOtp, name='AdminEnableOtp'),
    path('work/disable-otp-authentication', views.AdminDisableOtp, name='AdminDisableOtp'),
    
    path('', include('lead.urls')),
    path('', include('report.urls')),
]