from django.db import models
from django.db.models import Count, Sum
from django.core.validators import ValidationError


class Game(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    def calculate_scores(self, **kwargs):
        """
        Calculates scores of each frame for one or all players.
        :param kwargs: deliveries, player_id
        :rtype dict
        """
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
        """
        Calculates and sets the sum of every frame's score.
        :param players_frames:
        :return: Frames with scores summed
        :rtype dict
        """
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
    frame = models.SmallIntegerField()
    pins_hit = models.SmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def validate(self, latest_frame=None):
        """
        Validates the model.
        :param latest_frame: dict or None by default
        :raises ValidationError
        """
        if self.pins_hit > 10:
            raise ValidationError("Pins hit cannot be over 10")

        if latest_frame is not None and latest_frame['frame'] is 10:
            # No more than 3 possible, which is only allowed if spare.
            if latest_frame['count'] > 2 or (latest_frame['count'] is 2 and latest_frame['pins'] < 10):
                raise ValidationError("Player's game is complete. No more deliveries allowed.")

            frame_sum = Delivery.objects.filter(game_id=self.game_id, player_id=self.player_id,
                                                frame=self.frame).aggregate(sum=Sum('pins_hit')).get('sum')

            if frame_sum is not None and self.frame is not 10 and (frame_sum + self.pins_hit > 10):
                raise ValidationError("The total number of pins hit for this frame cannot be over 10")

    @classmethod
    def sorted(cls, game_id=None, player_id=None):
        """
        Gets sorted deliveries.
        :param game_id: Int defaults to None
        :param player_id: Int defaults to None
        :return: Sorted deliveries
        :rtype QuerySet
        """
        filters = dict(game_id=game_id)
        if player_id is not None:
            filters['player'] = player_id

        return Delivery.objects.filter(**filters).order_by('player', 'frame', 'created_at')

    def __get_frame_counts(self):
        """
        Retrieves the most recent frame and the sum of pins hit.
        :rtype QuerySet
        """
        return Delivery.objects.filter(
                game_id=self.game_id,
                player_id=self.player_id
        ).values('frame').order_by('-frame').annotate(
                count=Count('id'),
                pins=Sum('pins_hit')
        )[:1]

    def save(self, *args, **kwargs):
        """
        Validates the delivery, sets the following frame number, then saves the model.
        :param args: See superclass
        :param kwargs: See superclass
        """
        try:
            latest = self.__get_frame_counts()[0]
            self.validate(latest)

            if latest['frame'] < 10:
                if latest['count'] is 2 or latest['pins'] is 10:
                    self.frame = latest['frame'] + 1  # 2 deliveries or strike, next frame
                else:
                    self.frame = latest['frame']
            else:
                self.frame = 10  # can still stay in frame 10
        except IndexError or KeyError:
            self.frame = 1  # this is the first delivery
            self.validate()  # still validate

        super(Delivery, self).save(*args, **kwargs)
