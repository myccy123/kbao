from django.contrib import admin
from .models import *


# Register your models here.
@admin.register(UserInfo)
class UserInfoAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'user_id', 'user_type', 'role', 'bal', 'def_express',)
    search_fields = ('userid',)
    list_filter = ('user_type', 'role',)
    readonly_fields = ('user_id', 'id',)
    list_display_links = ('user_id', 'id',)
    fieldsets = (
        (None, {
            'fields': ('id', 'user_id', 'user_type', 'role',
                       'tel', 'db_name', 'qq', 'wx', 'email',
                       'bal', 'avatar', 'reference', 'def_express',)
        }),
    )


@admin.register(ChargeInfo)
class ChargeInfoAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'charge_type', 'order_id', 'amt', 'status',)
    search_fields = ('userid',)
    list_filter = ('charge_type',)
    readonly_fields = ('user_id', 'id',)
    list_display_links = ('user_id', 'id',)
    fieldsets = (
        (None, {
            'fields': ('id', 'user_id', 'charge_type', 'order_id', 'amt', 'status',)
        }),
    )


@admin.register(ConsumeInfo)
class ConsumeInfoAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'order_id', 'ec_id', 'goods_name', 'sender', 'amt', 'status',)
    search_fields = ('userid', 'order_id', 'ec_id',)
    list_filter = ('express_type',)
    readonly_fields = ('user_id', 'id',)
    list_display_links = ('user_id', 'id',)
    fieldsets = (
        (None, {
            'fields': ('id', 'user_id', 'order_id', 'ec_id', 'goods_name', 'express_type', 'express_name', 'amt', 'status')
        }),
        ('发货人信息', {
            'fields': ('sender', 'sender_tel', 'send_prov', 'send_city', 'send_county', 'send_addr', 'sender_postid',)
        }),
        ('收货人信息', {
            'fields': ('receiver', 'receiver_tel', 'receive_prov', 'receive_city', 'receive_county', 'receive_addr', 'receiver_postid',)
        }),
    )


@admin.register(CodeInfo)
class CodeInfoAdmin(admin.ModelAdmin):
    list_display = ('code_type_name', 'code_value_name', 'idx', 'code_group_name',)
    search_fields = ('code_type', 'code_type_name', 'code_value', 'code_value_name',)
    list_filter = ('code_type', 'code_type_name',)
    readonly_fields = ('id',)
    list_display_links = ('code_type_name', 'code_value_name',)
    fieldsets = (
        (None, {
            'fields': ('id', 'code_type', 'code_type_name', 'code_value', 'code_value_name', 'idx', 'code_group', 'code_group_name',)
        }),
    )