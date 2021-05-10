from django.conf.urls import url, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from rest_framework.urlpatterns import format_suffix_patterns
from rigwell import views

urlpatterns = [
    # url(r'^admin/', admin.site.urls),
    url(r'^rigwell/', include('rigwell.urls')),
    url(r'^other/', include('other.urls')),
    url(r'^rigschedule/', include('rigschedule.urls')),
    url(r'^$', views.rig_user_loginpage, name='rig_user_loginpage'),

    ################ Admin ################################################################################

    url(r'^admin',views.rig_admin,  name='rig_admin'),
    url(r'^ralogin',views.rig_admin_login,  name='rig_admin_login'),
    url(r'^rahome',views.rig_admin_home,  name='rig_admin_home'),
    url(r'^ranewrig',views.rig_admin_new_rig,  name='rig_admin_new_rig'),
    url(r'^ranewwell',views.rig_admin_new_well,  name='rig_admin_new_well'),
    url(r'^ranewactivity',views.rig_admin_new_activity,  name='rig_admin_new_activity'),
    url(r'^raactitemsetup',views.rig_admin_act_item_setup,  name='rig_admin_act_item_setup'),
    url(r'^ralogout',views.rig_admin_logout,  name='rig_admin_logout'),
    url(r'^raimportexcel', views.rig_admin_import_excel, name='rig_admin_import_excel'),
    url(r'^raexcelimportdata', views.rig_admin_import_excel_data, name='rig_admin_import_excel_data'),
    url(r'^raexltotalrows', views.rig_admin_get_loaded_excel_total_rows, name='rig_admin_get_loaded_excel_total_rows'),
    url(r'^ramanuallysetdata', views.rig_admin_act_manually_setup_data, name='rig_admin_act_manually_setup_data'),
    url(r'^raviewactivitydata', views.rig_admin_view_activity_data, name='rig_admin_view_activity_data'),
    url(r'^ra_to_page',views.ra_to_page,  name='ra_to_page'),
    url(r'^ra_to_previous',views.ra_to_previous,  name='ra_to_previous'),
    url(r'^ra_to_next',views.ra_to_next,  name='ra_to_next'),
    url(r'^raactivitydataview', views.rig_admin_activity_data_view, name='rig_admin_activity_data_view'),

    url(r'^rarigdel', views.rig_admin_delete_rig, name='rig_admin_delete_rig'),
    url(r'^radelwell', views.rig_admin_delete_well, name='rig_admin_delete_well'),
    url(r'^radelactivity', views.rig_admin_delete_activity, name='rig_admin_delete_activity'),
    url(r'^racleardata', views.rig_admin_clear_activity_item_data, name='rig_admin_clear_activity_item_data'),

    url(r'^raeditrig', views.rig_admin_edit_rig, name='rig_admin_edit_rig'),
    url(r'^raeditwell', views.rig_admin_edit_well, name='rig_admin_edit_well'),
    url(r'^raeditactivity', views.rig_admin_edit_activity, name='rig_admin_edit_activity'),

    ################ User #######################################################################################

    url(r'^user', views.rig_user_loginpage, name='rig_user_loginpage'),
    url(r'^rusignuppage', views.rig_user_signuppage, name='rig_user_signuppage'),
    url(r'^ruforgotpasswordpage', views.rig_user_forgotpasswordpage, name='rig_user_forgotpasswordpage'),

    url(r'^rulogin', views.rig_user_login, name='rig_user_login'),
    url(r'^ruregister', views.rig_user_signup, name='rig_user_signup'),
    url(r'^ruhome', views.rig_user_home, name='rig_user_home'),
    url(r'^rulogout', views.rig_user_logout, name='rig_user_logout'),

    url(r'rusendmailforgotpassword',views.rig_user_send_mail_forgotpassword,  name='rig_user_send_mail_forgotpassword'),
    url(r'ruresetpassword', views.rig_user_resetpassword, name='rig_user_resetpassword'),
    url(r'rurstpwd',views.rig_user_rstpwd,  name='rig_user_rstpwd'),

    url(r'rupasswordchange', views.rig_user_passwordchange, name='rig_user_passwordchange'),
    url(r'ruchangepassword', views.rig_user_changepassword, name='rig_user_changepassword'),
    url(r'ruwelldetail', views.rig_user_well_detail, name='rig_user_well_detail'),
    url(r'rueow', views.rig_user_eow, name='rig_user_eow'),




    ############### RIGWELL Activity Item Data Fields Set Up ####################################################

    url(r'^rasetfields', views.rig_admin_set_fields, name='rig_admin_set_fields'),
]


urlpatterns+=static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns=format_suffix_patterns(urlpatterns)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)








































