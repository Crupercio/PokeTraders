from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from item.models import Pokemon

# Create your views here.
@login_required
def index(request):
    pokemons = Pokemon.objects.filter(owner=request.user)

    return render(request, 'dashboard/index.html',{
        'pokemons': pokemons,
    })



