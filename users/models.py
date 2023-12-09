from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.utils.translation import gettext_lazy as _
import random
import datetime


# Create your models here.
def generate_code(is_admin=False):
    if not is_admin:
        zero_sequence = ''.join(["0" for _ in range(6)])
        code = "#" + ("%s%s" % (zero_sequence, random.randint(0, 999999)))[-6:]
        while User.objects.filter(code=code, is_staff=False, is_active=True).count():
            code = "#" + ("%s%s" % (zero_sequence, random.randint(0, 999999)))[-6:]
    else:
        zero_sequence = ''.join(["0" for _ in range(11)])
        code = "##" + ("%s%s" % (zero_sequence, User.objects.filter(is_admin=True).count() + 1))[-6:]

    return code


class UserManager(BaseUserManager):
    def create_user(self, email, name, password=None):
        """
        Creates and saves a User with the given email, name ,password and code.
        """
        if not email:
            raise ValueError("Users must have an email address")

        if not name:
            raise ValueError("Users must have a name")

        user = self.model(
            email=self.normalize_email(email),
            name=name,
            code=generate_code(),
            created_on=datetime.datetime.now(datetime.timezone.utc),
            updated_on=datetime.datetime.now(datetime.timezone.utc),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None):
        """
        Creates and saves a superuser with the given email, name ,password and code.
        """
        user = self.create_user(
            email=email,
            name=name,
            password=password,
        )

        user.code = generate_code(is_admin=True)
        user.is_staff = True
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    name = models.CharField(_('Họ và tên'), max_length=255, )
    code = models.CharField(_('code'), max_length=255, unique=True, )
    email = models.EmailField(_('email'), max_length=255, unique=True, )
    created_on = models.DateTimeField(_('created on'))
    updated_on = models.DateTimeField(_('updated on'))

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        """Does the user have a specific permission?
        Simplest possible answer: Yes, always"""
        return True

    def has_module_perms(self, app_label):
        """Does the user have permissions to view the app `app_label`?
        Simplest possible answer: Yes, always"""
        return True
