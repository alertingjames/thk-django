# import datetime
from datetime import date
from datetime import timedelta
import difflib
import os
import string
import urllib
from itertools import islice

import io
import requests
import xlrd
import re

from django.core import mail
from django.core.mail import send_mail, BadHeaderError, EmailMessage
from django.contrib import messages
# from _mysql_exceptions import DataError, IntegrityError
from django.template import RequestContext

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.core.mail import EmailMultiAlternatives

from django.core.files.storage import FileSystemStorage
import json
from django.contrib import auth
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect, HttpResponseNotAllowed
from django.utils.datastructures import MultiValueDictKeyError
from django.views.decorators.cache import cache_control
from numpy import long
from openpyxl.styles import PatternFill

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.fields import empty
from rest_framework.permissions import AllowAny
from time import gmtime, strftime
import time
from xlrd import XLRDError

from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User, AnonymousUser
from django.conf import settings
from django import forms
import sys
from django.core.cache import cache
import random

from rigschedule.models import Member, Rig, Well, Version
from rigschedule.serializers import RigSerializer, WellSerializer

today = date.today()



######################################################################################### Admin ###########################################################################################################################
######################################################################################### Admin ###########################################################################################################################
######################################################################################### Admin ###########################################################################################################################


def admin_loginpage(request):
    return render(request, 'rigschedule/admin_login.html')


def admin_forgotpasswordpage(request):
    return render(request, 'rigschedule/admin_forgotpassword.html')


@api_view(['GET', 'POST'])
def admin_login(request):
    if request.method == 'POST':
        email = request.POST.get('email', '')
        password = request.POST.get('password', '')

        members = Member.objects.filter(email=email, password=password, role='admin')
        if members.count() > 0:
            member = members[0]
            request.session['adminidx'] = member.pk
            return HttpResponse('0')
        else:
            members = Member.objects.filter(email=email, role='admin')
            if members.count() > 0 :
                return HttpResponse('1')
            return HttpResponse('2')



@api_view(['GET', 'POST'])
def admin_forgotpassword(request):
    if request.method == 'POST':
        email = request.POST.get('email', '')

        members = Member.objects.filter(email=email, role='admin')
        if members.count() == 0:
            return HttpResponse('1')

        member = members[0]

        message = 'You are allowed to reset your password from your request.<br>For it, please click this link to reset your password.<br><br><a href=\'' + settings.URL + '/rigschedule/atoresetpassword?u=' + str(member.pk)
        message = message + '\' target=\'_blank\'>' + 'Link to reset password' + '</a>'

        html =  """\
                    <html>
                        <head></head>
                        <body>
                            <a href="#"><img src="https://hafizkurnia.pythonanywhere.com/static/images/rig_logo.jpg" style="width:120px; height:120px; border-radius:10px; margin-left:25px;"/></a>
                            <h2 style="color:#02839a;">Rig Schedule Administrator's Security Information Update</h2>
                            <div style="font-size:14px; word-break: break-all; word-wrap: break-word;">
                                {mes}
                            </div>
                        </body>
                    </html>
                """
        html = html.format(mes=message)

        fromEmail = 'hafiz.kurnia92@gmail.com'
        toEmailList = []
        toEmailList.append(email)
        msg = EmailMultiAlternatives('We allowed you to reset your password', '', fromEmail, toEmailList)
        msg.attach_alternative(html, "text/html")
        msg.send(fail_silently=False)

        return HttpResponse('0')



def admin_home(request):
    try:
        if request.session['adminidx'] == 0 or request.session['adminidx'] == '':
            return render(request, 'rigschedule/admin_login.html')
    except KeyError:
        print('no key')
        return render(request, 'rigschedule/admin_login.html')

    adminidx = request.session['adminidx']

    rigs = Rig.objects.filter(member_id=adminidx).order_by('-id')
    wellList = []
    for rig in rigs:
        wells = Well.objects.filter(rig_id=rig.pk).order_by('-id')
        processWellDates(wells)
        data = {
            'rig':rig,
            'wells':wells
        }
        wellList.append(data)

    last_version = None
    versions = Version.objects.filter(member_id=adminidx)
    if versions.count() > 0: last_version = versions.last()

    licenseList = []
    fieldList = []
    wells = Well.objects.all().order_by('-id')
    for well in wells:
        if not well.license in licenseList and well.license != '':
            licenseList.append(well.license)
        if not well.field in fieldList and well.field != '':
            fieldList.append(well.field)

    return render(request, 'rigschedule/admin_home.html', {'rigs':rigs, 'wells':wellList, 'last_version':last_version, 'fields':fieldList, 'licenses':licenseList})



def admin_resetpasswordpage(request):
    member_id = request.GET['u']
    member = Member.objects.get(id=member_id)
    return render(request, 'rigschedule/admin_resetpwd.html', {'email':member.email})



@api_view(['GET', 'POST'])
def admin_resetpassword(request):
    if request.method == 'POST':
        email = request.POST.get('email', '')
        password = request.POST.get('password', '')

        members = Member.objects.filter(email=email, role='admin')
        if members.count() == 0:
            return HttpResponse('1')

        member = members[0]
        member.password = password
        member.save()

        return HttpResponse('0')


def admin_logout(request):
    request.session['adminidx'] = 0
    return redirect('/rigschedule/admin')


