"""myweb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^sign/up/', sign_up),
    url(r'^sign/in/', sign_in),
    url(r'^change/password/', change_password),
    url(r'^log/out/', log_out),
    url(r'^fetch/img/', get_vailate_img),
    url(r'^charge/commit/', charge),
    url(r'^charge/list/', charge_list),
    url(r'^place/order/', place_order),
    url(r'^flow/list/', all_flow),
    url(r'^export/flows/', export_flow_list),
    url(r'^order/list/', order_list),
    url(r'^export/orders/', export_order_list),
    url(r'^user/info/', get_user_info),
    url(r'^address/list/', address_list),
    url(r'^address/delete/', address_delete),
    url(r'^upload/orders/', upload_orders),
    url(r'^set/default/address/', set_default_address),
    url(r'^set/default/express/', set_default_express),
    url(r'^code/info/', get_code_info),
    url(r'^refresh/vailate/', refresh_vailate_img),
]

