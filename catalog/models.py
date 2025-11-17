from django.db import models

class AdvUser(AbstractUser):

email = models.EmailField(unique=True, null=False, verbose_name='Email адрес')
patronymic = models.CharField(max_length=200)

def __str__(self):
    return self.get_full_name()

class Meta:
    permissions = (("moderator_access", "Доступ модератора"),)