@api_view(['POST', 'GET'])
def admin_uploadnewrig(request):
    import calendar
    try:
        if request.session['adminidx'] == 0 or request.session['adminidx'] == '':
            return render(request, 'rigschedule/admin_login.html')
    except KeyError:
        print('no key')
        return render(request, 'rigschedule/admin_login.html')

    adminidx = request.session['adminidx']

    if request.method == 'POST':
        rig_name = request.POST.get('rig_name', '')
        rig_type = request.POST.get('rig_type', '')
        pressure_rating = request.POST.get('pressure_rating', '')
        specification = request.POST.get('specification', '')
        contract_period = request.POST.get('contract_period', '')
        summary = request.POST.get('summary', '')
        comment = request.POST.get('comment', '')

        rigs = Rig.objects.filter(name=rig_name)
        if rigs.count() > 0:
            return render(request, 'rigschedule/result.html', {'response':'The rig name already is being used. Please rename the rig.'})
        rig = Rig()
        rig.member_id = adminidx
        rig.name = rig_name
        rig.type = rig_type
        rig.pressure_rating = pressure_rating
        rig.specification = specification
        rig.contract_period = contract_period
        rig.summary = summary
        rig.comment = comment
        rig.created_date = today.strftime("%Y-%m-%d")
        rig.save()

        rigs = Rig.objects.filter(member_id=adminidx).order_by('-id')
        wellList = []
        for rig in rigs:
            wells = Well.objects.filter(rig_id=rig.pk).order_by('-id')
            processWellDates(wells)
            data = {
                'rig':rig,
                'wells':wells
            }
            wellList.append(data)

        last_version = None
        versions = Version.objects.filter(member_id=adminidx)
        if versions.count() > 0: last_version = versions.last()

        licenseList = []
        fieldList = []
        wells = Well.objects.all().order_by('-id')
        for well in wells:
            if not well.license in licenseList and well.license != '':
                licenseList.append(well.license)
            if not well.field in fieldList and well.field != '':
                fieldList.append(well.field)

        return render(request, 'rigschedule/admin_home.html', {'rigs':rigs, 'wells':wellList, 'last_version':last_version, 'fields':fieldList, 'licenses':licenseList})

    else:
        return redirect('/rigschedule/ahome')


@api_view(['POST', 'GET'])
def admin_newwell(request):
    import datetime
    try:
        if request.session['adminidx'] == 0 or request.session['adminidx'] == '':
            return render(request, 'rigschedule/admin_login.html')
    except KeyError:
        print('no key')
        return render(request, 'rigschedule/admin_login.html')

    adminidx = request.session['adminidx']

    if request.method == 'POST':
        rig_id = request.POST.get('rig_id', '1')
        well_name = request.POST.get('well_name', '')
        p10_start_date = request.POST.get('p10_start_date', '')
        p50_start_date = request.POST.get('p50_start_date', '')
        p90_start_date = request.POST.get('p90_start_date', '')
        p10_days_operation = request.POST.get('p10_days_operation', '')
        p50_days_operation = request.POST.get('p50_days_operation', '')
        p90_days_operation = request.POST.get('p90_days_operation', '')
        p10_status = request.POST.get('p10_status', '')
        p50_status = request.POST.get('p50_status', '')
        p90_status = request.POST.get('p90_status', '')
        license = request.POST.get('license', '')
        field = request.POST.get('field', '')
        well_type = request.POST.get('well_type', '')
        well_status = request.POST.get('well_status', '')
        info = request.POST.get('info', '')

        well = Well()
        well.rig_id = rig_id
        well.name = well_name
        well.p10_start_date = p10_start_date
        well.p50_start_date = p50_start_date
        well.p90_start_date = p90_start_date
        well.p10_days_operation = p10_days_operation
        well.p50_days_operation = p50_days_operation
        well.p90_days_operation = p90_days_operation
        well.p10_status = p10_status
        well.p50_status = p50_status
        well.p90_status = p90_status

        dt10 = datetime.datetime(year=int(p10_start_date.split('-')[0]), month=int(p10_start_date.split('-')[1]), day=int(p10_start_date.split('-')[2]))
        p10_end_date = (dt10 + timedelta(days=int(p10_days_operation))).strftime("%Y-%m-%d")

        dt50 = datetime.datetime(year=int(p50_start_date.split('-')[0]), month=int(p50_start_date.split('-')[1]), day=int(p50_start_date.split('-')[2]))
        p50_end_date = (dt50 + timedelta(days=int(p50_days_operation))).strftime("%Y-%m-%d")

        dt90 = datetime.datetime(year=int(p90_start_date.split('-')[0]), month=int(p90_start_date.split('-')[1]), day=int(p90_start_date.split('-')[2]))
        p90_end_date = (dt90 + timedelta(days=int(p90_days_operation))).strftime("%Y-%m-%d")

        well.p10_end_date = p10_end_date
        well.p50_end_date = p50_end_date
        well.p90_end_date = p90_end_date

        well.license = license
        well.field = field
        well.well_type = well_type
        well.well_status = well_status
        well.info = info

        well.save()

        rigs = Rig.objects.filter(member_id=adminidx).order_by('-id')
        wellList = []
        for rig in rigs:
            wells = Well.objects.filter(rig_id=rig.pk).order_by('-id')
            processWellDates(wells)
            data = {
                'rig':rig,
                'wells':wells
            }
            wellList.append(data)

        last_version = None
        versions = Version.objects.filter(member_id=adminidx)
        if versions.count() > 0: last_version = versions.last()

        licenseList = []
        fieldList = []
        wells = Well.objects.all().order_by('-id')
        for well in wells:
            if not well.license in licenseList and well.license != '':
                licenseList.append(well.license)
            if not well.field in fieldList and well.field != '':
                fieldList.append(well.field)

        return render(request, 'rigschedule/admin_home.html', {'rigs':rigs, 'wells':wellList, 'rig_id':rig_id, 'well_id':well.pk, 'last_version':last_version, 'fields':fieldList, 'licenses':licenseList})

    else:
        return redirect('/rigschedule/ahome')


def processWellDates(wells):
    for well in wells:
        if well.p10_start_date != '':
            well.p10_start_date = convertDate(well.p10_start_date)
        if well.p50_start_date != '':
            well.p50_start_date = convertDate(well.p50_start_date)
        if well.p90_start_date != '':
            well.p90_start_date = convertDate(well.p90_start_date)


def convertDate(datestr):
    import datetime
    year = int(datestr.split('-')[0])
    month = int(datestr.split('-')[1])
    day = int(datestr.split('-')[2])
    date = datetime.datetime(year, month, day)
    return date.strftime("%d %B %Y")


