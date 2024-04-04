from django.urls import re_path, include 
from tutorials import views 
 
urlpatterns = [ 
    re_path(r'^api/tutorials$', views.tutorial_list),
    re_path(r'^api/tutorials/(?P<pk>[0-9]+)$', views.tutorial_detail),
    re_path(r'^api/tutorials/published$', views.tutorial_list_published),
    re_path(r'^api/users$', views.user_list),
    re_path(r'^api/tutorials/(?P<tutorial_pk>[0-9]+)/users$', views.tutorial_users_manage),
    re_path(r'^api/users/(?P<pk>[0-9]+)$', views.user_detail)
]