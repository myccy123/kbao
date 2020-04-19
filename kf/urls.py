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
    url(r'^charge/list/', charge_list),
    url(r'^order/list/', order_list),
    url(r'^export/orders/', export_order_list),
    url(r'^update/user/', udpate_user_info),
    url(r'^update/history/', update_history),
    url(r'^user/list/', user_list),
    url(r'^charge/verify/', charge_verify),
    url(r'^order/verify/', order_verify),
    url(r'^order/resend/', order_resend),
    url(r'^order/send/', order_send),
    url(r'^order/resendDetailExport/', export_resend_detail),
    url(r'^express/save/', express_save),
    url(r'^express/list/', express_list),
    url(r'^express/delete/', express_delete),
    url(r'^excel/upload/', excel_save),
    url(r'^reset/password/', reset_password),
    url(r'^update/kf/', update_kf),
    url(r'^kf/list/', kf_list),
    url(r'^notice/list/', notice_list),
    url(r'^notice/add/', add_notice),
    url(r'^notice/update/', update_notice),
    url(r'^notice/delete/', delete_notice),
    url(r'^bi/all/day/', sum_day_all),
    url(r'^bi/all/month/', sum_month_all),
    url(r'^bi/user/day/', sum_day_user),
    url(r'^kuaibao/callback/', kuaibao_callback),
    url(r'^ali/callback/', ali_callback),
]
