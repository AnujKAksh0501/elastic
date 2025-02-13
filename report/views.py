from datetime import datetime
from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
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
from django.http import JsonResponse
import requests, pprint, json

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def AdminMatomoVisitCountriesList(request):
    auth_token = settings.MATOMO_API_TOKEN
    murl = settings.MATOMO_URL
    
    payload = {
        "module": "API",
        "method": "Events.getCategory",
        "idSite": settings.MATOMO_SITE_ID,
        "token_auth": auth_token,
        'period': 'day',
        'date': 'today',
        "format": "json",
        "filter_pattern": "Form",
    }
    response = requests.post(murl, data=payload)
    data = response.json()
    
    dlist = []
    for event in data:
        params = {
            "module": "API",
            "method": "Events.getNameFromCategoryId",
            "idSite": settings.MATOMO_SITE_ID,
            "token_auth": auth_token,
            "idSubtable": event.get("idsubdatatable"),
            "period": "day",
            "date": "today",
            "format": "json",
        }
        response = requests.post(murl, data={**params, "token_auth": auth_token})
        temp = response.json()
        for tmp in temp:
            dlist.append(json.loads(tmp["label"]))

    context = {
        'data': dlist
    }
    return render(request, 'work/matomo/visit-countries-list.html', context)
