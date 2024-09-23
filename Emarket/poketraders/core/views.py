from django.shortcuts import get_object_or_404
import random
from django.shortcuts import render, redirect
from .models import UserProfile

from item.models import Pokemon, Type

from .forms import SignupForm


# Create your views here.

def index(request):
    pokemons = Pokemon.objects.filter(is_sold=False, is_tradeable=True)[0:150]
    types = Type.objects.all()
    return render(request, 'core/index.html', {
        'types': types,
        'pokemons':pokemons,
    })

def contact(request):
    return render(request, 'core/contact.html')

def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)

        if form.is_valid():
            user = form.save()
            
            # Check if the UserProfile already exists
            user_profile, created = UserProfile.objects.get_or_create(user=user)
            
            if created:
                # Only grant Pokepeso if it's a new profile
                user_profile.pokepeso = 1000
                user_profile.save()

            # Get original Pokémon
            original_pokemons = Pokemon.objects.filter(is_original=True)

            # Select 5 random original Pokémon
            selected_pokemons = random.sample(list(original_pokemons), 5)

            for original_pokemon in selected_pokemons:
                new_pokemon = Pokemon.objects.create(
                    owner=user,
                    name=original_pokemon.name,
                    description=original_pokemon.description,
                    level=1,
                    current_experience=0,
                    is_tradeable=original_pokemon.is_tradeable,
                    is_original=False,
                    image=original_pokemon.image,
                    category=original_pokemon.category,
                    region=original_pokemon.region,
                    generation=original_pokemon.generation
                )

                new_pokemon.types.set(original_pokemon.types.all())

            return redirect('/login/')
    else:
        form = SignupForm()

    return render(request, 'core/signup.html', {
        'form': form,
    })




