# import datetime
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

from other.models import Member, Bid, Folder, File , Note, BidFolder, NowBid


def loginpage(request):
    return render(request, 'other/userlogin.html')

def signuppage(request):
    return render(request, 'other/usersignup.html')

@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def userlogin(request):
    if request.method == 'POST':
        email = request.POST.get('email', '')
        password = request.POST.get('password', '')
        members = Member.objects.filter(email=email, password=password)
        if members.count() > 0:
            request.session['myID'] = members[0].pk
            return redirect('/other/folderhome')
        else:
            members = Member.objects.filter(email=email)
            if members.count() > 0:
                return render(request, 'other/result.html',
                          {'result': 'Your password is incorrect.'})
            else:
                return render(request, 'other/result.html',
                          {'result': 'You haven\'t been registered. Please sign up.'})
    else:
        return redirect('/other/loginpage')

@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def usersignup(request):
    if request.method == 'POST':
        email = request.POST.get('email', '')
        password = request.POST.get('password', '')
        members = Member.objects.filter(email=email)
        if members.count() > 0:
            return render(request, 'other/result.html',
                          {'result': 'Your email has already been registered. Please login.'})
        member = Member()
        member.email = email
        member.password = password
        member.save()
        request.session['myID'] = member.pk
        return redirect('/other/folderhome')
    else:
        return redirect('/other/signuppage')

def folderhome(request):
    try:
        if request.session['myID'] == 0 or request.session['myID'] == '':
            return render(request, 'other/userlogin.html')
    except KeyError:
        print('no session')
        return render(request, 'other/userlogin.html')

    idx = request.session['myID']

    folders = Folder.objects.filter(user_id=idx).order_by('-id')
    return render(request, 'other/folderhome.html', {'folders':folders})

@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def createnewfolder(request):
    if request.method == 'POST':
        name = request.POST.get('name', '')
        try:
            if request.session['myID'] == 0 or request.session['myID'] == '':
                return render(request, 'other/userlogin.html')
        except KeyError:
            print('no session')
            return render(request, 'other/userlogin.html')

        idx = request.session['myID']

        folder = Folder()
        folder.user_id = idx
        if len(name) == 0:
            name = 'New folder'
        folders = Folder.objects.filter(name=name)
        if folders.count() > 0:
            folders = Folder.objects.filter(name__startswith=name + '(')
            folder.name = name + '(' + str(folders.count() + 2) + ')'
        else:
            folders = Folder.objects.filter(name__startswith=name + '(')
            if folders.count() > 0:
                folder.name = name + '(' + str(folders.count() + 2) + ')'
            else:
                folder.name = name
        folder.files = '0'
        folder.save()
        return redirect('/other/folderhome')

def openfolder(request, folder_id):
    try:
        if request.session['myID'] == 0 or request.session['myID'] == '':
            return render(request, 'other/userlogin.html')
    except KeyError:
        print('no session')
        return render(request, 'other/userlogin.html')

    idx = request.session['myID']

    files = File.objects.filter(folder_id=folder_id).order_by('-id')
    folder_name = Folder.objects.get(id=folder_id).name
    return render(request, 'other/filehome.html', {'folder_id':folder_id, 'folder_name':folder_name, 'files':files})

@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def addfile(request):
    if request.method == 'POST':
        folder_id = request.POST.get('folder_id', '')
        file = request.FILES['file']

        try:
            if request.session['myID'] == 0 or request.session['myID'] == '':
                return render(request, 'other/userlogin.html')
        except KeyError:
            print('no session')
            return render(request, 'other/userlogin.html')

        idx = request.session['myID']

        f = File()
        files = File.objects.filter(name=file.name)
        if files.count() > 0:
            files = File.objects.filter(name__startswith=file.name + '(')
            f.name = file.name + '(' + str(files.count() + 2) + ')'
        else:
            files = File.objects.filter(name__startswith=file.name + '(')
            if files.count() > 0:
                f.name = file.name + '(' + str(files.count() + 2) + ')'
            else:
                f.name = file.name

        import time

        fs = FileSystemStorage()
        filename = fs.save(randomize(15) + f.name, file)
        uploaded_file_url = fs.url(filename)

        f.folder_id = folder_id
        f.link = settings.URL + uploaded_file_url
        f.save()
        folder = Folder.objects.get(id=folder_id)
        folder.files = str(int(folder.files) + 1)
        folder.save()
        return redirect('/other/openfolder/' + folder_id + '/')

def randomize(size):
    chars = string.ascii_lowercase + string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(size))

