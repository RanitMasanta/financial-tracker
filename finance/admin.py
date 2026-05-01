from django.contrib import admin
from .models import Account, Category, Transaction

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'account_type', 'balance']
    list_filter = ['account_type', 'user']
    search_fields = ['name', 'user__username']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category_type', 'user']
    list_filter = ['category_type', 'user']
    search_fields = ['name']

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['date', 'transaction_type', 'category', 'amount', 'user']
    list_filter = ['transaction_type', 'date', 'user']
    search_fields = ['description', 'user__username']
    date_hierarchy = 'date'