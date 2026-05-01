from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Account(models.Model):
    ACCOUNT_TYPES = [
        ('cash', 'Cash'),
        ('bank', 'Bank Account'),
        ('wallet', 'Digital Wallet'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='accounts')
    name = models.CharField(max_length=100)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES, default='cash')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.user.username}"
    
    class Meta:
        ordering = ['-created_at']

class Category(models.Model):
    CATEGORY_TYPES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=50)
    category_type = models.CharField(max_length=10, choices=CATEGORY_TYPES)
    
    class Meta:
        unique_together = ['user', 'name', 'category_type']
        verbose_name_plural = 'Categories'
    
    def __str__(self):
        return f"{self.name} ({self.category_type})"

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='transactions')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    description = models.TextField(blank=True)
    date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.transaction_type} - {self.amount} - {self.date}"
    
    class Meta:
        ordering = ['-date', '-created_at']
    
    def save(self, *args, **kwargs):
        if self.transaction_type == 'income':
            self.account.balance += self.amount
        else:
            self.account.balance -= self.amount
        self.account.save()
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        if self.transaction_type == 'income':
            self.account.balance -= self.amount
        else:
            self.account.balance += self.amount
        self.account.save()
        super().delete(*args, **kwargs)