def deletefile(request, folder_id, file_id):

    try:
        if request.session['myID'] == 0 or request.session['myID'] == '':
            return render(request, 'other/userlogin.html')
    except KeyError:
        print('no session')
        return render(request, 'other/userlogin.html')

    idx = request.session['myID']

    file = File.objects.get(id=file_id)
    file.delete()
    fs = FileSystemStorage()
    fs.delete(file.link.replace(settings.URL + '/media/', ''))
    folder = Folder.objects.get(id=folder_id)
    folder.files = str(int(folder.files) - 1)
    folder.save()
    return redirect('/other/openfolder/' + folder_id + '/')

def filelogout(request):
    request.session.flush()
    for key in request.session.keys():
        del request.session[key]
    return redirect('/other/loginpage')

@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def savefolder(request, folder_id):
    if request.method == 'POST':
        name = request.POST.get('name', '')
        folder = Folder.objects.get(id=folder_id)
        if len(name) == 0:
            name = 'New folder'
        folders = Folder.objects.filter(name=name)
        if folders.count() > 0:
            folders = Folder.objects.filter(name__startswith=name + '(')
            folder.name = name.replace(find_between(name, '(', ')'), '') + '(' + str(folders.count() + 2) + ')'
        else:
            folders = Folder.objects.filter(name__startswith=name + '(')
            if folders.count() > 0:
                folder.name = name.replace(find_between(name, '(', ')'), '') + '(' + str(folders.count() + 2) + ')'
            else:
                folder.name = name
        folder.save()
        return redirect('/other/folderhome')
    else:
        return redirect('/other/folderhome')

@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def deletefolder(request, folder_id):
    if request.method == 'POST':
        folder = Folder.objects.get(id=folder_id)
        folder.delete()
        fs = FileSystemStorage()
        files = File.objects.filter(folder_id=folder_id)
        for file in files:
            file.delete()
            fs.delete(file.link.replace(settings.URL + '/media/', ''))
        bids = Bid.objects.filter(folder_id=folder_id)
        for bid in bids:
            bid.delete()
        return redirect('/other/folderhome')
    else:
        return redirect('/other/folderhome')

def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first ) - 1
        end = s.index( last, start ) + 1
        return s[start:end]
    except ValueError:
        return ""

def mynotes(request):
    try:
        if request.session['myID'] == 0 or request.session['myID'] == '':
            return render(request, 'other/userlogin.html')
    except KeyError:
        print('no session')
        return render(request, 'other/userlogin.html')

    idx = request.session['myID']

    notes = Note.objects.filter(user_id=idx).order_by('-id')
    return render(request, 'other/notebook.html', {'notes': notes})

@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def savenote(request,note_id):
    if request.method == 'POST':

        try:
            if request.session['myID'] == 0 or request.session['myID'] == '':
                return render(request, 'other/userlogin.html')
        except KeyError:
            print('no session')
            return render(request, 'other/userlogin.html')

        idx = request.session['myID']

        caption = request.POST.get('caption', '')
        text = request.POST.get('text', '')
        note = Note.objects.get(id=note_id)
        note.user_id = idx
        note.caption = caption
        note.text = text
        note.save()
        return redirect('/other/mynotes')

def addnote(request):
    try:
        if request.session['myID'] == 0 or request.session['myID'] == '':
            return render(request, 'other/userlogin.html')
    except KeyError:
        print('no session')
        return render(request, 'other/userlogin.html')

    idx = request.session['myID']

    note = Note()
    note.user_id = idx
    note.save()
    return redirect('/other/mynotes')

def deletenote(request, note_id):
    Note.objects.get(id=note_id).delete()
    return redirect('/other/mynotes')


def bidhome(request):

    try:
        if request.session['myID'] == 0 or request.session['myID'] == '':
            return render(request, 'other/userlogin.html')
    except KeyError:
        print('no session')
        return render(request, 'other/userlogin.html')

    idx = request.session['myID']

    folders = BidFolder.objects.filter(user_id=idx).order_by('-id')
    return render(request, 'other/bidhome.html', {'bidfolders':folders})

@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def newbidfolder(request):
    if request.method == 'POST':
        name = request.POST.get('name', '')

        try:
            if request.session['myID'] == 0 or request.session['myID'] == '':
                return render(request, 'other/userlogin.html')
        except KeyError:
            print('no session')
            return render(request, 'other/userlogin.html')

        idx = request.session['myID']

        folder = BidFolder()
        folder.user_id = idx
        if len(name) == 0:
            name = 'New folder'
        folders = BidFolder.objects.filter(name=name)
        if folders.count() > 0:
            folders = BidFolder.objects.filter(name__startswith=name + '(')
            folder.name = name + '(' + str(folders.count() + 2) + ')'
        else:
            folders = BidFolder.objects.filter(name__startswith=name + '(')
            if folders.count() > 0:
                folder.name = name + '(' + str(folders.count() + 2) + ')'
            else:
                folder.name = name
        folder.files = '0'
        folder.save()
        return redirect('/other/bidhome')

