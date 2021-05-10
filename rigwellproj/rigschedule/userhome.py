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


def user_home(request):
    import datetime
    import calendar

    try:
        if request.session['useridx'] == 0 or request.session['useridx'] == '':
            return render(request, 'rigschedule/user_login.html')
    except KeyError:
        print('no key')
        return render(request, 'rigschedule/user_login.html')

    useridx = request.session['useridx']

    try:
        version_name = request.GET['version_name']
        p_name = request.GET['p_name']
        months = request.GET['months']
        well_type = request.GET['well_type']
        well_field = request.GET['well_field']
        license = request.GET['license']
        prev = request.GET['prev']
        next = request.GET['next']
        q = request.GET['q']
    except KeyError:
        print('No key')
        return redirect('/rigschedule?version_name=&p_name=P50&months=12&well_type=&well_field&license=&q=&prev=no&next=no')

    datas = []
    rwdataList = []
    monthTimeList = []
    licenseList = []
    fieldList = []
    yearStr = str(today.year)

    fieldNameList = []

    versionList = []
    last_version = None
    versions = Version.objects.filter(member_id=1).order_by('-id')
    if versions.count() > 0:
        last_version = versions.first()
        if version_name == '':
            version_name = last_version.version_name
        else:
            last_version = Version.objects.filter(version_name=version_name)[0]
        if prev == 'no' and next == 'no':
            try:
                lastVersionYear = request.session['last_version_year']
                lastVersionMonth = request.session['last_version_month']
                # months = request.session['months']
                monthTimeList, fieldNameList, minYear, minMonth, maxYear, maxMonth = getMonthList(int(lastVersionYear), int(lastVersionMonth), int(months))
            except KeyError:
                print('No key')
                monthTimeList, fieldNameList, minYear, minMonth, maxYear, maxMonth = getMonthList(int(last_version.year), int(last_version.month), int(months))
            yearStr = str(minYear) + ' - ' + str(maxYear)
            request.session['min_year'] = minYear
            request.session['min_month'] = minMonth
            request.session['max_year'] = maxYear
            request.session['max_month'] = maxMonth
            request.session['last_version_year'] = last_version.year
            request.session['last_version_month'] = last_version.month
            request.session['months'] = months
            for version in versions:
                dt = datetime.datetime(year=int(version.year), month=int(version.month), day=1)
                tm = time.mktime(dt.timetuple())
                if tm in monthTimeList:
                    versionList.insert(0,version)
        elif prev == 'yes':
            minYear = request.session['min_year']
            minMonth = request.session['min_month']
            monthTimeList, fieldNameList, minYear, minMonth, maxYear, maxMonth = getPrevMonthList(int(minYear), int(minMonth), int(months))
            yearStr = str(minYear) + ' - ' + str(maxYear)
            request.session['min_year'] = minYear
            request.session['min_month'] = minMonth
            request.session['max_year'] = maxYear
            request.session['max_month'] = maxMonth
            request.session['last_version_year'] = minYear
            request.session['last_version_month'] = minMonth
            request.session['months'] = months
            for version in versions:
                dt = datetime.datetime(year=int(version.year), month=int(version.month), day=1)
                tm = time.mktime(dt.timetuple())
                if tm in monthTimeList:
                    versionList.insert(0,version)
        elif next == 'yes':
            maxYear = request.session['max_year']
            maxMonth = request.session['max_month']
            monthTimeList, fieldNameList, minYear, minMonth, maxYear, maxMonth = getNextMonthList(int(maxYear), int(maxMonth), int(months))
            yearStr = str(minYear) + ' - ' + str(maxYear)
            request.session['min_year'] = minYear
            request.session['min_month'] = minMonth
            request.session['max_year'] = maxYear
            request.session['max_month'] = maxMonth
            request.session['last_version_year'] = maxYear
            request.session['last_version_month'] = maxMonth
            request.session['months'] = months
            for version in versions:
                dt = datetime.datetime(year=int(version.year), month=int(version.month), day=1)
                tm = time.mktime(dt.timetuple())
                if tm in monthTimeList:
                    versionList.insert(0,version)

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
                    rig.year = version.year
                    rig.month = version.month
                    rig.version = version.version
                    rig.version_text = version.version_name

                    # rigList.append(rig)

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

                        if not well.license in licenseList:
                            licenseList.append(well.license)

                        if not well.field in fieldList:
                            fieldList.append(well.field)

                        if well_type != '':
                            if well_type == well.well_type or well_type == well.well_status:
                                if q != '':
                                    if q.lower() in well.name.lower() or q.lower() in well.well_type.lower() or q.lower() in well.well_status.lower() or q.lower() in well.info.lower() \
                                    or q.lower() in well.p10_start_date.lower() or q.lower() in well.p50_start_date.lower() or q.lower() in well.p90_start_date.lower() or q.lower() in well.field.lower() \
                                    or q.lower() in well.license.lower():
                                        if not well in wells:
                                            wells.append(well)
                                else:
                                    if not well in wells:
                                        wells.append(well)
                        elif well_field != '':
                            if well_field == well.field:
                                if q != '':
                                    if q.lower() in well.name.lower() or q.lower() in well.well_type.lower() or q.lower() in well.well_status.lower() or q.lower() in well.info.lower() \
                                    or q.lower() in well.p10_start_date.lower() or q.lower() in well.p50_start_date.lower() or q.lower() in well.p90_start_date.lower() or q.lower() in well.field.lower() \
                                    or q.lower() in well.license.lower():
                                        if not well in wells:
                                            wells.append(well)
                                else:
                                    if not well in wells:
                                        wells.append(well)
                        elif license != '':
                            if license == well.license:
                                if q != '':
                                    if q.lower() in well.name.lower() or q.lower() in well.well_type.lower() or q.lower() in well.well_status.lower() or q.lower() in well.info.lower() \
                                    or q.lower() in well.p10_start_date.lower() or q.lower() in well.p50_start_date.lower() or q.lower() in well.p90_start_date.lower() or q.lower() in well.field.lower() \
                                    or q.lower() in well.license.lower():
                                        if not well in wells:
                                            wells.append(well)
                                else:
                                    if not well in wells:
                                        wells.append(well)
                        else:
                            if q != '':
                                if q.lower() in well.name.lower() or q.lower() in well.well_type.lower() or q.lower() in well.well_status.lower() or q.lower() in well.info.lower() \
                                or q.lower() in well.p10_start_date.lower() or q.lower() in well.p50_start_date.lower() or q.lower() in well.p90_start_date.lower() or q.lower() in well.field.lower() \
                                or q.lower() in well.license.lower():
                                    if not well in wells:
                                        wells.append(well)
                            else:
                                if not well in wells:
                                    wells.append(well)

                    rwdata = [rig, wells]
                    rwdataList.append(rwdata)

                    # if q != '':
                    #     if q.lower() in rig.name.lower() or q.lower() in rig.type.lower() or q.lower() in rig.specification.lower() \
                    #     or q.lower() in rig.contract_period.lower() or q.lower() in rig.summary.lower() or q.lower() in rig.version_text.lower():
                    #         rwdataList.append(rwdata)
                    # else:
                    #     rwdataList.append(rwdata)

            except:
                print('Error')

        rigs = Rig.objects.filter(member_id=1)
        for rig in rigs:
            dlist = []
            rwdata0 = None
            for rwdata in rwdataList:
                if rig.name == rwdata[0].name:
                    rwdata0 = rwdata
                    break
            if rwdata0 is not None:
                lastwsids = []
                for mt in monthTimeList:
                    ws = []
                    for well in rwdata0[1]:
                        sdt = datetime.datetime(year=int(getPStartDate(well, p_name).split('-')[0]), month=int(getPStartDate(well, p_name).split('-')[1]), day=int(getPStartDate(well, p_name).split('-')[2]))
                        for daycnt in range(0, int(getPDays(well, p_name)) + 1):
                            dt = (sdt + timedelta(days=int(daycnt)))
                            dt = datetime.datetime(year=dt.year, month=dt.month, day=1)
                            tm = time.mktime(dt.timetuple())
                            if mt == tm:
                                # well.status = ''
                                # if well.id in lastwsids:
                                #     well.status = 'rpt'
                                ws.insert(0, well)
                                if well.id in lastwsids:
                                    indx = lastwsids.index(well.id)
                                    for k in range(0, indx):
                                        ws.insert(0, None)
                                break

                    rwjsondata = {
                        'rig':rwdata0[0],
                        'wells':ws
                    }
                    dlist.append(rwjsondata)

                    lastwsids = []
                    for w in ws:
                        if w is None:
                            lastwsids.append(-1)
                        else:
                            lastwsids.append(w.id)


                r = rwdata0[0]
                rrww = {
                    'rig':r,
                    'wells':[]
                }
                data = {
                    'rigwell':rrww,
                    'dlist':dlist
                }
                datas.append(data)

    if last_version is not None:
        month_name = calendar.month_abbr[int(last_version.month)]
        version_name = month_name + ' ' + str(last_version.year)

    context = {
        'fieldnames':fieldNameList,
        'datas':datas,
        'version_name':version_name,
        'years':yearStr,
        'versions':versions,
        'last_version':last_version,
        'p_name':p_name,
        'months':months,
        'well_type':well_type,
        'fields':fieldList,
        'well_field':well_field,
        'licenses':licenseList,
        'license':license,
        'q':q,
    }
    return render(request, 'rigschedule/user_home.html', context)


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



