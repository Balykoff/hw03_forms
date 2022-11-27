from django.db import models
from django.contrib.auth import get_user_model
# Create your models here.
User = get_user_model


class Creation(models.Model):
   first_name = models.TextField()
   last_name = models.TextField()
   username = models.TextField()
   email = models.EmailField()