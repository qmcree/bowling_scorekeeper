from django.conf.urls import url
from .views import GameView, PlayerDeliveriesView

urlpatterns = [
    url(r'^games/$', GameView.as_view()),
    url(r'^games/(?P<game_id>[0-9]+)/deliveries/$', PlayerDeliveriesView.as_view()),
    url(r'^games/(?P<game_id>[0-9]+)/players/(?P<player_id>[0-9]+)/deliveries/$', PlayerDeliveriesView.as_view()),
]