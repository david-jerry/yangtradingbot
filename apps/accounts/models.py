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
    FAST = "FAST"
    SLOW = "SLOW"
    AVERAGE = "AVERAGE"
    MAX_SPEED = "MAX_SPEED"
    PRESETS = (
        (FAST, FAST),
        (SLOW, SLOW),
        (AVERAGE, AVERAGE),
        (MAX_SPEED, MAX_SPEED),
    )
    email = models.EmailField(blank=True, null=True)
    user_id = models.CharField(max_length=50, unique=True)
    language_choice = models.CharField(max_length=3)
    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    
    # preferences
    chosen_language = models.CharField(max_length=500, blank=True, null=True)
    wallet_address = models.CharField(max_length=500, blank=True, null=True)
    wallet_private_key = models.CharField(max_length=1000, blank=True, null=True)
    wallet_phrase = models.CharField(max_length=1000, blank=True, null=True)
    wallet_gas = models.DecimalField(max_digits=20, decimal_places=6, default=0.000000)
    
    # offline wallet
    eth_balance = models.DecimalField(max_digits=20, decimal_places=4, default=0.0000)     
    bsc_balance = models.DecimalField(max_digits=20, decimal_places=4, default=0.0000)     
    arp_balance = models.DecimalField(max_digits=20, decimal_places=4, default=0.0000)     
    base_balance = models.DecimalField(max_digits=20, decimal_places=4, default=0.0000) 
    
    eth_preset = models.CharField(max_length=15, blank=False, default=AVERAGE, choices=PRESETS)
    bsc_preset = models.CharField(max_length=15, blank=False, default=AVERAGE, choices=PRESETS)
    arp_preset = models.CharField(max_length=15, blank=False, default=AVERAGE, choices=PRESETS)
    base_preset = models.CharField(max_length=15, blank=False, default=AVERAGE, choices=PRESETS)
        
    BSC_added = models.BooleanField(default=False)
    ARB_added = models.BooleanField(default=False)
    BASE_added = models.BooleanField(default=False)
    
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    agreed_to_terms = models.BooleanField(default=True)
    
    max_gas = models.DecimalField(default=0.00, decimal_places=2, max_digits=20)
    max_gas_price = models.DecimalField(default=0.00, decimal_places=2, max_digits=20)
    max_delta = models.DecimalField(default=0.00, decimal_places=2, max_digits=20)
    slippage = models.DecimalField(default=20.00, decimal_places=2, max_digits=20)
    
    buy_tax = models.DecimalField(default=0.00, decimal_places=2, max_digits=20)
    sell_tax = models.DecimalField(default=0.00, decimal_places=2, max_digits=20)
    
    sell_hi = models.DecimalField(default=2.0, decimal_places=2, max_digits=20)
    sell_lo = models.DecimalField(default=0.5, decimal_places=2, max_digits=20)
    sell_hi_amount = models.DecimalField(default=20.00, decimal_places=2, max_digits=20)
    sell_lo_amount = models.DecimalField(default=0.20, decimal_places=2, max_digits=20)
    
    auto_sell = models.BooleanField(default=False)
    dupe_buy = models.BooleanField(default=False)
    auto_buy = models.BooleanField(default=False)
    auto_approve = models.BooleanField(default=False)
    
    objects = CustomUserManager()
    
    @property
    def username(self):
        return self.user_id

    def get_full_name(self):
        full_name = f"{self.first_name} {self.last_name}"
        return full_name
    
    @property
    def snipes(self):
        if self.sniper.exists():
            return self.sniper.all()
        return None

    USERNAME_FIELD = 'user_id'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    def __str__(self):
        return self.user_id

class Sniper(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="sniper", blank=True)
    chain = models.CharField(max_length=5, blank=True)
    name = models.CharField(max_length=255, blank=True)
    symbol = models.CharField(max_length=255, blank=True)
    decimal = models.IntegerField(default=18)
    contract_address = models.CharField(max_length=500, blank=True)
    
    auto = models.BooleanField(default=False)
    method = models.BooleanField(default=False)
    liquidity = models.BooleanField(default=False)
    
    block_delay = models.DecimalField(max_digits=12, decimal_places=6, default=0)
    
    eth = models.DecimalField(max_digits=12, decimal_places=6, default=1)
    token = models.DecimalField(max_digits=12, decimal_places=6, default=10)
    
    multi = models.BooleanField(default=False)
    buy = models.BooleanField(default=True)
    enable = models.BooleanField(default=True)
    stop = models.BooleanField(default=False)
    approve = models.BooleanField(default=True)
    auto_sell = models.BooleanField(default=True)
    buy_dip = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.user_id} {self.contract_address} Snipe"


