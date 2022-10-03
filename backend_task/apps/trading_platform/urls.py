from django.urls import path
from . import views

urlpatterns = [
    path('drop', views.drop_trades, name='drop_trades'),
    path('trades', views.get_everything_from_trades, name='get_everything_from_trades'),
    path('insert', views.insert_into_trade, name='insert_into_trade'),
    path('stock/<str:symbol>/price', views.max_min_price, name='max_min_price'),
    path('init_db', views.init_db, name='init_db')
]