@api_view(['POST', 'GET'])
def admin_updaterig(request):
    import calendar
    try:
        if request.session['adminidx'] == 0 or request.session['adminidx'] == '':
            return render(request, 'rigschedule/admin_login.html')
    except KeyError:
        print('no key')
        return render(request, 'rigschedule/admin_login.html')

    adminidx = request.session['adminidx']

    if request.method == 'POST':
        rig_id = request.POST.get('rig_id', '1')
        rig_name = request.POST.get('rig_name', '')
        rig_type = request.POST.get('rig_type', '')
        pressure_rating = request.POST.get('pressure_rating', '')
        specification = request.POST.get('specification', '')
        contract_period = request.POST.get('contract_period', '')
        summary = request.POST.get('summary', '')
        comment = request.POST.get('comment', '')

        rigs = Rig.objects.filter(id=rig_id)
        if rigs.count() == 0:
            return redirect('/rigschedule/ahome')
        rig = rigs[0]
        rig.name = rig_name
        rig.type = rig_type
        rig.pressure_rating = pressure_rating
        rig.specification = specification
        rig.contract_period = contract_period
        rig.summary = summary
        rig.comment = comment
        rig.save()

        rigs = Rig.objects.filter(member_id=adminidx).order_by('-id')
        wellList = []
        for rig in rigs:
            wells = Well.objects.filter(rig_id=rig.pk).order_by('-id')
            processWellDates(wells)
            data = {
                'rig':rig,
                'wells':wells
            }
            wellList.append(data)

        last_version = None
        versions = Version.objects.filter(member_id=adminidx)
        if versions.count() > 0: last_version = versions.last()

        return render(request, 'rigschedule/admin_home.html', {'rigs':rigs, 'wells':wellList, 'rig_id':rig_id, 'last_version':last_version})

    else:
        return redirect('/rigschedule/ahome')



def admin_deleterig(request):
    rig_id = request.GET['rig_id']
    wells = Well.objects.filter(rig_id=rig_id)
    wells.delete()
    Rig.objects.filter(id=rig_id).delete()
    return redirect('/rigschedule/ahome')


@api_view(['POST', 'GET'])
def admin_wellupdate(request):
    import datetime
    try:
        if request.session['adminidx'] == 0 or request.session['adminidx'] == '':
            return render(request, 'rigschedule/admin_login.html')
    except KeyError:
        print('no key')
        return render(request, 'rigschedule/admin_login.html')

    adminidx = request.session['adminidx']

    if request.method == 'POST':
        well_id = request.POST.get('well_id', '1')
        well_name = request.POST.get('well_name', '')
        p10_start_date = request.POST.get('p10_start_date', '')
        p50_start_date = request.POST.get('p50_start_date', '')
        p90_start_date = request.POST.get('p90_start_date', '')
        p10_days_operation = request.POST.get('p10_days_operation', '')
        p50_days_operation = request.POST.get('p50_days_operation', '')
        p90_days_operation = request.POST.get('p90_days_operation', '')
        p10_status = request.POST.get('p10_status', '')
        p50_status = request.POST.get('p50_status', '')
        p90_status = request.POST.get('p90_status', '')
        license = request.POST.get('license', '')
        field = request.POST.get('field', '')
        well_type = request.POST.get('well_type', '')
        well_status = request.POST.get('well_status', '')
        info = request.POST.get('info', '')

        wells = Well.objects.filter(id=well_id)
        if wells.count() == 0:
            return redirect('/rigschedule/ahome')
        well = wells[0]
        well.name = well_name
        well.p10_start_date = p10_start_date
        well.p50_start_date = p50_start_date
        well.p90_start_date = p90_start_date
        well.p10_days_operation = p10_days_operation
        well.p50_days_operation = p50_days_operation
        well.p90_days_operation = p90_days_operation
        well.p10_status = p10_status
        well.p50_status = p50_status
        well.p90_status = p90_status

        dt10 = datetime.datetime(year=int(p10_start_date.split('-')[0]), month=int(p10_start_date.split('-')[1]), day=int(p10_start_date.split('-')[2]))
        p10_end_date = (dt10 + timedelta(days=int(p10_days_operation))).strftime("%Y-%m-%d")

        dt50 = datetime.datetime(year=int(p50_start_date.split('-')[0]), month=int(p50_start_date.split('-')[1]), day=int(p50_start_date.split('-')[2]))
        p50_end_date = (dt50 + timedelta(days=int(p50_days_operation))).strftime("%Y-%m-%d")

        dt90 = datetime.datetime(year=int(p90_start_date.split('-')[0]), month=int(p90_start_date.split('-')[1]), day=int(p90_start_date.split('-')[2]))
        p90_end_date = (dt90 + timedelta(days=int(p90_days_operation))).strftime("%Y-%m-%d")

        well.p10_end_date = p10_end_date
        well.p50_end_date = p50_end_date
        well.p90_end_date = p90_end_date

        well.license = license
        well.field = field
        well.well_type = well_type
        well.well_status = well_status
        well.info = info

        well.save()

        rigs = Rig.objects.filter(member_id=adminidx).order_by('-id')
        wellList = []
        for rig in rigs:
            wells = Well.objects.filter(rig_id=rig.pk).order_by('-id')
            processWellDates(wells)
            data = {
                'rig':rig,
                'wells':wells
            }
            wellList.append(data)

        last_version = None
        versions = Version.objects.filter(member_id=adminidx)
        if versions.count() > 0: last_version = versions.last()

        licenseList = []
        fieldList = []
        wells = Well.objects.all().order_by('-id')
        for well in wells:
            if not well.license in licenseList and well.license != '':
                licenseList.append(well.license)
            if not well.field in fieldList and well.field != '':
                fieldList.append(well.field)

        return render(request, 'rigschedule/admin_home.html', {'rigs':rigs, 'wells':wellList, 'rig_id':well.rig_id, 'well_id':well.pk, 'last_version':last_version, 'fields':fieldList, 'licenses':licenseList})

    else:
        return redirect('/rigschedule/ahome')



def admin_deletewell(request):
    try:
        if request.session['adminidx'] == 0 or request.session['adminidx'] == '':
            return render(request, 'rigschedule/admin_login.html')
    except KeyError:
        print('no key')
        return render(request, 'rigschedule/admin_login.html')

    adminidx = request.session['adminidx']

    rig_id = request.GET['rig_id']
    well_id = request.GET['well_id']
    wells = Well.objects.filter(id=well_id)
    wells.delete()

    rigs = Rig.objects.filter(member_id=adminidx).order_by('-id')
    wellList = []
    for rig in rigs:
        wells = Well.objects.filter(rig_id=rig.pk).order_by('-id')
        processWellDates(wells)
        data = {
            'rig':rig,
            'wells':wells
        }
        wellList.append(data)

    last_version = None
    versions = Version.objects.filter(member_id=adminidx)
    if versions.count() > 0: last_version = versions.last()

    return render(request, 'rigschedule/admin_home.html', {'rigs':rigs, 'wells':wellList, 'rig_id':rig_id, 'last_version':last_version})



