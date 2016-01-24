from django.db import models


class Game(models.Model):
    created_at = models.DateTimeField()

    def frames(self, player_id=None):
        filters = dict(game=self.id)
        if player_id is not None:
            filters['player'] = player_id

        # Get sorted deliveries
        deliveries = Delivery.objects.filter(**filters).order_by('player', 'frame', 'created_at')

        players_frames = dict()

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
                    elif last_last_frame.get('strike') is True:
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
            elif delivery.frame is 10:  # length 3, take care of last frame edge case
                frame['score'] = frame_sum

        return self.sum_scores(players_frames)

    def sum_scores(self, players_frames):
        # Compound scores
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
    created_at = models.DateTimeField()

    #@classmethod
    #def calculate_scores(self, deliveries):


class GameScore(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    score = models.SmallIntegerField()  # max_length=300
