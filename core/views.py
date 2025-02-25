from datetime import datetime, timedelta
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.hashers import make_password
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login, logout
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
from lead .models import *
from lead .serializer import *
from django.db.models import Q

@api_view(['GET'])
@permission_classes([AllowAny])
def Welcome(request):
    return redirect('SignIn')

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def SignUp(request):
    if request.method == 'GET':
        return render(request, 'auth/sign-up.html')
    elif request.method == 'POST':
        email = request.data.get("email")
        password = request.data.get("password")

        if email is None or password is None:
            messages.error(request, "Please provide all the details." )
            return redirect(SignUp)
        
        user = User.objects.filter(email=email).exists()
        if not user:
            account = User(
                username = request.POST['email'],
                first_name = request.POST['first_name'],
                last_name = request.POST['last_name'],
                email = request.POST['email'],
                mobile = request.POST['mobile'],
                password = make_password(request.POST['password']),
                role = 'Admin',
                added_by = request.POST['email'],
                admin = request.POST['email']
            )
            account.save()
            id = account.id

            otp = random.randint(100000, 999999)
            if id:
                otp = Otp(
                    email = request.POST['email'],
                    mobile = request.POST['mobile'],
                    otp = otp,
                )
                otp.save()
                oid = otp.id

                if oid:
                    html_mail = render_to_string('emails/account-verification-otp.html', {
                        'name': request.POST['first_name'],
                        'otp': otp
                    })
                    plain_message = strip_tags(html_mail)

                    message = EmailMultiAlternatives(
                        subject = 'Account Verification OTP',
                        body = plain_message,
                        from_email = "apptexit@apptexit.com",
                        to = [request.POST['email']]
                    )
                    message.attach_alternative(html_mail, 'text/html')
                    send_mail(message)

                    messages.success(request, "Your account has been created successfully!")
                    return redirect(VerifyAccount, otp.code)
            else:
                messages.success(request, "Something went wrong!")
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            messages.info(request, "Your account has already been created!")
            return redirect(SignIn)

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def SignIn(request):
    if request.method == 'GET':
        return render(request, 'auth/sign-in.html')
    elif request.method == 'POST':
        try:
            email = request.data.get("email")
            password = request.data.get("password")

            if email is None or password is None:
                messages.error(request, "Please enter your registered email and password." )
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            
            if User.objects.filter(email=email).exists():
                user = User.objects.filter(email=email).first()

                if user.is_active == 1:
                    auth = authenticate(username=email, password=password)

                    if not auth:
                        messages.warning(request, "Please enter correct credentials." )
                        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
                    
                    user.is_online = True
                    user.save()
                    token = Token.objects.get_or_create(user=user)[0].key

                    if token:
                        login(request, user)
                    return redirect(AdminDashboard)
                else:
                    otp = Otp(
                        email = request.POST['email'],
                        mobile = request.POST['mobile'],
                        otp = otp,
                    )
                    otp.save()
                    oid = otp.id

                    if oid:
                        html_mail = render_to_string('emails/account-verification-otp.html', {
                            'name': request.POST['first_name'],
                            'otp': otp
                        })
                        plain_message = strip_tags(html_mail)

                        message = EmailMultiAlternatives(
                            subject = 'Account Verification OTP',
                            body = plain_message,
                            from_email = None,
                            to = [request.POST['email']]
                        )
                        message.attach_alternative(html_mail, 'text/html')
                        send_mail(message)

                        messages.success(request, "Your account has been created successfully!")
                        return redirect(VerifyAccount, otp.code)
            else:
                messages.warning(request, "Your account is not created! Please Sign Up first." )
        except KeyError as e:
            messages.error(request, f"Missing parameter: {str(e)}")
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")    
            
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def VerifyAccount(request, code):
    if request.method == 'GET':
        otp = Otp.objects.filter(code=code).first()

        return render(request, 'auth/verify-account.html', otp)
    elif request.method == 'POST':
        try:
            fetch = Otp.objects.filter(code=request.POST['code']).first()

            otp = request.POST['o1']+request.POST['o2']+request.POST['o4']+request.POST['o3']+request.POST['o5']+request.POST['o6']

            if fetch.otp == otp:
                fetch.status = 'Verified'
                fetch.save()

                account = User.objects.filter(email=fetch.email).first()
                account.is_active = 1
                account.save()

                messages.success(request, "Your account has been verified successfully!")
                return redirect(SignIn)
            else:
                messages.warning(request, "Please enter correct OTP." )
        except KeyError as e:
            messages.error(request, f"Missing parameter: {str(e)}")
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
        
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def ForgotPassword(request):
    if request.method == 'GET':
        return render(request, 'auth/forgot-password.html')
    elif request.method == 'POST':
        try:
            if User.objects.filter(email=request.POST['email']).exists():
                account = User.objects.filter(email=request.POST['email']).first()

                otp = Otp(
                    email = account.email,
                    mobile = account.mobile,
                    otp = otp,
                )
                otp.save()
                oid = otp.id

                if oid:
                    html_mail = render_to_string('emails/email-verification-otp.html', {
                        'name': account.first_name,
                        'otp': otp
                    })
                    plain_message = strip_tags(html_mail)

                    message = EmailMultiAlternatives(
                        subject = 'Account Verification OTP',
                        body = plain_message,
                        from_email = None,
                        to = [request.POST['email']]
                    )
                    message.attach_alternative(html_mail, 'text/html')
                    send_mail(message)

                    messages.success(request, "OTP for account password reset has been sent successfully!")
                    return redirect(VerifyEmail, otp.code)
            else:
                messages.error(request, "Email is not registered!!")
        except KeyError as e:
            messages.error(request, f"Missing parameter: {str(e)}")
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def VerifyEmail(request, code):
    if request.method == 'GET':
        otp = Otp.objects.filter(code=code).first()

        return render(request, 'auth/verify-email.html', otp)
    elif request.method == 'POST':
        try:
            fetch = Otp.objects.filter(code=request.POST['code']).first()

            otp = request.POST['o1']+request.POST['o2']+request.POST['o4']+request.POST['o3']+request.POST['o5']+request.POST['o6']+request.POST['o7']

            if fetch.otp == otp:
                fetch.status = 'Verified'
                fetch.save()

                code = ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits, k=36))
                account = User.objects.filter(email=fetch.email).first()
                account.is_active = 1
                account.password_reset_code = code
                account.save()

                messages.success(request, "Your account has been verified successfully!")
                return redirect(ResetPassword, code)
            else:
                messages.error(request, "Please enter correct OTP." )
        except KeyError as e:
            messages.error(request, f"Missing parameter: {str(e)}")
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def ResetPassword(request, code):
    if request.method == 'GET':
        account = User.objects.filter(unique_code=code).first()

        return render(request, 'auth/reset-password.html', account)
    elif request.method == 'POST':
        try:
            account = User.objects.filter(password_reset_code=code).first()
            if not account:
                messages.error(request, "User not found.")
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

            account.password = make_password(request.POST['password'])
            account.is_online = False
            account.save()

            request.user.auth_token.delete()
            request.session.flush()
            logout(request)
            messages.error(request, "Your account password changed successfully!" )
            return redirect(SignIn)
        except KeyError as e:
            messages.error(request, f"Missing parameter: {str(e)}")
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@api_view(['POST'])
@permission_classes([AllowAny])
def FetchStates(request):
    try:
        if request.POST['country']:
            country = Country.objects.filter(name=request.POST['country']).first()
            states = State.objects.filter(country_id=country.id).all()

            if not states:
                return Response({'error': 'No states found for the given country ID.'}, status=404)

            serialized = StateSerializer(states, many=True)

            return Response({"status": HTTP_200_OK, "data": serialized.data})
    except Exception as e:
        return Response({'error': f"An error occurred: {str(e)}"}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def AdminDashboard(request):
    websites = Website.objects.filter(status='Active').all()

    data = []
    today = datetime.today().date()
    yesterday = today - timedelta(days=1)

    for website in websites:
        tleads = Lead.objects.filter(Q(source=website.domain) & Q(created_at__date=today)).count()
        yleads = Lead.objects.filter(Q(source=website.domain) & Q(created_at__date=yesterday)).count()
 
        # Calculate the percentage change, avoid division by zero
        if tleads > 0:
            change = ((tleads - yleads) / tleads) * 100
        else:
            change = 0  # Default to 0% change if tleads is 0

        data.append({
            'domain': website.domain,
            'today': tleads,
            'yesterday': yleads,
            'change': change
        })

    context = {
        'data': data
    }
    return render(request, 'work/dashboard.html', context)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def AdminAllCompanies(request):
    rawdata = Company.objects.all()
    groups = Group.objects.all()
    
    companies = []
    for company in rawdata:
        if(User.objects.filter(admin=company.admin).exists()):
            count = User.objects.filter(admin=company.admin).count()
            companies.append({
                'name': company.name,
                'email': company.email,
                'mobile': company.mobile,
                'unique_code': company.unique_code,
                'users': count,
                'status': company.status,
            })
        else:
            companies.append({
                'name': company.name,
                'email': company.email,
                'mobile': company.mobile,
                'unique_code': company.unique_code,
                'users': 0,
                'status': company.status,
            })

    context = {
        'groups': groups,
        'companies': companies
    }
    return render(request, 'work/company/all.html', context)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def AdminCreateCompany(request):
    if request.method == 'GET':
        groups = Group.objects.all()

        context = {
            'groups': groups
        }
        return render(request, 'work/company/create.html', context)
    elif request.method == 'POST':
        try:
            account = User(
                username = request.POST['email'],
                first_name = request.POST['first_name'],
                last_name = request.POST['last_name'],
                email = request.POST['email'],
                mobile = request.POST['mobile'],
                password = make_password('NewUser@123456'),
                role = 'Admin',
                added_by = request.POST['email'],
                admin = request.POST['email']
            )
            account.save()
            id = account.id

            company = Company(
                user_id = id,
                group = request.POST['group'],
                name = request.POST['name'],
                email = request.POST['email'],
                mobile = request.POST['mobile'],
                description = request.POST['desc'],
                added_by = request.POST['email'],
                admin = request.POST['email']
            )
            company.save()
            
            messages.success(request, "New company created successfully!")
        except KeyError as e:
            messages.error(request, f"Missing parameter: {str(e)}")
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def AdminAllCompanyLead(request, code):
    company = Company.objects.filter(unique_code=code).first()
    leads = Companylead.objects.filter(company_id=company.id).get().order_by('-created_at')
    accounts = User.objects.filter(admin=company.admin).get()

    paginator = Paginator(leads, 15)  # Show 15 leads per page
    page_number = request.GET.get('page')  # Get page number from URL
    page_obj = paginator.get_page(page_number)  # Get the correct page

    context = {
        'company': company,
        'leads': page_obj,
        'accounts': accounts
    }
    return render(request, 'work/company/lead-all.html', context)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def AdminViewCompanyLeads(request, code):
    company = Company.objects.filter(unique_code=code).first()
    leads = Companylead.objects.filter(company_id=company.id).all()

    context = {
        'company': company,
        'leads': leads
    }
    return render(request, 'work/company/lead-all.html', context)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def AdminViewCompanyLeadDetails(request, code):
    lead = Companylead.objects.filter(unique_code=code).first()
    if not lead:
        messages.error(request, "Lead not found.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    
    company = Company.objects.filter(id=lead.company_id).first()
    accounts = User.objects.filter(admin=company.admin).all()

    context = {
        'lead': lead,
        'company': company,
        'accounts': accounts
    }
    return render(request, 'work/company/lead-view.html', context)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def AdminUpdateCompanyLeadDetails(request):
    try:
        if not request.POST['lead']:
            messages.error(request, "Lead ID is required.")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        
        lead = Companylead.objects.filter(id=request.POST['lead']).first()
        if not lead:
            messages.error(request, "Lead not found.")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        # Update lead details if provided
        if request.POST['assign'] != '' and request.POST['assign'] != lead.assign_id:
            lead.assign_id = request.POST['assign']
        if request.POST['name'] != '' and request.POST['name'] != lead.name:
            lead.name = request.POST['name']
        if request.POST['email'] != '' and request.POST['email'] != lead.email:
            lead.email = request.POST['email']
        if request.POST['mobile'] != '' and request.POST['mobile'] != lead.mobile:
            lead.mobile = request.POST['mobile']
        if request.POST['part'] != '' and request.POST['part'] != lead.part:
            lead.part = request.POST['part']
        if request.POST['make'] != '' and request.POST['make'] != lead.make:
            lead.make = request.POST['make']
        if request.POST['model'] != '' and request.POST['model'] != lead.model:
            lead.model = request.POST['model']
        if request.POST['year'] != '' and request.POST['year'] != lead.year:
            lead.year = request.POST['year']
        if request.POST['size'] != '' and request.POST['size'] != lead.size:
            lead.size = request.POST['size']
        if request.POST['type'] != '' and request.POST['type'] != lead.type:
            lead.type = request.POST['type']
        if request.POST['premium'] != '' and request.POST['premium'] != lead.is_premium:
            lead.is_premium = request.POST['premium']
        if request.POST['status'] != '' and request.POST['status'] != lead.status:
            lead.status = request.POST['status']

        lead.updated_by = request.user.email
        lead.save()

        messages.success(request, "Company lead details updated successfully!")
    except KeyError as e:
        messages.error(request, f"Missing parameter: {str(e)}")
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def AdminDeleteCompanyLead(request):
    try:
        if not request.POST['dclid']:
            messages.error(request, "Lead ID is required.")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        
        lead = Companylead.objects.filter(id=request.POST['dclid']).first()
        if not lead:
            messages.error(request, "Lead not found.")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        
        lead.delete()

        messages.success(request, "Company lead deleted successfully!")
    except KeyError as e:
        messages.error(request, f"Missing parameter: {str(e)}")
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def AdminEditCompanyDetails(request, code):
    groups = Group.objects.all()
    company = Company.objects.filter(unique_code=code).first()
    if not company:
        messages.error(request, "Company not found.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    
    users = User.objects.filter(admin=company.admin).all()

    context = {
        'groups': groups,
        'company': company,
        'users': users
    }
    return render(request, 'work/company/edit.html', context)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def AdminUpdateCompanyDetails(request):
    if not request.POST['company']:
        messages.error(request, "Company ID is required.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    
    company = Company.objects.filter(unique_code=request.POST['company']).first()
    if not company:
        messages.error(request, "Company not found.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        
    admin = User.objects.filter(id=request.POST['admin']).first()
    email = Groupmail.objects.filter(Q(email=company.email) & Q(group=company.group)).first()

    if request.FILES.get('logo') != None:
        company.logo = request.FILES.get('logo')
    if admin.id != company.user_id:
        company.user_id = admin.id
    if admin.email != company.admin:
        company.admin = admin.email
    if request.POST['group'] != '' and request.POST['group'] != company.group:
        if email:
            email.group = request.POST['group']
        company.group = request.POST['group']
    if request.POST['name'] != '' and request.POST['name'] != company.name:
        company.name = request.POST['name']
    if request.POST['email'] != '' and request.POST['email'] != company.email:
        if email:
            email.email = request.POST['email']
        company.email = request.POST['email']
    if request.POST['mobile'] != '' and request.POST['mobile'] != company.mobile:
        company.mobile = request.POST['mobile']
    if request.POST['desc'] != '' and request.POST['desc'] != company.description:
        company.description = request.POST['desc']
    if request.POST['cstatus'] != '' and request.POST['cstatus'] != company.status:
        company.status = request.POST['cstatus']

    company.updated_by = request.user.email
    email.save()
    company.save()

    messages.success(request, "Company details updated successfully!")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def AdminChangeCompanyGroup(request):
    if not request.POST['company']:
        messages.error(request, "Company ID is required.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    
    company = Company.objects.filter(unique_code=request.POST['company']).first()
    if not company:
        messages.error(request, "Company not found.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    
    company.group = request.POST['group']
    company.save()

    messages.success(request, "Company group updated successfully!")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def AdminDeleteCompany(request):
    try:
        if not request.POST['dcid']:
            messages.error(request, "Company ID is required.")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        
        company = Company.objects.filter(id=request.POST['dcid']).first()
        if not company:
            messages.error(request, "Company not found.")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        company.delete()

        messages.success(request, "Company details deleted successfully!")
    except KeyError as e:
        messages.error(request, f"Missing parameter: {str(e)}")
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
    
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def AdminAllCompanyUser(request, code):
    company = Company.objects.filter(unique_code=code).first()
    accounts = User.objects.filter(admin=company.admin).all().order_by('-created_at')

    paginator = Paginator(accounts, 15)  # Show 15 leads per page
    page_number = request.GET.get('page')  # Get page number from URL
    page_obj = paginator.get_page(page_number)  # Get the correct page
    
    context = {
        'company': company,
        'accounts': page_obj
    }
    return render(request, 'work/company/user-all.html', context)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def AdminAddNewCompanyUser(request, code):
    if code == 'New':
        company = Company.objects.all()
        
        context = {
            'type': 'New Company',
            'company': company
        }
        return render(request, 'work/company/user-add.html', context)
    else:
        company = Company.objects.filter(unique_code=code).first()
        
        context = {
            'type': 'Existing Company',
            'company': company
        }
        return render(request, 'work/company/user-add.html', context)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def AdminCreateNewCompanyUser(request):
    try:
        company = Company.objects.filter(id=request.POST['company']).first()

        account = User(
            username = request.POST['email'],
            first_name = request.POST['first_name'],
            last_name = request.POST['last_name'],
            email = request.POST['email'],
            mobile = request.POST['mobile'],
            password = make_password('NewUser@123456'),
            role = 'User',
            added_by = company.admin,
            admin = company.admin,
            otp_enabled = request.POST['otp_enable']
        )
        account.save()

        email = Groupmail(
            group = company.group,
            email = request.POST['email'],
        )
        email.save()
        
        messages.success(request, "New user created successfully!")
    except KeyError as e:
        messages.error(request, f"Missing parameter: {str(e)}")
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def AdminViewUserDetails(request, code):
    account = User.objects.filter(unique_code=code).first()
    if not account:
        messages.error(request, "User not found.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    company = Company.objects.filter(admin=account.admin).first()
    
    context = {
        'account': account,
        'company': company
    }
    return render(request, 'work/company/user-view.html', context)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def AdminUpdateCompanyUserDetails(request):
    try:
        account = User.objects.filter(unique_code=request.POST['account']).first()
        company = Company.objects.filter(admin=account.admin).first()

        if request.POST['first_name'] != '' and request.POST['first_name'] != account.first_name:
            account.first_name = request.POST['first_name']
        if request.POST['last_name'] != '' and request.POST['last_name'] != account.last_name:
            account.last_name = request.POST['last_name']
        if request.POST['email'] != '' and request.POST['email'] != account.email:
            email = Groupmail.objects.filter(Q(email=account.email) & Q(group=company.group)).first()
            email.email = request.POST['email']
            email.save()

            account.email = request.POST['email']
        if request.POST['mobile'] != '' and request.POST['mobile'] != account.mobile:
            account.mobile = request.POST['mobile']
        if request.POST['otp_enable'] != '' and request.POST['otp_enable'] != account.otp_enabled:
            account.otp_enabled = request.POST['otp_enable']

        account.updated_by = request.user.email
        account.save()

        messages.success(request, "Company user details updated successfully!")
    except KeyError as e:
        messages.error(request, f"Missing parameter: {str(e)}")
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def AdminDeleteCompanyUser(request):
    try:
        acc = User.objects.filter(id=request.POST['duid']).first()
        acc.delete()

        messages.success(request, "User details deleted successfully!")
    except KeyError as e:
        messages.error(request, f"Missing parameter: {str(e)}")
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def AdminViewCompanyEmails(request):
    companies = Company.objects.all()

    try:
        emails = Companyemail.objects.order_by('id')
    except Companyemail.DoesNotExist:
        emails = None

    paginator = Paginator(emails, 15)  # Show 15 leads per page
    page_number = request.GET.get('page')  # Get page number from URL
    page_obj = paginator.get_page(page_number)  # Get the correct page
    
    context = {
        'companies': companies,
        'emails': page_obj
    }
    return render(request, 'work/company/emails.html', context)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def AdminAddNewCompanyEmail(request):
    if request.method == 'POST':
        try:
            email = Companyemail(
                company_id = request.POST['company'],
                email = request.POST['email'],
            )
            email.save()

            messages.success(request, "New company email has been added successfully!")
        except KeyError as e:
            messages.error(request, f"Missing parameter: {str(e)}")
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def AdminDeleteCompanyEmail(request):
    try:
        email = Companyemail.objects.filter(id=request.POST['deid']).first()
        email.delete()

        messages.success(request, "Company email deleted successfully!")
    except KeyError as e:
        messages.error(request, f"Missing parameter: {str(e)}")
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def AdminAllGroups(request):
    companies = Company.objects.all()
    groups = Group.objects.all()
    
    context = {
        'companies': companies,
        'groups': groups
    }
    return render(request, 'work/group-all.html', context)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def AdminCreateNewGroup(request):
    if request.method == 'GET':
        return render(request, 'work/group-create.html')
    elif request.method == 'POST':
        try:
            rules = []
            fields = request.POST.getlist('field[]')
            conditions = request.POST.getlist('condition[]')
            values = request.POST.getlist('value[]')
            logics = request.POST.getlist('logic[]')
            count = len(fields)

            for i in range(count):
                rules.append({
                    'field': fields[i],
                    'condition': conditions[i],
                    'value': values[i],
                    'logic': logics[i],
                })

            group = Group(
                name=request.POST['name'],
                filter=request.POST['filter'],
                description=request.POST['desc'],
                rule=rules,
            )
            group.save()

            messages.success(request, "New group has been created successfully!")
        except KeyError as e:
            messages.error(request, f"Missing parameter: {str(e)}")
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def AdminViewGroupDetails(request, code):
    group = Group.objects.filter(unique_code=code).first()
    if not group:
        messages.error(request, "Group not found.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    context = {
        'group': group
    }
    return render(request, 'work/group-view.html', context)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def AdminUpdateGroupDetails(request):
    try:
        group = Group.objects.filter(unique_code=request.POST['group']).first()
        if not group:
            messages.error(request, "Group not found.")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        # Update group details if provided
        if 'name' in request.POST and request.POST['name'] and request.POST['name'] != group.name:
            finds = Company.objects.filter(group=group.name).get()

            if finds:
                for com in finds:
                    com.group = request.POST['name']
                Company.objects.bulk_update(finds, ['group'])

            group.name = request.POST['name']
        if 'filter' in request.POST and request.POST['filter'] and request.POST['filter'] != group.filter:
            group.filter = request.POST['filter']
        if 'desc' in request.POST and request.POST['desc'] and request.POST['desc'] != group.description:
            group.description = request.POST['desc']
        if 'status' in request.POST and request.POST['status'] and request.POST['status'] != group.status:
            group.status = request.POST['status']

        # Update rules
        fields = request.POST.getlist('field[]', [])
        conditions = request.POST.getlist('condition[]', [])
        values = request.POST.getlist('value[]', [])
        logics = request.POST.getlist('logic[]', [])

        if fields and conditions and values and logics:
            rules = [
                {'field': fields[i], 'condition': conditions[i], 'value': values[i], 'logic': logics[i]}
                for i in range(len(fields))
            ]
            group.rule = rules
        group.save()

        messages.success(request, "Group details updated successfully!")
    except KeyError as e:
        messages.error(request, f"Missing parameter: {str(e)}")
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def AdminGroupCompanies(request, code):
    group = Group.objects.filter(unique_code=code).first()
    if not group:
        messages.error(request, "Group not found.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    
    groupcompanies = Company.objects.filter(group=group.name).all()
    
    companies = []
    for company in groupcompanies:
        if(User.objects.filter(admin=company.admin).exists()):
            count = User.objects.filter(admin=company.admin).count()
            companies.append({
                'name': company.name,
                'email': company.email,
                'mobile': company.mobile,
                'unique_code': company.unique_code,
                'users': count,
                'status': company.status,
            })
        else:
            companies.append({
                'name': company.name,
                'email': company.email,
                'mobile': company.mobile,
                'unique_code': company.unique_code,
                'users': 0,
                'status': company.status,
            })

    allcompanies = Company.objects.all()

    context = {
        'group': group,
        'companies': companies,
        'allcompanies': allcompanies
    }
    return render(request, 'work/group-company.html', context)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def AdminCompanyInGroup(request):
    try:
        group = Group.objects.filter(unique_code=request.POST.get('gid')).first()
        if not group:
            messages.error(request, "Group not found.")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        updated_count = 0
        companies = request.POST.get('company').split(",")

        for company in companies:
            company = Company.objects.filter(unique_code=company).first()

            if company:
                company.group = group.name
                company.save()
                updated_count += 1

        message = ""
        if updated_count <= 1:
            message = f"{updated_count} company added to the group '{group.name}' successfully!"
        else:
            message = f"{updated_count} companies added to the group '{group.name}' successfully!"

        messages.success(request, message)
    except KeyError as e:
        messages.error(request, f"Missing parameter: {str(e)}")
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def AdminDeleteCompanyFromGroup(request):
    try:
        group = Group.objects.filter(unique_code=request.POST['gid']).first()
        if not group:
            messages.error(request, "Group not found.")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        company = Company.objects.filter(id=request.POST['company']).first()
        company.group = 'Unknown'
        company.save()

        messages.success(request, "Company from group deleted successfully!")
        
    except KeyError as e:
        messages.error(request, f"Missing parameter: {str(e)}")
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def AdminDeleteGroup(request):
    try:
        group = Group.objects.filter(id=request.POST['dgid']).first()
        if not group:
            messages.error(request, "Group not found.")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        
        companies = Company.objects.filter(group=group.name).all()
        for company in companies:
            tmp = Company.objects.filter(id=company.id).first()
            tmp.group = 'Unknown'
            tmp.save()

        group.delete()
        messages.success(request, "Group deleted successfully!")
    except KeyError as e:
        messages.error(request, f"Missing parameter: {str(e)}")
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def AdminAllWebsite(request):
    websites = Website.objects.all()
    
    context = {
        'websites': websites,
    }
    return render(request, 'work/websites.html', context)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def AdminAddNewWebsite(request):
    if request.method == 'POST':
        try:
            website = Website(
                domain = request.POST['domain'],
            )
            website.save()

            messages.success(request, "New website has been added successfully!")
        except KeyError as e:
            messages.error(request, f"Missing parameter: {str(e)}")
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def AdminFetchWebsite(request):
    website = Website.objects.filter(unique_code=request.POST.get('wid')).first()

    serialized = WebsiteSerializer(website)

    return Response({
        "status": HTTP_200_OK,
        "data": serialized.data
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def AdminUpdateWebsite(request):
    try:
        website = Website.objects.filter(unique_code=request.POST.get('wid')).first()
        if not website:
            messages.error(request, "Website not found.")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        # update website details if provided
        if 'domain' in request.POST and request.POST['domain'] and request.POST['domain'] != website.domain:
            website.domain = request.POST['domain']
        if 'status' in request.POST and request.POST['status'] and request.POST['status'] != website.status:
            website.status = request.POST['status']
        
        website.save()

        messages.success(request, "Website details updated successfully!")
    except KeyError as e:
        messages.error(request, f"Missing parameter: {str(e)}")
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def AdminDeleteWebsite(request):
    try:
        website = Website.objects.filter(id=request.POST.get('dwid')).first()
        if not website:
            messages.error(request, "Website not found.")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        website.delete()

        messages.success(request, "Website deleted successfully!")
    except KeyError as e:
        messages.error(request, f"Missing parameter: {str(e)}")
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def AdminSecuritySettings(request):
    return render(request, 'work/security-settings.html')

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def AdminUpdatePassword(request):
    try:
        account = User.objects.filter(unique_code=request.user.unique_code).first()
        if not account:
            messages.error(request, "User not found.")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        account.password = make_password(request.POST['password'])
        account.is_online = False
        account.save()

        request.user.auth_token.delete()
        request.session.flush()
        logout(request)
        messages.error(request, "Your account password changed successfully!" )
        return redirect(SignIn)
    except KeyError as e:
        messages.error(request, f"Missing parameter: {str(e)}")
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))  

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def AdminEnableOtp(request):
    try:
        account = User.objects.filter(unique_code=request.user.unique_code).first()
        if not account:
            messages.error(request, "User not found.")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        account.otp_enabled = 'Enabled'
        account.save()
        
        messages.error(request, "OTP authentication enabled successfully!" )
        return redirect(SignIn)
    except KeyError as e:
        messages.error(request, f"Missing parameter: {str(e)}")
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))  

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def AdminDisableOtp(request):
    try:
        account = User.objects.filter(unique_code=request.user.unique_code).first()
        if not account:
            messages.error(request, "User not found.")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        account.otp_enabled = 'Disabled'
        account.save()
        
        messages.error(request, "OTP authentication enabled successfully!" )
        return redirect(SignIn)
    except KeyError as e:
        messages.error(request, f"Missing parameter: {str(e)}")
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def SignOut(request):
    acc = User.objects.filter(unique_code = request.user.unique_code)
    acc.is_online = False
    acc.update()

    request.user.auth_token.delete()
    request.session.flush()
    logout(request)
    return redirect(SignIn)