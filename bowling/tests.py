from django.test import TestCase
from django.core.validators import ValidationError
from .models import Delivery, Game, Player


class GameTests(TestCase):
    def setUp(self):
        Player(id=1).save()
        Game(id=1).save()
        Delivery(player_id=1, game_id=1, frame=1, pins_hit=1).save()
        Delivery(player_id=1, game_id=1, frame=1, pins_hit=8).save()
        Delivery(player_id=1, game_id=1, frame=2, pins_hit=10).save()
        Delivery(player_id=1, game_id=1, frame=3, pins_hit=4).save()
        Delivery(player_id=1, game_id=1, frame=3, pins_hit=6).save()
        Delivery(player_id=1, game_id=1, frame=4, pins_hit=10).save()
        Delivery(player_id=1, game_id=1, frame=5, pins_hit=1).save()
        Delivery(player_id=1, game_id=1, frame=5, pins_hit=9).save()
        Delivery(player_id=1, game_id=1, frame=6, pins_hit=7).save()
        Delivery(player_id=1, game_id=1, frame=6, pins_hit=3).save()
        Delivery(player_id=1, game_id=1, frame=7, pins_hit=4).save()
        Delivery(player_id=1, game_id=1, frame=7, pins_hit=4).save()
        Delivery(player_id=1, game_id=1, frame=8, pins_hit=10).save()
        Delivery(player_id=1, game_id=1, frame=9, pins_hit=10).save()
        Delivery(player_id=1, game_id=1, frame=10, pins_hit=5).save()
        Delivery(player_id=1, game_id=1, frame=10, pins_hit=5).save()
        Delivery(player_id=1, game_id=1, frame=10, pins_hit=10).save()

    def test_frames_calculation(self):
        expected_scores = {
            1: 9,
            2: 29,
            3: 49,
            4: 69,
            5: 86,
            6: 100,
            7: 108,
            8: 133,
            9: 153,
            10: 173,
        }

        frames = Game(id=1).calculate_scores(player_id=1)

        for player, player_frames in frames.items():
            for frame_number, frame in player_frames.items():
                self.assertEqual(frame['score'], expected_scores[frame_number])

    def test_validation(self):
        try:
            Delivery(game_id=1, player_id=1, pins_hit=5).save()
            self.fail('Delivery saved when game was already completed for player.')
        except ValidationError:
            pass

        # Test that bad pins_hit number is impossible
        try:
            Delivery(game_id=1, player_id=1, pins_hit=11).save()

            self.fail('Pin max is 10')
        except ValidationError:
            pass

        try:
            Delivery.objects.filter(game_id=1, player_id=1, frame=1).delete()
            Delivery(game_id=1, player_id=1, pins_hit=2, frame=1).save()
            Delivery(game_id=1, player_id=1, pins_hit=9, frame=1).save()

            self.fail('Pins hit over max value for frame')
        except ValidationError:
            pass

        # Test that the correct frame is set
        Delivery.objects.filter(game_id=1, player_id=1, frame=10).delete()
        d1 = Delivery(game_id=1, player_id=1, pins_hit=10)
        d2 = Delivery(game_id=1, player_id=1, pins_hit=5)
        d3 = Delivery(game_id=1, player_id=1, pins_hit=5)
        d1.save()
        d2.save()
        d3.save()

        self.assertEqual(d1.frame, 10)
        self.assertEqual(d2.frame, 10)
        self.assertEqual(d3.frame, 10)
