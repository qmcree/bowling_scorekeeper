from django.http import JsonResponse
from django.views.generic import View


class GameView(View):
    def get(self, game_id):
        pass

    def post(self):
        pass


class PlayerDeliveriesView(View):
    def get(self, game_id, player_id):
        pass

    def post(self, game_id, player_id):
        pass