from django.http import JsonResponse
from django.views.generic import View
from .models import Game


class GameView(View):
    def get(self, *args, **kwargs):
        game = Game.objects.get(id=kwargs.get('game_id'))
        return JsonResponse(game.frames())

    def post(self, *args, **kwargs):
        game = Game()
        game.save()
        return JsonResponse(dict(id=game.id, created_at=game.created_at))


class PlayerDeliveriesView(View):
    def get(self, game_id, player_id):
        pass

    def post(self, game_id, player_id):
        pass