@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def savebidfolder(request, folder_id):
    if request.method == 'POST':
        name = request.POST.get('name', '')
        folder = BidFolder.objects.get(id=folder_id)
        if len(name) == 0:
            name = 'New folder'
        folders = BidFolder.objects.filter(name=name)
        if folders.count() > 0:
            folders = BidFolder.objects.filter(name__startswith=name + '(')
            folder.name = name.replace(find_between(name, '(', ')'), '') + '(' + str(folders.count() + 2) + ')'
        else:
            folders = BidFolder.objects.filter(name__startswith=name + '(')
            if folders.count() > 0:
                folder.name = name.replace(find_between(name, '(', ')'), '') + '(' + str(folders.count() + 2) + ')'
            else:
                folder.name = name
        folder.save()
        return redirect('/other/bidhome')
    else:
        return redirect('/other/bidhome')

@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def deletebidfolder(request, folder_id):
    if request.method == 'POST':
        folder = BidFolder.objects.get(id=folder_id)
        folder.delete()
        bids = Bid.objects.filter(folder_id=folder_id)
        if bids.count() > 0:
            for bid in bids:
                bid.delete()
        return redirect('/other/bidhome')
    else:
        return redirect('/other/bidhome')


def openbidfolder(request, folder_id):

    try:
        if request.session['myID'] == 0 or request.session['myID'] == '':
            return render(request, 'other/userlogin.html')
    except KeyError:
        print('no session')
        return render(request, 'other/userlogin.html')

    idx = request.session['myID']
    members = Member.objects.filter(id=idx)
    if members.count() == 0:
        return render(request, 'other/result.html', {'result': 'Your account doesn\'t exist.'})

    member = members[0]

    bids = Bid.objects.filter(user_id=idx, folder_id=folder_id).order_by('-id')
    bfolder = BidFolder.objects.get(id=folder_id)
    folder_name = bfolder.name

    bid_id = 0
    try:
        bid_id = request.GET['bid_id']
    except KeyError:
        print('No key')

    return render(request, 'other/mybids.html', {'bids': bids, 'folder_id':folder_id, 'folder_name':folder_name, 'member':member, 'bid_id': bid_id})

@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def savebid(request,bid_id, folder_id):
    if request.method == 'POST':

        try:
            if request.session['myID'] == 0 or request.session['myID'] == '':
                return render(request, 'other/userlogin.html')
        except KeyError:
            print('no session')
            return render(request, 'other/userlogin.html')

        idx = request.session['myID']

        caption = request.POST.get('caption', '')
        text = request.POST.get('text', '')
        bid = Bid.objects.get(id=bid_id)
        bid.user_id = idx
        bid.folder_id = folder_id
        bid.caption = caption
        bid.text = text
        bid.save()

        return redirect('/other/openbidfolder/' + folder_id + '?bid_id=' + str(bid.pk))

def addbid(request, folder_id):

    try:
        if request.session['myID'] == 0 or request.session['myID'] == '':
            return render(request, 'other/userlogin.html')
    except KeyError:
        print('no session')
        return render(request, 'other/userlogin.html')

    idx = request.session['myID']

    bid = Bid()
    bid.user_id = idx
    bid.folder_id = folder_id
    bid.save()
    return redirect('/other/openbidfolder/' + folder_id)

def deletebid(request, bid_id, folder_id):
    Bid.objects.get(id=bid_id).delete()
    return redirect('/other/openbidfolder/' + folder_id)


def nowedit(request):

    try:
        if request.session['myID'] == 0 or request.session['myID'] == '':
            return render(request, 'other/userlogin.html')
    except KeyError:
        print('no session')
        return render(request, 'other/userlogin.html')

    idx = request.session['myID']

    nbid = None

    nbids = NowBid.objects.filter(user_id=idx)
    if nbids.count() == 0:
        nbid = NowBid()
        nbid.user_id = idx
        nbid.save()
    else:
        nbid = nbids[0]
    return render(request, 'other/nowbitedit.html', {'nowbid':nbid})


@csrf_protect
@csrf_exempt
@permission_classes((AllowAny,))
@api_view(['GET', 'POST'])
def savenowbid(request):
    if request.method == 'POST':
        try:
            if request.session['myID'] == 0 or request.session['myID'] == '':
                return render(request, 'other/userlogin.html')
        except KeyError:
            print('no session')
            return render(request, 'other/userlogin.html')

        idx = request.session['myID']

        text = request.POST.get('text', '')

        nbids = NowBid.objects.filter(user_id=idx)
        if nbids.count() == 0:
            nbid = NowBid()
        nbid = nbids[0]
        nbid.user_id = idx
        nbid.text = text
        nbid.save()
        return redirect('/other/nowedit/')














































