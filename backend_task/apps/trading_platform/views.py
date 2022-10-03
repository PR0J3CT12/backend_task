from django.http import HttpResponse
from .models import User, Trade
import json
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.utils import DataError
from django.db.models import Max, Min
from django.views.decorators.http import require_http_methods
from custom_functions import get_variable


@require_http_methods(["DELETE"])
def drop_trades(request):
    Trade.objects.all().delete()
    return HttpResponse(json.dumps({'message': 'Таблица trades успешно очищена.'}, ensure_ascii=False, status=204))


@require_http_methods(["POST"])
def insert_into_trade(request):
    if request.body:
        request_body = json.loads(request.body)
    else:
        return HttpResponse(json.dumps({'message': 'Body запроса пустое.', 'detail': '', 'instance': '/api/insert'}, ensure_ascii=False), status=400)
    try:
        user = User.objects.get(id=request_body["user"])
        if request_body["type"] not in ["sell", "buy"]:
            return HttpResponse(json.dumps({'message': 'В поле type указан неверный тип.', 'detail': 'Необходимо указать "sell" или "buy".', 'instance': '/api/insert'}, ensure_ascii=False), status=400)
        if "timestamp" not in request_body.keys():
            trade = Trade(type=request_body["type"], symbol=request_body["symbol"], price=request_body["price"], timestamp=timezone.now(), user=user)
        else:
            trade = Trade(type=request_body["type"], symbol=request_body["symbol"], price=request_body["price"], timestamp=request_body["timestamp"], user=user)
        trade.save()
        return HttpResponse(json.dumps({'message': 'Данные успешно добавлены в таблицу trades.'}, ensure_ascii=False))
    except ValidationError:
        return HttpResponse(json.dumps({'message': 'Пользователь не существует.', 'detail': '', 'instance': '/api/insert'}, ensure_ascii=False), status=404)
    except ValueError:
        return HttpResponse(json.dumps({'message': 'В поле price указано неверное значение', 'detail': 'Значение должно быть рациональным числом.', 'instance': '/api/insert'}, ensure_ascii=False), status=400)
    except DataError:
        return HttpResponse(json.dumps({'message': 'В поле symbol указано не верное значение.', 'detail': 'Длина введенного символа не должна превышать 4.', 'instance': '/api/insert'}, ensure_ascii=False), status=400)
    except KeyError as e:
        return HttpResponse(json.dumps({'message': f'Не указано поле {e}.', 'detail': '', 'instance': '/api/insert'}, ensure_ascii=False), status=404)


@require_http_methods(["GET"])
def get_everything_from_trades(request):
    try:
        user_id = get_variable('user', request)
        if user_id:
            user = User.objects.get(id=user_id)
            trades_data = list(Trade.objects.filter(user=user))
            result_list = []
            for trade in trades_data:
                trade_json = {"type": trade.type, "user": {"id": str(user.id), "name": user.name}, "symbol": trade.symbol, "price": trade.price, "timestamp": str(trade.timestamp)}
                result_list.append(trade_json)
            return HttpResponse(json.dumps({'trades': result_list}, ensure_ascii=False))
        else:
            trades_data = Trade.objects.all()
            result_list = []
            for trade in trades_data:
                trade_json = {"type": trade.type, "user": {"id": "", "name": ""}, "symbol": trade.symbol, "price": trade.price, "timestamp": str(trade.timestamp)}
                result_list.append(trade_json)
            return HttpResponse(json.dumps({'trades': result_list}, ensure_ascii=False))
    except ValidationError:
        return HttpResponse(json.dumps({'message': 'Пользователь не существует.', 'detail': '', 'instance': '/api/trades'}, ensure_ascii=False), status=404)


@require_http_methods(["GET"])
def max_min_price(request, symbol):
    try:
        start = get_variable('start', request)
        end = get_variable('end', request)
        trades_data_by_symbol = Trade.objects.filter(symbol=symbol)
        if start:
            if end:
                trades_data_filtered = trades_data_by_symbol.filter(timestamp__lte=end, timestamp__gte=start)
            else:
                trades_data_filtered = trades_data_by_symbol.filter(timestamp__gte=start)
        else:
            if end:
                trades_data_filtered = trades_data_by_symbol.filter(timestamp__lte=end)
            else:
                trades_data_filtered = trades_data_by_symbol

        if len(trades_data_by_symbol) == 0:
            return HttpResponse(json.dumps({'message': f'Сделок с символом {symbol} не существует.', 'detail': '', 'instance': request.get_full_path()}, ensure_ascii=False), status=404)
        else:
            if len(trades_data_filtered) == 0:
                return HttpResponse(json.dumps({'message': 'Нет сделок в заданном периоде.', 'detail': '', 'instance': request.get_full_path()}, ensure_ascii=False), status=404)
        max_price = trades_data_filtered.aggregate(Max('price'))["price__max"]
        min_price = trades_data_filtered.aggregate(Min('price'))["price__min"]
        return HttpResponse(json.dumps({'symbol': symbol, 'max': max_price, 'min': min_price}, ensure_ascii=False))
    except ValidationError:
        return HttpResponse(json.dumps({'message': 'В поле start или end указано неверное значение.', 'detail': 'Значение должно удовлетворять datetime формату: YYYY-MM-DD.', 'instance': request.get_full_path()}, ensure_ascii=False), status=400)