def getMonthList(syear, smonth, months):
    import time
    import datetime
    import calendar
    year = syear
    month = smonth
    monthTimeList = []
    fieldNameList = []
    yearList = []
    monthList = []

    if months > 1:
        for i in range(0, months):
            dt = datetime.datetime(year=year, month=month, day=1)
            tm = time.mktime(dt.timetuple())
            monthTimeList.insert(0, tm)
            month_name = calendar.month_abbr[int(month)]
            fieldNameList.insert(0, month_name + ' ' + str(year))
            yearList.insert(0,year)
            monthList.insert(0,month)

            month = month - 1
            if month == 0:
                month = 12
                year = year - 1
    else:
        dt = datetime.datetime(year=year, month=month, day=1)
        tm = time.mktime(dt.timetuple())
        monthTimeList.insert(0, tm)
        month_name = calendar.month_abbr[int(month)]
        fieldNameList.insert(0, month_name + ' ' + str(year))
        yearList.insert(0,year)
        monthList.insert(0,month)

    minYear = yearList[0]
    minMonth = monthList[0]
    maxYear = yearList[len(yearList) - 1]
    maxMonth = monthList[len(monthList) - 1]

    return monthTimeList, fieldNameList, minYear, minMonth, maxYear, maxMonth



def getPrevMonthList(syear, smonth, months):
    import time
    import datetime
    import calendar
    year = syear
    month = smonth
    monthTimeList = []
    fieldNameList = []
    yearList = []
    monthList = []

    if months > 1:
        for i in range(0, months):
            dt = datetime.datetime(year=year, month=month, day=1)
            tm = time.mktime(dt.timetuple())
            monthTimeList.insert(0, tm)
            month_name = calendar.month_abbr[int(month)]
            fieldNameList.insert(0, month_name + ' ' + str(year))
            yearList.insert(0,year)
            monthList.insert(0,month)

            month = month - 1
            if month == 0:
                month = 12
                year = year - 1
    else:
        month = month - 1
        if month == 0:
            month = 12
            year = year - 1
        dt = datetime.datetime(year=year, month=month, day=1)
        tm = time.mktime(dt.timetuple())
        monthTimeList.insert(0, tm)
        month_name = calendar.month_abbr[int(month)]
        fieldNameList.insert(0, month_name + ' ' + str(year))
        yearList.insert(0,year)
        monthList.insert(0,month)

    minYear = yearList[0]
    minMonth = monthList[0]
    maxYear = yearList[len(yearList) - 1]
    maxMonth = monthList[len(monthList) - 1]

    return monthTimeList, fieldNameList, minYear, minMonth, maxYear, maxMonth



