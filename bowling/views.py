from django.http import JsonResponse
from django.views.generic import View
from django.core.validators import ValidationError
from .models import Game, Delivery
import json


class GameView(View):
    def post(self, *args, **kwargs):
        game = Game()
        game.save()
        return JsonResponse(dict(id=game.id, created_at=game.created_at))


class PlayerDeliveriesView(View):
    def get(self, *args, **kwargs):
        game = Game.objects.get(id=kwargs['game_id'])
        return JsonResponse(game.frames(kwargs.get('player_id')))  # @todo confirm player existence if is not None

    def post(self, *args, **kwargs):
        try:
            delivery = Delivery(game_id=kwargs['game_id'], player_id=kwargs['player_id'])  # @todo confirm existence, save hook should validate and determine frame number
            data = json.loads(self.request.body.decode('utf-8'))
            delivery.pins_hit = data['pins_hit']
            delivery.save()

            data = delivery.game.frames(kwargs['player_id'])
        except KeyError:
            data = dict(error='One or more required parameters are missing.')
        except ValidationError as e:
            data = dict(error=e.message)

        return JsonResponse(data)