def admin_users(request):
    try:
        if request.session['adminidx'] == 0 or request.session['adminidx'] == '':
            return render(request, 'rigschedule/admin_login.html')
    except KeyError:
        print('no key')
        return render(request, 'rigschedule/admin_login.html')

    adminidx = request.session['adminidx']

    users = Member.objects.filter(admin_id=adminidx, role='').order_by('-id')
    return render(request, 'rigschedule/admin_users.html', {'users':users})



def admin_deleteuser(request):
    try:
        if request.session['adminidx'] == 0 or request.session['adminidx'] == '':
            return render(request, 'rigschedule/admin_login.html')
    except KeyError:
        print('no key')
        return render(request, 'rigschedule/admin_login.html')

    adminidx = request.session['adminidx']

    user_id = request.GET['u_id']

    users = Member.objects.filter(id=user_id, admin_id=adminidx, role='')
    users.delete()
    return redirect('/rigschedule/ausers')



def admin_versions(request):
    try:
        if request.session['adminidx'] == 0 or request.session['adminidx'] == '':
            return render(request, 'rigschedule/admin_login.html')
    except KeyError:
        print('no key')
        return render(request, 'rigschedule/admin_login.html')

    adminidx = request.session['adminidx']

    versions = Version.objects.filter(member_id=adminidx)

    rigList = []
    wellList = []

    last_version = None
    if versions.count() > 0:
        last_version = versions.last()

        try:
            version_id = request.GET['version_id']
            vers = Version.objects.filter(id=version_id)
            if vers.count() > 0 :
                selected_version = vers.first()
                last_version = selected_version
        except KeyError:
            print('No key')

        data = last_version.data
        if data != '':
            try:
                decoded = json.loads(data)
                for data in decoded:
                    rig_data = data['rig']
                    rig = Rig()
                    rig.id = rig_data['id']
                    rig.member_id = rig_data['member_id']
                    rig.name = rig_data['name']
                    rig.type = rig_data['type']
                    rig.pressure_rating = rig_data['pressure_rating']
                    rig.specification = rig_data['specification']
                    rig.contract_period = rig_data['contract_period']
                    rig.summary = rig_data['summary']
                    rig.comment = rig_data['comment']
                    rig.created_date = rig_data['created_date']
                    rig.version_text = last_version.version_name

                    rigList.append(rig)

                    wells = []
                    well_data_list = data['wells']
                    for well_data in well_data_list:
                        well = Well()
                        well.id = well_data['id']
                        well.rig_id = well_data['rig_id']
                        well.name = well_data['name']

                        well.p10_start_date = well_data['p10_start_date']
                        well.p50_start_date = well_data['p50_start_date']
                        well.p90_start_date = well_data['p90_start_date']

                        well.p10_end_date = well_data['p10_end_date']
                        well.p50_end_date = well_data['p50_end_date']
                        well.p90_end_date = well_data['p90_end_date']

                        well.p10_status = well_data['p10_status']
                        well.p50_status = well_data['p50_status']
                        well.p90_status = well_data['p90_status']

                        well.p10_days_operation = well_data['p10_days_operation']
                        well.p50_days_operation = well_data['p50_days_operation']
                        well.p90_days_operation = well_data['p90_days_operation']

                        well.license = well_data['license']
                        well.field = well_data['field']
                        well.well_type = well_data['well_type']
                        well.well_status = well_data['well_status']
                        well.info = well_data['info']

                        wells.append(well)

                    processWellDates(wells)
                    data = {
                        'rig':rig,
                        'wells':wells
                    }
                    wellList.append(data)

                versions = versions.order_by('-id')

                return render(request, 'rigschedule/admin_versions.html', {'rigs':rigList, 'wells':wellList, 'versions':versions, 'last_version':last_version})

            except:
                print('Error')
                return render(request, 'rigschedule/result.html', {'response':'Error!'})

        versions = versions.order_by('-id')
        return render(request, 'rigschedule/admin_versions.html', {'rigs':[], 'wells':[], 'versions':versions, 'last_version':last_version})

    return render(request, 'rigschedule/admin_versions.html', {'rigs':[], 'wells':[], 'last_version':last_version})



@api_view(['POST', 'GET'])
def admin_saveversion(request):
    import calendar
    try:
        if request.session['adminidx'] == 0 or request.session['adminidx'] == '':
            return render(request, 'rigschedule/admin_login.html')
    except KeyError:
        print('no key')
        return render(request, 'rigschedule/admin_login.html')

    adminidx = request.session['adminidx']

    if request.method == 'POST':

        version_date = request.POST.get('version_date','')
        version_number = request.POST.get('version_number','1')

        rigs = Rig.objects.filter(member_id=adminidx).order_by('-id')
        dataList = []
        for rig in rigs:
            wells = Well.objects.filter(rig_id=rig.pk).order_by('-id')
            data = {
                'rig':RigSerializer(rig, many=False).data,
                'wells':WellSerializer(wells, many=True).data
            }
            dataList.append(data)

        rig.version = '1'
        datestr = version_date.split('-')
        year = datestr[0]
        month = str(int(datestr[1]))
        month_name = calendar.month_name[int(month)]

        versions = Version.objects.filter(member_id=adminidx, year=int(year), month=int(month))
        if versions.count() > 0:
            return HttpResponse('1')

        version = Version()
        version.member_id = adminidx
        version.year = year
        version.month = month
        # version.version = version_number
        version.version = '1'
        version.version_name = month_name + ' ' + year + ' Version 1'
        version.created_date = today.strftime("%Y-%m-%d")
        version.data = json.dumps(dataList)
        version.save()

        return HttpResponse('0')



