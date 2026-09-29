from django.db import models
import uuid

# Create your models here.
from django.db import models


class SensorNode(models.Model):
    name = models.CharField(max_length=255)

    node_name = models.CharField(max_length=255)

    year = models.PositiveIntegerField()
    
    node = models.UUIDField(editable=False, unique=True, db_index=True)

    parent = models.UUIDField(blank=True,null=True)


    def __str__(self):
        return self.name


class SpectrumData(models.Model):
    sensor_name = models.CharField(max_length=255)
    
    name = models.CharField(max_length=255)

    year = models.PositiveIntegerField()

    node_id = models.UUIDField(editable=False, unique=True, db_index=True)

    data = models.BinaryField()

class SensorInfo(models.Model):
    sensor_name=models.CharField(max_length=255)
    sensor_type=models.CharField(max_length=255)
    year=models.PositiveIntegerField()
    value=models.FloatField(default=0.0)