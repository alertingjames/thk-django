from django.conf.urls import url
from . import views

app_name='rigwell'

urlpatterns=[
    url(r'^$', views.mea_jobboard, name='mea_jobboard'),
    url(r'browsejobs', views.browsejobs, name='browsejobs'),
    url(r'candidates', views.mea_candidates, name='mea_candidates'),
    url(r'postjob', views.postjob, name='postjob'),
    url(r'wantjob', views.wantjob, name='wantjob'),
    url(r'toblog', views.toblog, name='toblog'),
    url(r'contact', views.mea_contact, name='mea_contact'),
    url(r'blogdetail', views.blogdetail, name='blogdetail'),
    url(r'forgotpassword', views.forgotpassword, name='forgotpassword'),
    url(r'loginpage', views.loginpage, name='loginpage'),
    url(r'signuppage', views.signuppage, name='signuppage'),
    url(r'jobdetail', views.jobdetail, name='jobdetail'),
    url(r'categoryjobs', views.categoryjobs, name='categoryjobs'),
    url(r'jobcompanies', views.jobcompanies, name='jobcompanies'),
    url(r'comprofile', views.companyprofile, name='companyprofile'),
    url(r'comreviews', views.companyreviews, name='companyreviews'),
    url(r'rating', views.rating, name='rating'),
    url(r'comsalaries', views.companysalaries, name='companysalaries'),
    url(r'comjobs', views.companyjobs, name='companyjobs'),
    url(r'awj-login', views.awj_login, name='awj_login'),
    url(r'awj-signup', views.awj_signup, name='awj_signup'),
    url(r'awj-logout', views.awj_logout, name='awj_logout'),
    url(r'awj-home', views.awj_home, name='awj_home'),

]