@api_view(['POST', 'GET'])
def admin_version_updaterig(request):
    try:
        if request.session['adminidx'] == 0 or request.session['adminidx'] == '':
            return render(request, 'rigschedule/admin_login.html')
    except KeyError:
        print('no key')
        return render(request, 'rigschedule/admin_login.html')

    adminidx = request.session['adminidx']

    if request.method == 'POST':
        version_id = request.POST.get('version_id', '1')
        rig_id = request.POST.get('rig_id', '1')
        rig_name = request.POST.get('rig_name', '')
        rig_type = request.POST.get('rig_type', '')
        pressure_rating = request.POST.get('pressure_rating', '')
        specification = request.POST.get('specification', '')
        contract_period = request.POST.get('contract_period', '')
        summary = request.POST.get('summary', '')
        comment = request.POST.get('comment', '')

        rigList = []
        wellList = []
        dataList = []

        versions = Version.objects.filter(member_id=adminidx)

        vers = Version.objects.filter(id=version_id)
        selected_version = vers.first()

        data = selected_version.data
        if data != '':
            try:
                decoded = json.loads(data)
                for data in decoded:
                    rig_data = data['rig']

                    rig = None

                    if int(rig_id) == int(rig_data['id']):
                        rig = Rig()
                        rig.id = rig_id
                        rig.member_id = adminidx
                        rig.name = rig_name
                        rig.type = rig_type
                        rig.pressure_rating = pressure_rating
                        rig.specification = specification
                        rig.contract_period = contract_period
                        rig.summary = summary
                        rig.comment = comment
                        rig.created_date = rig_data['created_date']
                        rig.version_text = selected_version.version_name

                    else:
                        rig = Rig()
                        rig.id = rig_data['id']
                        rig.member_id = rig_data['member_id']
                        rig.name = rig_data['name']
                        rig.type = rig_data['type']
                        rig.pressure_rating = rig_data['pressure_rating']
                        rig.specification = rig_data['specification']
                        rig.contract_period = rig_data['contract_period']
                        rig.summary = rig_data['summary']
                        rig.comment = rig_data['comment']
                        rig.created_date = rig_data['created_date']
                        rig.version_text = selected_version.version_name

                    rigList.append(rig)

                    wells = []
                    well_data_list = data['wells']
                    for well_data in well_data_list:

                        well = Well()
                        well.id = well_data['id']
                        well.rig_id = well_data['rig_id']
                        well.name = well_data['name']
                        well.p10_days_operation = well_data['p10_days_operation']
                        well.p50_days_operation = well_data['p50_days_operation']
                        well.p90_days_operation = well_data['p90_days_operation']
                        well.license = well_data['license']
                        well.field = well_data['field']
                        well.well_type = well_data['well_type']
                        well.well_status = well_data['well_status']
                        well.start_date = well_data['start_date']
                        well.end_date = well_data['end_date']
                        well.spud_date = well_data['spud_date']
                        well.info = well_data['info']
                        well.comment = well_data['comment']
                        well.startup_constraint = well_data['startup_constraint']

                        wells.append(well)

                    processWellDates(wells)
                    data = {
                        'rig':rig,
                        'wells':wells
                    }
                    wellList.append(data)

                    data = {
                        'rig':RigSerializer(rig, many=False).data,
                        'wells':WellSerializer(wells, many=True).data
                    }
                    dataList.append(data)

                selected_version.data = json.dumps(dataList)
                selected_version.save()

                versions = versions.order_by('-id')

                return render(request, 'rigschedule/admin_versions.html', {'rigs':rigList, 'wells':wellList, 'versions':versions, 'last_version':selected_version, 'rig_id':rig_id})

            except:
                print('Error')
                return render(request, 'rigschedule/result.html', {'response':'Error!'})

        return redirect('/rigschedule/aversions')

    else:
        return redirect('/rigschedule/aversions')




def admin_version_deleterig(request):
    try:
        if request.session['adminidx'] == 0 or request.session['adminidx'] == '':
            return render(request, 'rigschedule/admin_login.html')
    except KeyError:
        print('no key')
        return render(request, 'rigschedule/admin_login.html')

    adminidx = request.session['adminidx']

    version_id = request.GET['version_id']
    rig_id = request.GET['rig_id']

    rigList = []
    wellList = []
    dataList = []

    versions = Version.objects.filter(member_id=adminidx)

    vers = Version.objects.filter(id=version_id)
    selected_version = vers.first()

    data = selected_version.data
    if data != '':
        try:
            decoded = json.loads(data)
            for data in decoded:
                rig_data = data['rig']

                if int(rig_id) == int(rig_data['id']):
                    continue

                rig = Rig()
                rig.id = rig_data['id']
                rig.member_id = rig_data['member_id']
                rig.name = rig_data['name']
                rig.type = rig_data['type']
                rig.pressure_rating = rig_data['pressure_rating']
                rig.specification = rig_data['specification']
                rig.contract_period = rig_data['contract_period']
                rig.summary = rig_data['summary']
                rig.comment = rig_data['comment']
                rig.created_date = rig_data['created_date']
                rig.version_text = selected_version.version_name


                rigList.append(rig)

                wells = []
                well_data_list = data['wells']
                for well_data in well_data_list:

                    well = Well()
                    well.id = well_data['id']
                    well.rig_id = well_data['rig_id']
                    well.name = well_data['name']

                    well.p10_start_date = well_data['p10_start_date']
                    well.p50_start_date = well_data['p50_start_date']
                    well.p90_start_date = well_data['p90_start_date']

                    well.p10_end_date = well_data['p10_end_date']
                    well.p50_end_date = well_data['p50_end_date']
                    well.p90_end_date = well_data['p90_end_date']

                    well.p10_status = well_data['p10_status']
                    well.p50_status = well_data['p50_status']
                    well.p90_status = well_data['p90_status']

                    well.p10_days_operation = well_data['p10_days_operation']
                    well.p50_days_operation = well_data['p50_days_operation']
                    well.p90_days_operation = well_data['p90_days_operation']

                    well.license = well_data['license']
                    well.field = well_data['field']
                    well.well_type = well_data['well_type']
                    well.well_status = well_data['well_status']
                    well.info = well_data['info']

                    wells.append(well)

                data = {
                    'rig':RigSerializer(rig, many=False).data,
                    'wells':WellSerializer(wells, many=True).data
                }
                dataList.append(data)

                processWellDates(wells)
                data = {
                    'rig':rig,
                    'wells':wells
                }
                wellList.append(data)

            selected_version.data = json.dumps(dataList)
            selected_version.save()

            versions = versions.order_by('-id')

            return render(request, 'rigschedule/admin_versions.html', {'rigs':rigList, 'wells':wellList, 'versions':versions, 'last_version':selected_version})

        except:
            print('Error')
            return render(request, 'rigschedule/result.html', {'response':'Error!'})

    return redirect('/rigschedule/aversions')




