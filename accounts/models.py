from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True)
    currency = models.CharField(max_length=3, default='USD')
    
    def __str__(self):
        return self.user.username