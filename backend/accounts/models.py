from django.db import models
from django.contrib.auth.models import AbstractUser #using this we can use django's inbuild user modules
from django.db import models


class User(AbstractUser):

    ROLE_CHOICES = (
        ("user", "User"), #how store and displayed
        ("trainer", "Trainer"),
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES, #give role choice default will be user not trainer
        default="user"
    )
