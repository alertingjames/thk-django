from django.conf.urls import url
from . import views, userhome

app_name='rigschedule'


urlpatterns=[
    url(r'^$', userhome.user_home, name='user_home'),

    ############################## Admin #######################################################################################################

    url(r'admin',views.admin_loginpage,  name='admin_loginpage'),
    url(r'alogin',views.admin_login,  name='admin_login'),
    url(r'atoforgotpassword',views.admin_forgotpasswordpage,  name='admin_forgotpasswordpage'),
    url(r'aforgotpassword',views.admin_forgotpassword,  name='admin_forgotpassword'),
    url(r'ahome',views.admin_home,  name='admin_home'),
    url(r'atoresetpassword',views.admin_resetpasswordpage,  name='admin_resetpasswordpage'),
    url(r'aresetpassword',views.admin_resetpassword,  name='admin_resetpassword'),
    url(r'alogout',views.admin_logout,  name='admin_logout'),
    url(r'anewrig',views.admin_uploadnewrig,  name='admin_uploadnewrig'),
    url(r'anewwell',views.admin_newwell,  name='admin_newwell'),
    url(r'aeditrig',views.admin_updaterig,  name='admin_updaterig'),
    url(r'arigdel',views.admin_deleterig,  name='admin_deleterig'),
    url(r'awelledit',views.admin_wellupdate,  name='admin_wellupdate'),
    url(r'adelwell',views.admin_deletewell,  name='admin_deletewell'),
    url(r'ausers',views.admin_users,  name='admin_users'),
    url(r'adeluser',views.admin_deleteuser,  name='admin_deleteuser'),
    url(r'aversions',views.admin_versions,  name='admin_versions'),
    url(r'asaveversion',views.admin_saveversion,  name='admin_saveversion'),
    url(r'aveditrig',views.admin_version_updaterig,  name='admin_version_updaterig'),
    url(r'avrigdel',views.admin_version_deleterig,  name='admin_version_deleterig'),
    url(r'avnewwell',views.admin_version_newwell,  name='admin_version_newwell'),
    url(r'avdelwell',views.admin_version_deletewell,  name='admin_version_deletewell'),
    url(r'avwelledit',views.admin_version_wellupdate,  name='admin_version_wellupdate'),
    url(r'avdelversion',views.admin_version_deleteversion,  name='admin_version_deleteversion'),


    #################################### User ###################################################################################################

    url(r'utoforgotpassword',views.user_forgotpasswordpage,  name='user_forgotpasswordpage'),
    url(r'uforgotpassword',views.user_forgotpassword,  name='user_forgotpassword'),
    url(r'ulogin',views.user_login,  name='user_login'),
    url(r'utosignup',views.user_signuppage,  name='user_signuppage'),
    url(r'usignup',views.user_signup,  name='user_signup'),
    url(r'utoresetpassword',views.user_resetpasswordpage,  name='user_resetpasswordpage'),
    url(r'uresetpassword',views.user_resetpassword,  name='user_resetpassword'),
    url(r'ulogout',views.user_logout,  name='user_logout'),
]














































