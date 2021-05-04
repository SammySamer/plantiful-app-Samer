from django.db import models
from passlib.hash import pbkdf2_sha256
from django import forms
from django.forms.widgets import DateInput


class users(models.Model):
    id=models.AutoField(primary_key=True)
    first_name = models.TextField(max_length=500)
    last_name = models.TextField(max_length=500)
    email = models.TextField(max_length=500)
    pwd = models.TextField(max_length=500)

    def verify_password(db_pwd, entr_pwd):
        return pbkdf2_sha256.verify(entr_pwd, db_pwd)

    class Meta:
        db_table = "usr"


class user_token(models.Model):
    token = models.TextField(max_length=500)
    invited_email = models.TextField(max_length=500)
    created_at = models.DateTimeField(max_length=500)
    access_type = models.IntegerField()

    class Meta:
        db_table = "user_token"


class user_access(models.Model):
    usr_id = models.IntegerField()
    project_id = models.IntegerField()
    access_type = models.IntegerField()

    class Meta:
        db_table = "user_access"


class project(models.Model):
    project_name = models.TextField(max_length=500)
    start_date = models.DateField()
    end_date = models.DateField()

    class Meta:
        db_table = "project"

class projectForm(forms.ModelForm):
    class Meta:
        model = project
        fields = '__all__'
        widgets = {
            'start_date': DateInput(attrs={'type': 'date'}),
            'end_date': DateInput(attrs={'type': 'date'})
        }

class settings(models.Model):
    number_of_sensor_blocks = models.IntegerField()
    interval_size = models.IntegerField()
    min_temperature = models.FloatField()
    max_temperature = models.FloatField()
    min_humidity = models.FloatField()
    max_humidity = models.FloatField()
    min_moisture = models.FloatField()
    max_moisture = models.FloatField()
    min_ph = models.FloatField()
    max_ph = models.FloatField()
    name = models.TextField(max_length=500)
    id = models.AutoField(primary_key=True)

    class Meta:
        db_table = "settings"


class grp(models.Model):
    project_id = models.IntegerField()
    settings_id = models.IntegerField()
    camera_id = models.TextField()
    id = models.AutoField(primary_key=True)

    class Meta:
        db_table = "grp"


class notification(models.Model):
    usr_id = models.IntegerField()
    project_id = models.IntegerField()
    group_id = models.IntegerField()
    msg = models.TextField()
    created_at = models.DateTimeField()
    if_read = models.BooleanField()

    class Meta:
        db_table = "notification"


class sensor_block(models.Model):
    sensor_block_name = models.TextField()
    group_id = models.IntegerField()

    class Meta:
        db_table = "sensor_block"


class sensor_block_reading(models.Model):
    sensor_block_id = models.IntegerField()
    temperature = models.FloatField()
    moisture = models.FloatField()
    humidity = models.FloatField()
    ph = models.FloatField()
    created_at = models.DateTimeField()

    class Meta:
        db_table = "sensore_block_reading"


class health(models.Model):
    group_id = models.IntegerField()
    health_state = models.TextField()
    created_at = models.DateTimeField()

    class Meta:
        db_table = "health"


class growth(models.Model):
    group_id = models.IntegerField()
    growth_state = models.TextField()
    created_at = models.DateTimeField()

    class Meta:
        db_table = "growth"
