from django.db import models

class Member(models.Model):
    admin_id = models.CharField(max_length=50)
    name = models.CharField(max_length=50)
    email = models.CharField(max_length=80)
    password = models.CharField(max_length=30)
    role = models.CharField(max_length=100)
    registered_time = models.CharField(max_length=50)
    status = models.CharField(max_length=20)


class Rig(models.Model):
    member_id = models.CharField(max_length=11)
    name = models.CharField(max_length=200)
    type = models.CharField(max_length=100)
    pressure_rating = models.CharField(max_length=100)
    specification = models.CharField(max_length=1000)
    contract_period = models.CharField(max_length=100)
    summary = models.CharField(max_length=1000)
    comment = models.CharField(max_length=2000)
    created_date = models.CharField(max_length=50)
    year = models.CharField(max_length=50)
    month = models.CharField(max_length=50)
    version = models.CharField(max_length=50)
    version_text = models.CharField(max_length=100)
    status = models.CharField(max_length=20)


class Well(models.Model):
    rig_id = models.CharField(max_length=11)
    name = models.CharField(max_length=200)
    p10_start_date = models.CharField(max_length=100)
    p10_end_date = models.CharField(max_length=100)
    p10_days_operation = models.CharField(max_length=50)
    p10_status = models.CharField(max_length=50)
    p50_start_date = models.CharField(max_length=100)
    p50_end_date = models.CharField(max_length=100)
    p50_days_operation = models.CharField(max_length=50)
    p50_status = models.CharField(max_length=50)
    p90_start_date = models.CharField(max_length=100)
    p90_end_date = models.CharField(max_length=100)
    p90_days_operation = models.CharField(max_length=50)
    p90_status = models.CharField(max_length=50)
    license = models.CharField(max_length=100)
    field = models.CharField(max_length=100)
    well_type = models.CharField(max_length=100)
    well_status = models.CharField(max_length=100)
    info = models.CharField(max_length=5000)
    status = models.CharField(max_length=20)



class Version(models.Model):
    member_id = models.CharField(max_length=11)
    year = models.CharField(max_length=50)
    month = models.CharField(max_length=50)
    version = models.CharField(max_length=50)
    version_name = models.CharField(max_length=100)
    data = models.CharField(max_length=100000)
    created_date = models.CharField(max_length=50)
    status = models.CharField(max_length=20)























