def admin_version_deletewell(request):
    try:
        if request.session['adminidx'] == 0 or request.session['adminidx'] == '':
            return render(request, 'rigschedule/admin_login.html')
    except KeyError:
        print('no key')
        return render(request, 'rigschedule/admin_login.html')

    adminidx = request.session['adminidx']

    version_id = request.GET['version_id']
    rig_id = request.GET['rig_id']
    well_id = request.GET['well_id']

    rigList = []
    wellList = []
    dataList = []

    versions = Version.objects.filter(member_id=adminidx)

    vers = Version.objects.filter(id=version_id)
    selected_version = vers.first()

    data = selected_version.data
    if data != '':
        try:
            decoded = json.loads(data)
            for data in decoded:
                rig_data = data['rig']

                rig = Rig()
                rig.id = rig_data['id']
                rig.member_id = rig_data['member_id']
                rig.name = rig_data['name']
                rig.type = rig_data['type']
                rig.pressure_rating = rig_data['pressure_rating']
                rig.specification = rig_data['specification']
                rig.contract_period = rig_data['contract_period']
                rig.summary = rig_data['summary']
                rig.comment = rig_data['comment']
                rig.created_date = rig_data['created_date']
                rig.version_text = selected_version.version_name


                rigList.append(rig)

                wells = []
                well_data_list = data['wells']
                for well_data in well_data_list:

                    if int(rig_id) == int(rig_data['id']) and int(well_id) == int(well_data['id']):
                        continue

                    well = Well()
                    well.id = well_data['id']
                    well.rig_id = well_data['rig_id']
                    well.name = well_data['name']

                    well.p10_start_date = well_data['p10_start_date']
                    well.p50_start_date = well_data['p50_start_date']
                    well.p90_start_date = well_data['p90_start_date']

                    well.p10_end_date = well_data['p10_end_date']
                    well.p50_end_date = well_data['p50_end_date']
                    well.p90_end_date = well_data['p90_end_date']

                    well.p10_status = well_data['p10_status']
                    well.p50_status = well_data['p50_status']
                    well.p90_status = well_data['p90_status']

                    well.p10_days_operation = well_data['p10_days_operation']
                    well.p50_days_operation = well_data['p50_days_operation']
                    well.p90_days_operation = well_data['p90_days_operation']

                    well.license = well_data['license']
                    well.field = well_data['field']
                    well.well_type = well_data['well_type']
                    well.well_status = well_data['well_status']
                    well.info = well_data['info']

                    wells.append(well)

                data = {
                    'rig':RigSerializer(rig, many=False).data,
                    'wells':WellSerializer(wells, many=True).data
                }
                dataList.append(data)

                processWellDates(wells)
                data = {
                    'rig':rig,
                    'wells':wells
                }
                wellList.append(data)

            selected_version.data = json.dumps(dataList)
            selected_version.save()

            versions = versions.order_by('-id')

            return render(request, 'rigschedule/admin_versions.html', {'rigs':rigList, 'wells':wellList, 'versions':versions, 'last_version':selected_version, 'rig_id':rig_id})

        except:
            print('Error')
            return render(request, 'rigschedule/result.html', {'response':'Error!'})

    return redirect('/rigschedule/aversions')


