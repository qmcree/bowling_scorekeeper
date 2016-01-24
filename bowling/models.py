from django.db import models


class Game(models.Model):
    created_at = models.DateTimeField()

    def frames(self, player_id=None):
        # @todo throw exception for undefined or ID null
        filters = dict(game_id=self.id)
        if player_id is not None:
            filters['player_id'] = player_id

        # Get sorted deliveries
        deliveries = Delivery.objects.filter(**filters).order_by('player_id', 'frame', 'created_at')

        players_frames = dict()

        # Calculate scores for each individual frame
        for delivery in deliveries:
            player_id = delivery.player_id
            frame = players_frames[player_id][delivery.frame]
            frame['pins_hit'].append(delivery.pins_hit)

            length = len(frame['pins_hit'])
            frame_sum = sum(frame['pins_hit'])

            if length is 1 and delivery.pins_hit is 10:
                frame['score'] = 0  # can't score yet
                frame['strike'] = True
            elif length is 2:
                if frame_sum < 10:
                    frame['score'] = frame_sum
                else:
                    frame['score'] = 0  # can't score yet
                    frame['spare'] = True

            # If not first frame, try to start scoring last frame if it's un-scored
            if frame > 1:
                last_frame = players_frames[player_id][delivery.frame - 1]
                last_last_frame = players_frames[player_id][delivery.frame - 2] if frame > 2 else None

                # Score last frames with strikes
                if last_frame.strike:
                    if length == 2:
                        last_frame.score = 10 + frame_sum
                    elif last_last_frame is not None and last_last_frame.strike:
                        last_last_frame.score = 30  # Max of 3 strikes to score

                # Score last frame if it was a spare and this is the first delivery
                if last_frame.spare and length == 1:
                    last_frame.score = 10 + delivery.pins_hit

            # Last frame case
            if frame == 10:
                pass

        return players_frames
        # Compound scores
        #for player_frames in players_frames:
            #for frame in player_frames:



class Player(models.Model):
    first_name = models.CharField(max_length=40)


class Delivery(models.Model):
    player_id = models.ForeignKey(Player, on_delete=models.CASCADE)
    game_id = models.ForeignKey(Game, on_delete=models.CASCADE)
    frame = models.SmallIntegerField()  # max_length=10
    pins_hit = models.SmallIntegerField(default=0)  # max_length=10
    created_at = models.DateTimeField()

    #@classmethod
    #def calculate_scores(self, deliveries):


class GameScore(models.Model):
    game_id = models.ForeignKey(Game, on_delete=models.CASCADE)
    player_id = models.ForeignKey(Player, on_delete=models.CASCADE)
    score = models.SmallIntegerField()  # max_length=300