def getNextMonthList(syear, smonth, months):
    import time
    import datetime
    import calendar
    year = syear
    month = smonth
    monthTimeList = []
    fieldNameList = []
    yearList = []
    monthList = []

    if months > 1:
        for i in range(0, months):
            dt = datetime.datetime(year=year, month=month, day=1)
            tm = time.mktime(dt.timetuple())
            monthTimeList.append(tm)
            month_name = calendar.month_abbr[int(month)]
            fieldNameList.append(month_name + ' ' + str(year))
            yearList.append(year)
            monthList.append(month)

            month = month + 1
            if month == 13:
                month = 1
                year = year + 1
    else:
        month = month + 1
        if month == 13:
            month = 1
            year = year + 1
        dt = datetime.datetime(year=year, month=month, day=1)
        tm = time.mktime(dt.timetuple())
        monthTimeList.append(tm)
        month_name = calendar.month_abbr[int(month)]
        fieldNameList.append(month_name + ' ' + str(year))
        yearList.append(year)
        monthList.append(month)

    minYear = yearList[0]
    minMonth = monthList[0]
    maxYear = yearList[len(yearList) - 1]
    maxMonth = monthList[len(monthList) - 1]

    return monthTimeList, fieldNameList, minYear, minMonth, maxYear, maxMonth



def getPDays(well, pname):
    if pname == 'P10':
        return well.p10_days_operation
    elif pname == 'P50':
        return well.p50_days_operation
    elif pname == 'P90':
        return well.p90_days_operation
    return '0'


def getPStartDate(well, pname):
    if pname == 'P10':
        return well.p10_start_date
    elif pname == 'P50':
        return well.p50_start_date
    elif pname == 'P90':
        return well.p90_start_date
    return ''


def procws(ws, lastwsids):
    for w in ws:
        if w is not None and w.id in lastwsids:
            w.status = 'rpt'
    return ws














































