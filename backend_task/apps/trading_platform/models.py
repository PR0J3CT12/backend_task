from django.db import models
import uuid


class User(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField('user name', max_length=20)

    def __str__(self):
        return str(self.id)


class Trade(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.CharField('trade type', max_length=4)
    symbol = models.CharField('the stock symbol', max_length=4)
    price = models.FloatField('stock price')
    timestamp = models.DateTimeField('transaction time')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.id)
