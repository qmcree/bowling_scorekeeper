from django.db import models


class Game(models.Model):
    created_at = models.DateTimeField()


class Player(models.Model):
    first_name = models.CharField(max_length=40)


class Delivery(models.Model):
    player_id = models.ForeignKey(Player, on_delete=models.CASCADE)
    game_id = models.ForeignKey(Game, on_delete=models.CASCADE)
    frame = models.SmallIntegerField() # max_length=10
    pins_hit = models.SmallIntegerField(default=0) # max_length=10
    created_at = models.DateTimeField()


class GameScore(models.Model):
    game_id = models.ForeignKey(Game, on_delete=models.CASCADE)
    player_id = models.ForeignKey(Player, on_delete=models.CASCADE)
    score = models.SmallIntegerField() # max_length=300