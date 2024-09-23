from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from .models import Pokemon, Type, PokemonOfUser
from .forms import NewPokemonForm, EditPokemonPriceForm
from django.contrib import messages
# Create your views here.

def pokemons(request):
    query = request.GET.get('query','')
    
    selected_types = request.GET.getlist('types')  # Get the list of selected types
    pokemons = PokemonOfUser.objects.filter(is_sold=False, is_tradeable=True)

    if query:
        pokemons = pokemons.filter(Q(name__icontains=query) | Q(description__icontains=query))

    if selected_types:
        pokemons = pokemons.filter(types__id__in=selected_types).distinct()  # Filter by type and ensure distinct results

    # Fetch all types to display in the dropdown
    all_types = Type.objects.all()


    return render(request, 'pokemon/pokemons.html', {
        'pokemons': pokemons,
        'query':query,
        'selected_types': selected_types,
        'all_types': all_types,
    })

def detail(request, pk):
    pokemon = get_object_or_404(PokemonOfUser, pk=pk)
    
    related_pokemons = PokemonOfUser.objects.filter(types__in=pokemon.types.all(), is_tradeable=True, is_sold=False).exclude(pk=pk).distinct()[:6]

    return render(request, 'pokemon/detail.html',{
        'pokemon': pokemon,
        'related_pokemons': related_pokemons,
    })

@login_required
@user_passes_test(lambda u: u.is_staff)  # This decorator restricts access to admin users
def new(request):
    if request.method == 'POST':
        form = NewPokemonForm(request.POST, request.FILES)

        if form.is_valid():
            pokemon = form.save(commit=False)
            pokemon.owner = request.user
            pokemon.save()
            form.save_m2m()  # This will save the many-to-many relationships (like types)

            return redirect('core:index')
    else:
        form = NewPokemonForm()

    return render(request,'pokemon/form.html', {
        'form': form,
        'title': 'New pokemons',
    })

@login_required
def delete(request, pk):
    pokemon = get_object_or_404(PokemonOfUser, pk=pk, owner=request.user)
    pokemon.delete()

    return redirect('dashboard:index')

@login_required
def edit(request, pk):
    pokemon = get_object_or_404(PokemonOfUser, pk=pk, owner=request.user)
    if request.method == 'POST':
        form = EditPokemonPriceForm(request.POST, request.FILES, instance=pokemon)

        if form.is_valid():
            pokemon.save()
            

            return redirect('item:detail',pk=pokemon.id)
    else:
        form = EditPokemonPriceForm(instance=pokemon)

    return render(request,'pokemon/form.html', {
        'form': form,
        'title': 'Edit pokemons',
    })

@login_required
def buy_pokemon(request, pk):
    pokemon = get_object_or_404(PokemonOfUser, pk=pk)

    # Check if the Pokémon is tradeable and has a price
    if pokemon.price is None or not pokemon.is_tradeable:
        messages.error(request, "This Pokémon is not available for purchase.")
        return redirect('item:detail', pk=pokemon.id)

    # Check if the user has enough Pokepesos
    if request.user.userprofile.pokepeso >= pokemon.price:
        # Deduct Pokepesos from buyer
        request.user.userprofile.pokepeso -= pokemon.price
        request.user.userprofile.save()

        # Transfer ownership
        pokemon.owner = request.user
        pokemon.is_tradeable = False  # Mark as not tradeable after purchase
        pokemon.save()

        # Award experience points to the buyer
        experience_gained = 10  # Fixed 10 XP for every purchase
        request.user.userprofile.add_experience(experience_gained)

        # Award experience points to the Pokémon
        pokemon.add_experience(50)  # Fixed experience for Pokémon

        messages.success(request, f"You have successfully bought {pokemon.name} and gained {experience_gained} experience points!")
        return redirect('dashboard:index')
    else:
        messages.error(request, "You do not have enough Pokepesos to buy this Pokémon.")
        return redirect('item:detail', pk=pokemon.id)