@api_view(['POST', 'GET'])
def admin_version_newwell(request):
    import datetime
    try:
        if request.session['adminidx'] == 0 or request.session['adminidx'] == '':
            return render(request, 'rigschedule/admin_login.html')
    except KeyError:
        print('no key')
        return render(request, 'rigschedule/admin_login.html')

    adminidx = request.session['adminidx']

    if request.method == 'POST':
        version_id = request.POST.get('version_id', '1')
        rig_id = request.POST.get('rig_id', '1')
        well_name = request.POST.get('well_name', '')
        p10_start_date = request.POST.get('p10_start_date', '')
        p50_start_date = request.POST.get('p50_start_date', '')
        p90_start_date = request.POST.get('p90_start_date', '')
        p10_days_operation = request.POST.get('p10_days_operation', '')
        p50_days_operation = request.POST.get('p50_days_operation', '')
        p90_days_operation = request.POST.get('p90_days_operation', '')
        p10_status = request.POST.get('p10_status', '')
        p50_status = request.POST.get('p50_status', '')
        p90_status = request.POST.get('p90_status', '')
        license = request.POST.get('license', '')
        field = request.POST.get('field', '')
        well_type = request.POST.get('well_type', '')
        well_status = request.POST.get('well_status', '')
        info = request.POST.get('info', '')

        rigList = []
        wellList = []
        dataList = []

        versions = Version.objects.filter(member_id=adminidx)

        vers = Version.objects.filter(id=version_id)
        selected_version = vers.first()

        data = selected_version.data
        if data != '':
            try:
                decoded = json.loads(data)
                for data in decoded:
                    rig_data = data['rig']

                    rig = Rig()
                    rig.id = rig_data['id']
                    rig.member_id = rig_data['member_id']
                    rig.name = rig_data['name']
                    rig.type = rig_data['type']
                    rig.pressure_rating = rig_data['pressure_rating']
                    rig.specification = rig_data['specification']
                    rig.contract_period = rig_data['contract_period']
                    rig.summary = rig_data['summary']
                    rig.comment = rig_data['comment']
                    rig.created_date = rig_data['created_date']
                    rig.version_text = selected_version.version_name

                    rigList.append(rig)

                    wells = []
                    wellids = []
                    well_data_list = data['wells']

                    for well_data in well_data_list:

                        well = Well()
                        well.id = well_data['id']
                        if int(rig_id) == int(rig_data['id']):
                            wellids.append(int(well.id))
                        well.rig_id = well_data['rig_id']
                        well.name = well_data['name']

                        well.p10_start_date = well_data['p10_start_date']
                        well.p50_start_date = well_data['p50_start_date']
                        well.p90_start_date = well_data['p90_start_date']

                        well.p10_end_date = well_data['p10_end_date']
                        well.p50_end_date = well_data['p50_end_date']
                        well.p90_end_date = well_data['p90_end_date']

                        well.p10_status = well_data['p10_status']
                        well.p50_status = well_data['p50_status']
                        well.p90_status = well_data['p90_status']

                        well.p10_days_operation = well_data['p10_days_operation']
                        well.p50_days_operation = well_data['p50_days_operation']
                        well.p90_days_operation = well_data['p90_days_operation']

                        well.license = well_data['license']
                        well.field = well_data['field']
                        well.well_type = well_data['well_type']
                        well.well_status = well_data['well_status']
                        well.info = well_data['info']

                        wells.append(well)

                    if int(rig_id) == int(rig_data['id']):
                        well = Well()
                        well.id = max(wellids) + 1
                        well.rig_id = rig_id
                        well.name = well_name
                        well.p10_start_date = p10_start_date
                        well.p50_start_date = p50_start_date
                        well.p90_start_date = p90_start_date
                        well.p10_days_operation = p10_days_operation
                        well.p50_days_operation = p50_days_operation
                        well.p90_days_operation = p90_days_operation
                        well.p10_status = p10_status
                        well.p50_status = p50_status
                        well.p90_status = p90_status

                        dt10 = datetime.datetime(year=int(p10_start_date.split('-')[0]), month=int(p10_start_date.split('-')[1]), day=int(p10_start_date.split('-')[2]))
                        p10_end_date = (dt10 + timedelta(days=int(p10_days_operation))).strftime("%Y-%m-%d")

                        dt50 = datetime.datetime(year=int(p50_start_date.split('-')[0]), month=int(p50_start_date.split('-')[1]), day=int(p50_start_date.split('-')[2]))
                        p50_end_date = (dt50 + timedelta(days=int(p50_days_operation))).strftime("%Y-%m-%d")

                        dt90 = datetime.datetime(year=int(p90_start_date.split('-')[0]), month=int(p90_start_date.split('-')[1]), day=int(p90_start_date.split('-')[2]))
                        p90_end_date = (dt90 + timedelta(days=int(p90_days_operation))).strftime("%Y-%m-%d")

                        well.p10_end_date = p10_end_date
                        well.p50_end_date = p50_end_date
                        well.p90_end_date = p90_end_date

                        well.license = license
                        well.field = field
                        well.well_type = well_type
                        well.well_status = well_status
                        well.info = info

                        wells.insert(0, well)

                    data = {
                        'rig':RigSerializer(rig, many=False).data,
                        'wells':WellSerializer(wells, many=True).data
                    }
                    dataList.append(data)

                    processWellDates(wells)
                    data = {
                        'rig':rig,
                        'wells':wells
                    }
                    wellList.append(data)

                selected_version.data = json.dumps(dataList)
                selected_version.save()

                versions = versions.order_by('-id')

                return render(request, 'rigschedule/admin_versions.html', {'rigs':rigList, 'wells':wellList, 'versions':versions, 'last_version':selected_version, 'rig_id':rig_id})

            except:
                print('Error')
                return render(request, 'rigschedule/result.html', {'response':'Error!'})

        return redirect('/rigschedule/aversions')

    else:
        return redirect('/rigschedule/aversions')



@api_view(['POST', 'GET'])
def admin_version_wellupdate(request):
    import datetime
    try:
        if request.session['adminidx'] == 0 or request.session['adminidx'] == '':
            return render(request, 'rigschedule/admin_login.html')
    except KeyError:
        print('no key')
        return render(request, 'rigschedule/admin_login.html')

    adminidx = request.session['adminidx']

    if request.method == 'POST':
        version_id = request.POST.get('version_id', '1')
        rig_id = request.POST.get('rig_id', '1')
        well_id = request.POST.get('well_id', '1')
        well_name = request.POST.get('well_name', '')
        p10_start_date = request.POST.get('p10_start_date', '')
        p50_start_date = request.POST.get('p50_start_date', '')
        p90_start_date = request.POST.get('p90_start_date', '')
        p10_days_operation = request.POST.get('p10_days_operation', '')
        p50_days_operation = request.POST.get('p50_days_operation', '')
        p90_days_operation = request.POST.get('p90_days_operation', '')
        p10_status = request.POST.get('p10_status', '')
        p50_status = request.POST.get('p50_status', '')
        p90_status = request.POST.get('p90_status', '')
        license = request.POST.get('license', '')
        field = request.POST.get('field', '')
        well_type = request.POST.get('well_type', '')
        well_status = request.POST.get('well_status', '')
        info = request.POST.get('info', '')

        rigList = []
        wellList = []
        dataList = []

        versions = Version.objects.filter(member_id=adminidx)

        vers = Version.objects.filter(id=version_id)
        selected_version = vers.first()

        data = selected_version.data
        if data != '':
            try:
                decoded = json.loads(data)
                for data in decoded:
                    rig_data = data['rig']

                    rig = Rig()
                    rig.id = rig_data['id']
                    rig.member_id = rig_data['member_id']
                    rig.name = rig_data['name']
                    rig.type = rig_data['type']
                    rig.pressure_rating = rig_data['pressure_rating']
                    rig.specification = rig_data['specification']
                    rig.contract_period = rig_data['contract_period']
                    rig.summary = rig_data['summary']
                    rig.comment = rig_data['comment']
                    rig.created_date = rig_data['created_date']
                    rig.version_text = selected_version.version_name

                    rigList.append(rig)

                    wells = []
                    well_data_list = data['wells']
                    for well_data in well_data_list:

                        well = None

                        if int(rig_id) == int(rig_data['id']) and int(well_id) == int(well_data['id']):
                            well = Well()
                            well.id = well_id
                            well.rig_id = rig_id
                            well.name = well_name
                            well.p10_start_date = p10_start_date
                            well.p50_start_date = p50_start_date
                            well.p90_start_date = p90_start_date
                            well.p10_days_operation = p10_days_operation
                            well.p50_days_operation = p50_days_operation
                            well.p90_days_operation = p90_days_operation
                            well.p10_status = p10_status
                            well.p50_status = p50_status
                            well.p90_status = p90_status

                            dt10 = datetime.datetime(year=int(p10_start_date.split('-')[0]), month=int(p10_start_date.split('-')[1]), day=int(p10_start_date.split('-')[2]))
                            p10_end_date = (dt10 + timedelta(days=int(p10_days_operation))).strftime("%Y-%m-%d")

                            dt50 = datetime.datetime(year=int(p50_start_date.split('-')[0]), month=int(p50_start_date.split('-')[1]), day=int(p50_start_date.split('-')[2]))
                            p50_end_date = (dt50 + timedelta(days=int(p50_days_operation))).strftime("%Y-%m-%d")

                            dt90 = datetime.datetime(year=int(p90_start_date.split('-')[0]), month=int(p90_start_date.split('-')[1]), day=int(p90_start_date.split('-')[2]))
                            p90_end_date = (dt90 + timedelta(days=int(p90_days_operation))).strftime("%Y-%m-%d")

                            well.p10_end_date = p10_end_date
                            well.p50_end_date = p50_end_date
                            well.p90_end_date = p90_end_date

                            well.license = license
                            well.field = field
                            well.well_type = well_type
                            well.well_status = well_status
                            well.info = info

                        else:
                            well = Well()
                            well.id = well_data['id']
                            well.rig_id = well_data['rig_id']
                            well.name = well_data['name']

                            well.p10_start_date = well_data['p10_start_date']
                            well.p50_start_date = well_data['p50_start_date']
                            well.p90_start_date = well_data['p90_start_date']

                            well.p10_end_date = well_data['p10_end_date']
                            well.p50_end_date = well_data['p50_end_date']
                            well.p90_end_date = well_data['p90_end_date']

                            well.p10_status = well_data['p10_status']
                            well.p50_status = well_data['p50_status']
                            well.p90_status = well_data['p90_status']

                            well.p10_days_operation = well_data['p10_days_operation']
                            well.p50_days_operation = well_data['p50_days_operation']
                            well.p90_days_operation = well_data['p90_days_operation']

                            well.license = well_data['license']
                            well.field = well_data['field']
                            well.well_type = well_data['well_type']
                            well.well_status = well_data['well_status']
                            well.info = well_data['info']

                        wells.append(well)

                    data = {
                        'rig':RigSerializer(rig, many=False).data,
                        'wells':WellSerializer(wells, many=True).data
                    }
                    dataList.append(data)

                    processWellDates(wells)
                    data = {
                        'rig':rig,
                        'wells':wells
                    }
                    wellList.append(data)

                selected_version.data = json.dumps(dataList)
                selected_version.save()

                versions = versions.order_by('-id')

                return render(request, 'rigschedule/admin_versions.html', {'rigs':rigList, 'wells':wellList, 'versions':versions, 'last_version':selected_version, 'rig_id':rig_id, 'well_id':well_id})

            except:
                print('Error')
                return render(request, 'rigschedule/result.html', {'response':'Error!'})

        return redirect('/rigschedule/aversions')

    else:
        return redirect('/rigschedule/aversions')



