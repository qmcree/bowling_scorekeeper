from django.http import JsonResponse
from django.views.generic import View
from .models import Game


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
        pass