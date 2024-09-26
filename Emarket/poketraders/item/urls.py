from django.urls import path

from . import views

app_name = 'item'

urlpatterns = [
    path('', views.pokemons, name='pokemons'),
    path('new/',views.new, name='new'),
    path('<int:pk>/', views.detail, name='detail'),
    path('<int:pk>/original', views.detail_original, name='detail_original'),
    path('<int:pk>/delete/', views.delete, name='delete'),
    path('<int:pk>/edit/', views.edit, name='edit'),
    path('<int:pk>/buy', views.buy_pokemon, name='buy'),
    path('<int:pk>/upgrade', views.upgrade_rarity, name='upgrade'),
]