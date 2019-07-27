from django.db import models
from django.contrib import messages
import bcrypt
import re
from datetime import datetime, timedelta
# hey Landon!
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
NAME_REGEX = re.compile(r'^[a-zA-Z]+$')
PASSWORD_REGEX_CHECK = '^(?=.*[A-Z])(?=.*\d)'

class UserManager(models.Manager):
    def validate_registration(self, request, postData):
        # First Name Validation
        if len(request.POST["first_name"]) < 2:
            messages.error(request, "First name must be at least 2 characters", extra_tags="first_name")
        if not NAME_REGEX.match(request.POST["first_name"]):
            messages.error(request, "First name must only contain letters", extra_tags="first_name")

        # Last Name Validation
        if len(request.POST["last_name"]) < 2:
            messages.error(request, "Last name must be at least 2 characters", extra_tags="last_name")
        if not NAME_REGEX.match(request.POST["last_name"]):
            messages.error(request, "Last name must only contain letters", extra_tags="last_name")

        # Username Validation
        same_username_list = User.objects.filter(username = request.POST["username"])
        if len(same_username_list) != 0:
            messages.error(request, "Username is already registered", extra_tags="username")
        if len(request.POST["username"]) < 3:
            messages.error(request, "Username must be at least 3 characters long", extra_tags="username")

        # Email Validation
        same_email_list = User.objects.filter(email = request.POST["email"])
        if len(same_email_list) != 0:
            messages.error(request, "Email is already registered", extra_tags="email")
        if not EMAIL_REGEX.match(request.POST["email"]):
            messages.error(request, "Email is not valid", extra_tags="email")

        # Password Validation
        if not re.match(PASSWORD_REGEX_CHECK, request.POST["password"]):
            messages.error(request, "Password must contain one number and one uppercase letter", extra_tags="password")
        if len(request.POST["password"]) < 8:
            messages.error(request, "Password must be at least 8 characters long", extra_tags="password")
        if request.POST["password"] != request.POST["confirm_password"]:
            messages.error(request, "Password and confirm password do not match", extra_tags="password")
        return

    def validate_login(self, request, postData):
        # Username or email in DB validation
        if (len(User.objects.filter(username = postData["email_or_username"])) == 0) and (len(User.objects.filter(email = postData["email_or_username"])) == 0):
            messages.error(request, "Login credentials do not match our database", extra_tags="login")
            return
        else:
            try:
                # In the case that the user entered their email
                logging_in_user = User.objects.get(email = postData["email_or_username"])
                # Password validation
                if not bcrypt.checkpw(postData["password"].encode(), logging_in_user.password.encode()):
                    messages.error(request, "Login credentials do not match our database", extra_tags="login")
                return logging_in_user
            except:
                # In the case that the user entered their username
                logging_in_user = User.objects.get(username = postData["email_or_username"])
                # Password validation
                if not bcrypt.checkpw(postData["password"].encode(), logging_in_user.password.encode()):
                    messages.error(request, "Login credentials do not match our database", extra_tags="login")
                return logging_in_user

class User(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    username = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    balance = models.DecimalField(max_digits=20, decimal_places=2, default = 1000.00)
    net_worth = models.DecimalField(max_digits=20, decimal_places=2, default = 1100.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = UserManager()

class User_Snapshot(models.Model):
    snapshot_number = models.IntegerField(default = 1)
    snapshot_datetime = models.CharField(max_length=255)
    snapshot_balance = models.DecimalField(max_digits=20, decimal_places=2)
    snapshot_net_worth = models.DecimalField(max_digits=20, decimal_places=2)
    snapshot_num_businesses = models.IntegerField(default = 0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, related_name="snapshots")

class Business_Type(models.Model):
    name = models.CharField(max_length=255)
    default_value = models.DecimalField(max_digits=20, decimal_places=2)
    revenue_per_minute = models.DecimalField(max_digits=20, decimal_places=2)
    image_url = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Market(models.Model):
    name = models.CharField(max_length=255)
    started = models.BooleanField(default = False)
    current_multiplier = models.DecimalField(max_digits=20, decimal_places=2, default = 1)
    volatility = models.DecimalField(max_digits=20, decimal_places=2)
    growth_rate = models.DecimalField(max_digits=20, decimal_places=2)
    description = models.TextField()
    color = models.CharField(max_length=255, default = "black")
    num_businesses = models.IntegerField(default = 0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    business_type = models.OneToOneField(Business_Type, related_name = "market")

class Market_Snapshot(models.Model):
    snapshot_number = models.IntegerField(default = 1)
    snapshot_datetime = models.CharField(max_length=255)
    snapshot_multiplier = models.DecimalField(max_digits=20, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    market = models.ForeignKey(Market, related_name="snapshots")

class Business(models.Model):
    name = models.CharField(max_length=255)
    level = models.IntegerField(default = 1)
    bought_for = models.DecimalField(max_digits=20, decimal_places=2)
    # base_value is the value before market multipliers
    base_value = models.DecimalField(max_digits=20, decimal_places=2)
    value = models.DecimalField(max_digits=20, decimal_places=2)
    revenue_per_minute = models.DecimalField(max_digits=20, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, related_name="businesses")
    market = models.ForeignKey(Market, related_name="businesses")
    business_type = models.ForeignKey(Business_Type, related_name="businesses")

class Addon_Type(models.Model):
    name = models.CharField(max_length=255)
    cost = models.DecimalField(max_digits=20, decimal_places=2)
    revenue_per_minute = models.DecimalField(max_digits=20, decimal_places=2)
    image_url = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    business_type = models.ForeignKey(Business_Type, related_name="addon_types")

class Addon(models.Model):
    name = models.CharField(max_length=255)
    revenue_per_minute = models.DecimalField(max_digits=20, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    business = models.ForeignKey(Business, related_name="addons")
    addon_type = models.ForeignKey(Addon_Type, related_name="addons")
