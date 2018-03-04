from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator

# Create your models here.
class Key_And_Number(models.Model):
    key = models.PositiveIntegerField(primary_key=True,
        unique=True,
        validators=[MinValueValidator(limit_value=0), MaxValueValidator(limit_value=9)])
    phonenumber = models.CharField(null=True,
        max_length=200, 
        validators=[
            RegexValidator(regex="[0-9]?",
                message="Bitte eine gültige Telefonnummer eingeben (00 statt +).",
                code="invalid_phonenumer")
            ])

class Caller_Number_Allowed(models.Model):
    phonenumber = models.CharField(primary_key=True,
    max_length=200, 
        validators=[
            RegexValidator(regex="[0-9]?",
                message="Bitte eine gültige Telefonnummer eingeben (00 statt +).",
                code="invalid_phonenumer")
            ])

class Global_Settings(models.Model):
    key = models.CharField(primary_key=True, max_length=50)
    value = models.CharField(null=True, max_length=200)