from django.conf.urls import url
from . import views

app_name='other'

urlpatterns=[
    url(r'^$', views.loginpage, name='loginpage'),
    url(r'bidhome',views.bidhome,  name='bidhome'),
    url(r'newbidfolder',views.newbidfolder,  name='newbidfolder'),
    url(r'savebidfolder/(?P<folder_id>[0-9]+)/$', views.savebidfolder, name='savebidfolder'),
    url(r'deletebidfolder/(?P<folder_id>[0-9]+)/$', views.deletebidfolder, name='deletebidfolder'),
    url(r'openbidfolder/(?P<folder_id>[0-9]+)/$', views.openbidfolder, name='openbidfolder'),
    url(r'addbid/(?P<folder_id>[0-9]+)/$',views.addbid,  name='addbid'),
    url(r'savebid/(?P<bid_id>[0-9]+)/(?P<folder_id>[0-9]+)/$', views.savebid, name='savebid'),
    url(r'deletebid/(?P<bid_id>[0-9]+)/(?P<folder_id>[0-9]+)/$', views.deletebid, name='deletebid'),

    url(r'loginpage', views.loginpage, name='loginpage'),
    url(r'signuppage', views.signuppage, name='signuppage'),
    url(r'userlogin', views.userlogin, name='userlogin'),
    url(r'usersignup', views.usersignup, name='usersignup'),
    url(r'folderhome', views.folderhome, name='folderhome'),
    url(r'createnewfolder',views.createnewfolder,  name='createnewfolder'),
    url(r'openfolder/(?P<folder_id>[0-9]+)/$', views.openfolder, name='openfolder'),
    url(r'addfile', views.addfile, name='addfile'),
    url(r'deletefile/(?P<folder_id>[0-9]+)/(?P<file_id>[0-9]+)/$', views.deletefile, name='deletefile'),
    url(r'savefolder/(?P<folder_id>[0-9]+)/$', views.savefolder, name='savefolder'),
    url(r'deletefolder/(?P<folder_id>[0-9]+)/$', views.deletefolder, name='deletefolder'),
    url(r'filelogout', views.filelogout, name='filelogout'),

    url(r'mynotes',views.mynotes,  name='mynotes'),
    url(r'addnote',views.addnote,  name='addnote'),
    url(r'savenote/(?P<note_id>[0-9]+)/$', views.savenote, name='savenote'),
    url(r'deletenote/(?P<note_id>[0-9]+)/$', views.deletenote, name='deletenote'),

    url(r'nowedit',views.nowedit,  name='nowedit'),
    url(r'savenowbid',views.savenowbid,  name='savenowbid'),
]



































