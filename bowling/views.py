from django.http import JsonResponse
from django.views.generic import View
from django.core.validators import ValidationError
from django.db.models.query import IntegrityError
from .models import Game, Delivery
import json


class GameView(View):
    def post(self, *args, **kwargs):
        """Creates new game"""
        game = Game()
        game.save()
        return JsonResponse(dict(id=game.id, created_at=game.created_at))


class PlayerDeliveriesView(View):
    integrity_error = "One or more ID's do not exist."

    def get(self, *args, **kwargs):
        """Calculates scores of one or all players' deliveries"""
        try:
            game = Game.objects.get(id=kwargs['game_id'])
            data = game.calculate_scores(player_id=kwargs.get('player_id'))
        except IntegrityError:
            data = dict(error=self.integrity_error)

        return JsonResponse(data)

    def post(self, *args, **kwargs):
        """Creates delivery (a.k.a. ball, throw, roll)"""
        try:
            delivery = Delivery(game_id=kwargs['game_id'], player_id=kwargs['player_id'])
            data = json.loads(self.request.body.decode('utf-8'))
            delivery.pins_hit = data['pins_hit']
            delivery.save()

            data = delivery.game.calculate_scores(player_id=kwargs['player_id'])
        except KeyError:
            data = dict(error='One or more required parameters are missing.')
        except ValidationError as e:
            data = dict(error=e.message)
        except IntegrityError:
            data = dict(error=self.integrity_error)

        return JsonResponse(data)