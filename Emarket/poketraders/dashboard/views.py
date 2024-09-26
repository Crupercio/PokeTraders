from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from item.models import Pokemon, PokemonOfUser, UserProfile

# Create your views here.
@login_required
def index(request):
    user_profile = UserProfile.objects.get(user=request.user)
    pokemons = PokemonOfUser.objects.filter(owner=user_profile)

    return render(request, 'dashboard/index.html',{
        'pokemons': pokemons,
    })