def admin_version_deleteversion(request):
    version_id = request.GET['version_id']
    versions = Version.objects.filter(id=version_id)
    versions.delete()
    return redirect('/rigschedule/aversions')












































######################################################################################### User ###########################################################################################################################
######################################################################################### User ###########################################################################################################################
######################################################################################### User ###########################################################################################################################


def user_signuppage(request):
    return render(request, 'rigschedule/user_signup.html')

def user_forgotpasswordpage(request):
    return render(request, 'rigschedule/user_forgotpassword.html')


@api_view(['GET', 'POST'])
def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email', '')
        password = request.POST.get('password', '')

        members = Member.objects.filter(email=email, password=password, role='')
        if members.count() > 0:
            member = members[0]
            request.session['useridx'] = member.pk
            return HttpResponse('0')
        else:
            members = Member.objects.filter(email=email, role='')
            if members.count() > 0:
                return HttpResponse('1')
            return HttpResponse('2')



@api_view(['GET', 'POST'])
def user_signup(request):
    if request.method == 'POST':
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        password = request.POST.get('password', '')

        members = Member.objects.filter(email=email, role='')
        if members.count() == 0:
            member = Member()
            member.admin_id = 1
            member.name = name
            member.email = email
            member.password = password
            member.registered_time = today.strftime("%b-%d-%Y")
            member.save()
            request.session['useridx'] = member.pk
            return HttpResponse('0')
        else:
            return HttpResponse('1')



@api_view(['GET', 'POST'])
def user_forgotpassword(request):
    if request.method == 'POST':
        email = request.POST.get('email', '')

        members = Member.objects.filter(email=email, role='')
        if members.count() == 0:
            return render(request, 'rigschedule/result.html',
                          {'response': 'This user\'s email doesn\'t exist. Please try another one.'})

        member = members[0]

        message = 'You are allowed to reset your password from your request.<br>For it, please click this link to reset your password.<br><br><a href=\'' + settings.URL + '/rigschedule/utoresetpassword?u=' + str(member.pk)
        message = message + '\' target=\'_blank\'>' + 'Link to reset password' + '</a>'

        html =  """\
                    <html>
                        <head></head>
                        <body>
                            <a href="#"><img src="https://hafizkurnia.pythonanywhere.com/static/images/rig_logo.jpg" style="width:120px; height:120px; border-radius:10px; margin-left:25px;"/></a>
                            <h2 style="color:#02839a;">Rig Schedule User's Security Information Update</h2>
                            <div style="font-size:14px; word-break: break-all; word-wrap: break-word;">
                                {mes}
                            </div>
                        </body>
                    </html>
                """
        html = html.format(mes=message)

        fromEmail = 'hafiz.kurnia92@gmail.com'
        toEmailList = []
        toEmailList.append(email)
        msg = EmailMultiAlternatives('We allowed you to reset your password', '', fromEmail, toEmailList)
        msg.attach_alternative(html, "text/html")
        msg.send(fail_silently=False)

        return HttpResponse('0')




def user_resetpasswordpage(request):
    member_id = request.GET['u']
    member = Member.objects.get(id=member_id)
    return render(request, 'rigschedule/user_resetpwd.html', {'email':member.email})



@api_view(['GET', 'POST'])
def user_resetpassword(request):
    if request.method == 'POST':
        email = request.POST.get('email', '')
        password = request.POST.get('password', '')

        members = Member.objects.filter(email=email, role='')
        if members.count() == 0:
            return HttpResponse('1')

        member = members[0]
        member.password = password
        member.save()

        return HttpResponse('0')


def user_logout(request):
    request.session['useridx'] = 0
    return redirect('/rigschedule/')








































































































