
import random
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from item.models import Pokemon
from item.models import Category, Pokemon, Type

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
            
            # Get original Pokémon
            original_pokemons = Pokemon.objects.filter(is_original=True)

            # Select 5 random original Pokémon
            selected_pokemons = random.sample(list(original_pokemons), 5)

            for original_pokemon in selected_pokemons:
                # Create a new Pokémon for the user
                new_pokemon = Pokemon.objects.create(
                    owner=user,
                    name=original_pokemon.name,
                    description=original_pokemon.description,
                    level=1,
                    current_experience=0,
                    is_tradeable=original_pokemon.is_tradeable,
                    is_original=False,  # Mark as non-original
                    image=original_pokemon.image,  # Copy the image from original Pokémon
                    category=original_pokemon.category,  # Set the category
                    region=original_pokemon.region,  # Copy region
                    generation=original_pokemon.generation  # Copy generation
                )

                # Now you can set the types after saving
                new_pokemon.types.set(original_pokemon.types.all())

            return redirect('/login/')
    else:
        form = SignupForm()

    return render(request, 'core/signup.html', {
        'form': form,
    })




