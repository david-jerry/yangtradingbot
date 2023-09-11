from datetime import datetime, timedelta
from decimal import Decimal

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.urls import reverse

# Create your models here.
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_active') is not True:
            raise ValueError("Superuser must have is_active=True.")
        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(blank=True)
    user_id = models.CharField(max_length=50, unique=True)
    language_choice = models.CharField(max_length=3)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    
    # preferences
    chosen_language = models.CharField(max_length=500, blank=True)
    wallet_address = models.CharField(max_length=500, blank=True)
    wallet_private_key = models.CharField(max_length=500, blank=True)
    wallet_phrase = models.CharField(max_length=500, blank=True)
    wallet_gas = models.DecimalField(max_digits=20, decimal_places=6, default=0.000000)
    
    # offline wallet
    eth_balance = models.DecimalField(max_digits=20, decimal_places=4, default=0.0000)     
    bsc_balance = models.DecimalField(max_digits=20, decimal_places=4, default=0.0000)     
    arp_balance = models.DecimalField(max_digits=20, decimal_places=4, default=0.0000)     
    base_balance = models.DecimalField(max_digits=20, decimal_places=4, default=0.0000)     
    
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    agreed_to_terms = models.BooleanField(default=True)
    
    objects = CustomUserManager()
    
    @property
    def username(self):
        return self.user_id

    def get_full_name(self):
        full_name = f"{self.first_name} {self.last_name}"
        return full_name

    USERNAME_FIELD = 'user_id'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.user_id
