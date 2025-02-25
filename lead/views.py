from django.http import HttpResponseRedirect
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.core.mail import send_mail, EmailMultiAlternatives
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
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
def AdminAllLeads(request):
    leads = Lead.objects.all().order_by('-created_at') # Order by most recent
    groups = Group.objects.all()

    paginator = Paginator(leads, 15)  # Show 15 leads per page
    page_number = request.GET.get('page')  # Get page number from URL
    page_obj = paginator.get_page(page_number)  # Get the correct page
        
    context = {
        'leads' : page_obj,
        'groups': groups
    }
    return render(request, 'work/leads/leads.html', context)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def AdminNormalLeads(request):
    leads = Lead.objects.filter(is_premium='No').order_by('-created_at') # Order by most recent
    groups = Group.objects.exclude(name='Premium').all()

    paginator = Paginator(leads, 15)  # Show 15 leads per page
    page_number = request.GET.get('page')  # Get page number from URL
    page_obj = paginator.get_page(page_number)  # Get the correct page
        
    context = {
        'leads' : page_obj,
        'groups': groups
    }
    return render(request, 'work/leads/leads-normal.html', context)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def AdminPremiumLeads(request):
    leads = Lead.objects.filter(is_premium='Yes').order_by('-created_at') # Order by most recent

    paginator = Paginator(leads, 15)  # Show 15 leads per page
    page_number = request.GET.get('page')  # Get page number from URL
    page_obj = paginator.get_page(page_number)  # Get the correct page
        
    context = {
        'leads' : page_obj
    }
    return render(request, 'work/leads/leads-premium.html', context)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def AdminCreateLead(request):
    if request.method == 'GET':
        websites = Website.objects.all()

        context = {
            'websites': websites
        }
        return render(request, 'work/leads/lead-create.html', context)
    elif request.method == 'POST':
        try:
            lead = Lead(
                name = request.POST['name'],
                email = request.POST['email'],
                mobile = request.POST['mobile'],
                part = request.POST['part'],
                make = request.POST['make'],
                model = request.POST['model'],
                year = request.POST['year'],
                size = request.POST['size'],
                source = request.POST['source'],
                type = request.POST['type'],
                is_premium = request.POST['premium'],
                status = request.POST['status'],
            )
            lead.save()
            
            messages.success(request, "New lead created successfully!")
        except KeyError as e:
            messages.error(request, f"Missing parameter: {str(e)}")
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
        
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def AdminViewLeadDetails(request, code):
    lead = Lead.objects.filter(unique_code=code).first()
    websites = Website.objects.all()
    if not lead:
        messages.error(request, "Lead not found.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    
    context = {
        'websites': websites,
        'lead': lead
    }
    return render(request, 'work/leads/lead-view.html', context)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def AdminSingleLeadEmail(request):
    if request.method == 'POST':
        try:
            lead = Lead.objects.filter(unique_code=request.POST.get('lid')).first()

            data = {
                "name": lead.name,
                "phone": lead.phone,
                "email": lead.email,
                "part": lead.part,
                "make": lead.make,
                "model": lead.model,
                "year": lead.year,
                "size": lead.size,
            }

            email_subject = f"Lead from {lead.phone}"
            email_body = render_to_string('emails/lead-email.html', {'data': data})

            companies = Company.objects.filter(group=request.POST.get('group')).all()
            emails = User.objects.filter(admin__company__in=companies).values_list('email', flat=True)

            if not emails:
                messages.error(request, "No recipients found.")
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            
            sent_logs = []
            for email in emails:
                # Send the email
                send_mail(
                    subject=email_subject,
                    message="",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    html_message=email_body,
                )

                # Prepare email log
                sent_logs.append(Sent(
                    lead_id=request.POST.get('lid'),
                    to_email=email,
                    phone=lead.phone,
                    date=lead.created_at.date(),
                    time=lead.created_at.time()
                ))

            # Bulk save email logs
            Sent.objects.bulk_create(sent_logs)

            messages.success(request, "Lead sent successfully!")
        except KeyError as e:
            messages.error(request, f"Missing parameter: {str(e)}")
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
        
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def AdminFetchEmailTransactions(request):
    try:
        lead = Lead.objects.filter(unique_code=request.POST.get('lid')).first()
        trans = Sent.objects.filter(lead_id=lead.unique_code).get()

        data = {}
        n = 0
        for tmp in trans:
            account = User.objects.filter(email=tmp.to_email).first()
            company = Company.objects.filter(admin=account.admin).first()

            temp = {
                'date': tmp.date,
                'time': tmp.date,
                'phone': tmp.phone,
                'email': tmp.to_email,
                'group': company.group,
                'status': tmp.status,
            }
            n = n + 1
            data[n] = temp
            temp = {}

        return Response({
            "status": HTTP_200_OK,
            "data": data,
        })
    except ObjectDoesNotExist:
        return Response({
            "status": HTTP_404_NOT_FOUND,
            "message": "No data found.",
        })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def AdminUpdateLeadDetails(request):
    try:
        if not request.POST.get('lead'):
            messages.error(request, "Lead ID is required.")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        
        lead = Lead.objects.filter(unique_code=request.POST.get('lead')).first()
        if not lead:
            messages.error(request, "Lead not found.")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        
        # Fields allowed to be updated
        updatable_fields = ['source', 'type', 'is_premium', 'status', 'name', 'email', 'phone', 'part', 'make', 'model', 'year', 'size']
        updated = False  # Flag to check if anything was updated

        for field in updatable_fields:
            new_value = request.POST.get(field)
            if new_value and new_value != getattr(lead, field):
                setattr(lead, field, new_value)
                updated = True
            
        if updated:
            lead.save()

            messages.success(request, "Lead details updated successfully!")
        else:
            messages.info(request, "No changes detected!")
    except KeyError as e:
        messages.error(request, f"Missing parameter: {str(e)}")
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def AdminDeleteLead(request):
    try:
        if not request.POST['dlid']:
            messages.error(request, "Lead ID is required.")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        lead = Lead.objects.filter(unique_code=request.POST['dlid']).first()

        if not lead:
            messages.error(request, "Lead not found.")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        
        lead.delete()

        messages.success(request, "Lead deleted successfully!")
    except KeyError as e:
        messages.error(request, f"Missing parameter: {str(e)}")
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def AdminAllContacts(request):
    contacts = Contact.objects.all().order_by('-created_at')

    paginator = Paginator(contacts, 15)  # Show 15 leads per page
    page_number = request.GET.get('page')  # Get page number from URL
    page_obj = paginator.get_page(page_number)  # Get the correct page
        
    context = {
        'contacts' : page_obj
    }
    return render(request, 'work/contacts.html', context)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def AdminCreateContact(request):
    if request.method == 'GET':
        countries = Country.objects.all()

        context = {
            'countries': countries
        }
        return render(request, 'work/contact-create.html', context)
    elif request.method == 'POST':
        try:
            contact = Contact(
                name = request.POST['name'],
                email = request.POST['email'],
                mobile = request.POST['mobile'],
                part = request.POST['address'],
                make = request.POST['country'],
                model = request.POST['state'],
                year = request.POST['city'],
                size = request.POST['zip']
            )
            contact.save()
            cid = contact.id

            if cid:
                messages.success(request, "New contact created successfully!")
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            else:
                messages.error(request, "Something went wrong!")
        except KeyError as e:
            messages.error(request, f"Missing parameter: {str(e)}")
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def AdminViewContactDetails(request, code):
    countries = Country.objects.all()
    contact = Contact.objects.filter(unique_code=code).first()

    if not contact:
        messages.error(request, "Contact not found.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    context = {
        'countries': countries,
        'contact': contact
    }    
    return render(request, 'work/contact-view.html', context)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def AdminUpdateContactDetails(request):
    try:
        if not request.POST['contact']:
            messages.error(request, "Contact ID is required.")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        
        contact = Contact.objects.filter(unique_code=request.POST['contact']).first()
        if not contact:
            messages.error(request, "Contact not found.")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        if request.POST['name'] != '' and request.POST['name'] != contact.name:
            contact.name = request.POST['name']
        if request.POST['email'] != '' and request.POST['email'] != contact.email:
            contact.email = request.POST['email']
        if request.POST['mobile'] != '' and request.POST['mobile'] != contact.mobile:
            contact.mobile = request.POST['mobile']
        if request.POST['address'] != '' and request.POST['address'] != contact.address:
            contact.address = request.POST['address']
        if request.POST['city'] != '' and request.POST['city'] != contact.city:
            contact.city = request.POST['city']
        if request.POST['state'] != '' and request.POST['state'] != contact.state:
            contact.state = request.POST['state']
        if request.POST['country'] != '' and request.POST['country'] != contact.country:
            contact.country = request.POST['country']
        if request.POST['zip'] != '' and request.POST['zip'] != contact.zip:
            contact.zip = request.POST['zip']
        if request.POST['status'] != '' and request.POST['status'] != contact.status:
            contact.status = request.POST['status']

        contact.save()

        messages.success(request, "Contact details updated successfully!")
    except KeyError as e:
        messages.error(request, f"Missing parameter: {str(e)}")
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def AdminDeleteContact(request):
    try:
        if not request.POST['dcid']:
            messages.error(request, "Contact ID is required.")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        
        contact = Contact.objects.filter(unique_code=request.POST['dcid']).first()
        if not contact:
            messages.error(request, "Contact not found.")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        
        contact.delete()

        messages.success(request, "Contact deleted successfully!")
    except KeyError as e:
        messages.error(request, f"Missing parameter: {str(e)}")
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

