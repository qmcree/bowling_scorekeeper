from django.db import models
from django.db.models import Count, Sum
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.core.validators import ValidationError


class Game(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    def calculate_scores(self, **kwargs):
        """Calculates the score of one or more players' frames"""
        deliveries = kwargs.get('deliveries')

        if deliveries is None:
            deliveries = Delivery.sorted(self.id, kwargs.get('player_id'))

        players_frames = {}

        # Calculate scores for each individual frame
        for delivery in deliveries:
            player_id = delivery.player.id

            # Build data structure if not already built
            try:
                frames = players_frames[player_id]
            except KeyError:
                players_frames[player_id] = {}
                frames = players_frames[player_id]

            try:
                frame = frames[delivery.frame]
            except KeyError:
                frames[delivery.frame] = dict(pins_hit=[], score=0)
                frame = frames[delivery.frame]

            frame['pins_hit'].append(delivery.pins_hit)

            length = len(frame['pins_hit'])
            frame_sum = sum(frame['pins_hit'])

            # If not first frame, try to start scoring last frame if it's un-scored
            if delivery.frame > 1:
                last_frame = players_frames[player_id][delivery.frame - 1]
                last_last_frame = players_frames[player_id][delivery.frame - 2] if delivery.frame > 2 else {}

                # Score last frames with strikes
                if last_frame.get('strike') is True:
                    if length is 2:
                        last_frame['score'] = 10 + frame_sum
                    elif length is 1 and last_last_frame.get('strike') is True:
                        last_last_frame['score'] = 20 + delivery.pins_hit  # Max of 3 strikes to score

                # Score last frame if it was a spare and this is the first delivery
                if last_frame.get('spare') is True and length is 1:
                    last_frame['score'] = 10 + delivery.pins_hit

            if length is 1 and delivery.pins_hit is 10:
                frame['score'] = 0  # can't score yet
                frame['strike'] = True
            elif length is 2:
                if frame_sum < 10:
                    frame['score'] = frame_sum
                else:
                    # Frame 10 can already have a strike in first delivery
                    if frame.get('strike') is not True:
                        frame['spare'] = True

                    frame['score'] = 0  # can't score yet
            elif delivery.frame is 10:  # length 3, take care of tenth frame edge case
                frame['score'] = frame_sum

        return self.__sum_scores(players_frames)

    def __sum_scores(self, players_frames):
        """Calculates and sets the sum of every frame's score."""
        for player, frames in players_frames.items():
            player_score = 0

            for frame_number, frame in frames.items():
                frame['score'] += player_score
                player_score = frame['score']

        return players_frames


class Player(models.Model):
    first_name = models.CharField(max_length=40)


class Delivery(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    frame = models.SmallIntegerField()  # max_length=10
    pins_hit = models.SmallIntegerField(default=0)  # max_length=10
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def sorted(self, game_id=None, player_id=None):
        """Get sorted deliveries"""
        filters = dict(game_id=game_id)
        if player_id is not None:
            filters['player'] = player_id

        return Delivery.objects.filter(**filters).order_by('player', 'frame', 'created_at')


@receiver(pre_save, sender=Delivery)
def set_frame(sender, **kwargs):
    """Validates the delivery and sets the following frame number."""
    instance = kwargs['instance']
    queryset = Delivery.objects.filter(
            game_id=instance.game_id,
            player_id=instance.player_id
    ).values('frame').order_by('-frame').annotate(count=Count('id'), pins=Sum('pins_hit'))[:1]

    try:
        latest = queryset[0]
        if latest['frame'] < 10:
            if latest['count'] is 2 or latest['pins'] is 10:
                instance.frame = latest['frame'] + 1  # 2 deliveries or strike, next frame
            else:
                instance.frame = latest['frame']
        else:
            # No more than 3 possible, which is only allowed if spare.
            if (latest['count'] > 2) or (latest['count'] is 2 and latest['pins'] < 10):
                raise ValidationError("Player's game is complete. No more deliveries allowed.")

            instance.frame = 10  # can still stay in frame 10
    except IndexError or KeyError:
        instance.frame = 1  # this is the first delivery

    if instance.pins_hit > 10:
        raise ValidationError("Pins hit cannot be over 10")

    frame_sum = Delivery.objects.filter(game_id=instance.game_id, player_id=instance.player_id,
                                        frame=instance.frame).aggregate(sum=Sum('pins_hit')).get('sum')

    if frame_sum is not None and instance.frame is not 10 and (frame_sum + instance.pins_hit > 10):
        raise ValidationError("The total number of pins hit for this frame cannot be over 10")