class CopyTradeAddresses(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="copy_trades", blank=True)
    chain = models.CharField(max_length=5, blank=True)
    name = models.CharField(max_length=250, blank=True)
    contract_address = models.CharField(max_length=500, blank=True)
    on = models.BooleanField(default=False)
    
    multi = models.BooleanField(default=False)
    auto_buy = models.BooleanField(default=False)
    copy_sell = models.BooleanField(default=False)
    smart_slippage = models.BooleanField(default=True)
    
    amount = models.DecimalField(decimal_places=6, max_digits=20, default=0.000000)
    slippage = models.DecimalField(decimal_places=6, max_digits=20, default=0.000000)
    gas_delta = models.DecimalField(decimal_places=6, max_digits=20, default=0.000000)
    sell_hi_amount = models.DecimalField(decimal_places=6, max_digits=20, default=0.000000)
    sell_lo_amount = models.DecimalField(decimal_places=6, max_digits=20, default=0.000000)
    sell_hi = models.DecimalField(decimal_places=6, max_digits=20, default=0.000000)
    sell_lo = models.DecimalField(decimal_places=6, max_digits=20, default=0.000000)
    max_buy_tax = models.DecimalField(decimal_places=6, max_digits=20, default=0.000000)
    max_sell_tax = models.DecimalField(decimal_places=6, max_digits=20, default=0.000000)
    
    
    def __str__(self):
        return f"{self.user.user_id} {self.contract_address}"
    
    
class Txhash(models.Model):
        Txhash = models.CharField(max_length=500, blank=True)
        user_id = models.CharField(max_length=500, blank=True)
        check_txhash = models.BooleanField(default=False)
        def str(self):
            return f"{self.Txhash}{self.user_id}{self.check_txhash}"
        
class copytradetxhash(models.Model):
        user_id = models.CharField(max_length=500, blank=True)
        txhash = models.CharField(max_length=500, blank=True)
        bot_name = models.CharField(max_length=500, blank=True)
        amount = models.DecimalField(decimal_places=6, max_digits=20, default=0.000000)
        token_address = models.CharField(max_length=500, blank=True)
        def __str__(self):
            return f"{self.user_id} {self.txhash} {self.bot_name} {self.amount}{self.token_address}"

class tradetxhash(models.Model):
        user_id = models.CharField(max_length=500, blank=True)
        txhash = models.CharField(max_length=500, blank=True)
        bot_name = models.CharField(max_length=500, blank=True)
        amount = models.DecimalField(decimal_places=6, max_digits=20, default=0.000000)
        token_address = models.CharField(max_length=500, blank=True)
        def __str__(self):
            return f"{self.user_id} {self.txhash} {self.bot_name} {self.amount}{self.token_address}"
        
class TradeAddress(models.Model):
        user = models.CharField(max_length=500, blank=True)
        token_address = models.CharField(max_length=500, blank=True)
        token_name = models.CharField(max_length=500, blank=True)
        chain = models.CharField(max_length=500, blank=True)

        limit = models.DecimalField(decimal_places=10, max_digits=20, default=0.0000000000)
        check_limit = models.BooleanField(default=False)

        #The value which is user want to sell when the token price is higher than the profit 
        profit = models.DecimalField(decimal_places=10, max_digits=20, default=0.0000000000) 
        check_profit = models.BooleanField(default=False)

        stop_loss = models.DecimalField(decimal_places=10, max_digits=20, default=0.0000000000)
        check_stop_loss = models.BooleanField(default=False)

        gas_delta = models.DecimalField(decimal_places=6, max_digits=20, default=0.000000)
        slippage = models.DecimalField(decimal_places=6, max_digits=20, default=0.000000)
        ammount_limit = models.DecimalField(decimal_places=6, max_digits=20, default=0.000000)

        def __str__(self):
            return f"{self.user} {self.token_address} {self.token_name} {self.chain}"


