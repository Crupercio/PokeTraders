from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from .models import Pokemon, Type, PokemonOfUser, Rarity
from  core.models import UserProfile
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

    related_pokemons = PokemonOfUser.objects.filter(
        types__in=pokemon.types.all(), 
        is_tradeable=True, 
        is_sold=False
    ).exclude(pk=pk).distinct()[:6]

    user_profile = None
    if request.user.is_authenticated:
        try:
            user_profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            user_profile = None  # Handle the case where the user has no profile

    return render(request, 'pokemon/detail.html', {
        'pokemon': pokemon,
        'related_pokemons': related_pokemons,
        'user_profile': user_profile,
    })


@login_required
@user_passes_test(lambda u: u.is_staff)  # This decorator restricts access to admin users
def detail_original(request, pk):
    pokemon = get_object_or_404(Pokemon, pk=pk)
    types = pokemon.types.all()  # Assuming a ManyToMany or ForeignKey relationship exists
    related_pokemons = Pokemon.objects.filter(types__in=pokemon.types.all()).exclude(pk=pk).distinct()[:150]

    return render(request, 'pokemon/detail_original.html',{
        'pokemon': pokemon,
        'related_pokemons': related_pokemons,
        'types': types,  # Make sure types are passed here
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
    # Ensure the Pokémon belongs to the logged-in user
    pokemon = get_object_or_404(PokemonOfUser, pk=pk, owner=request.user.userprofile)

    # Attempt to get the UserProfile
    try:
        user_profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        messages.error(request, "User profile does not exist.")
        return redirect('dashboard:index')

    # Get the types of the Pokémon
    pokemon_types = pokemon.types.all()

    # Update the user's token count based on the Pokémon's type(s)
    for pokemon_type in pokemon_types:
        if pokemon_type.name == 'Fire':
            user_profile.fire_tokens += 1
        elif pokemon_type.name == 'Water':
            user_profile.water_tokens += 1
        elif pokemon_type.name == 'Grass':
            user_profile.grass_tokens += 1
        elif pokemon_type.name == 'Electric':
            user_profile.electric_tokens += 1
        elif pokemon_type.name == 'Ice':
            user_profile.ice_tokens += 1
        elif pokemon_type.name == 'Fighting':
            user_profile.fighting_tokens += 1
        elif pokemon_type.name == 'Poison':
            user_profile.poison_tokens += 1
        elif pokemon_type.name == 'Ground':
            user_profile.ground_tokens += 1
        elif pokemon_type.name == 'Flying':
            user_profile.flying_tokens += 1
        elif pokemon_type.name == 'Psychic':
            user_profile.psychic_tokens += 1
        elif pokemon_type.name == 'Bug':
            user_profile.bug_tokens += 1
        elif pokemon_type.name == 'Rock':
            user_profile.rock_tokens += 1
        elif pokemon_type.name == 'Ghost':
            user_profile.ghost_tokens += 1
        elif pokemon_type.name == 'Dragon':
            user_profile.dragon_tokens += 1
        elif pokemon_type.name == 'Dark':
            user_profile.dark_tokens += 1
        elif pokemon_type.name == 'Fairy':
            user_profile.fairy_tokens += 1
        elif pokemon_type.name == 'Steel':
            user_profile.steel_tokens += 1
        elif pokemon_type.name == 'Normal':
            user_profile.normal_tokens += 1

    # Save the updated UserProfile
    user_profile.save()

    # Delete the Pokémon
    pokemon.delete()

    return redirect('dashboard:index')




@login_required
def edit(request, pk):
    pokemon = get_object_or_404(PokemonOfUser, pk=pk, owner=request.user.userprofile)
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
        pokemon.owner = request.user.userprofile
        pokemon.is_tradeable = False  # Mark as not tradeable after purchase
        pokemon.save()

        # Award experience points to the buyer
        experience_gained = 10  # Fixed 10 XP for every purchase
        request.user.userprofile.add_experience(experience_gained)

        # Award experience points to the Pokémon
        pokemon.add_experience(500)  # Fixed experience for Pokémon

        messages.success(request, f"You have successfully bought {pokemon.name} and gained {experience_gained} experience points!")
        return redirect('dashboard:index')
    else:
        messages.error(request, "You do not have enough Pokepesos to buy this Pokémon.")
        return redirect('item:detail', pk=pokemon.id)

@login_required    
def upgrade_rarity(request, pk):
    pokemon = get_object_or_404(PokemonOfUser, pk=pk)

    if pokemon.owner != request.user:
        messages.error(request, "You can only upgrade your own Pokémon.")
        return redirect('dashboard:index')

    required_tokens = 10  # Example required tokens for rarity upgrade
    user_profile = request.user.userprofile

    # Check token requirements based on Pokémon's rarity and type
    if pokemon.rarity.name == 'Common':
        pokemon.rarity = Rarity.objects.get(name='Uncommon')
            
    elif pokemon.rarity.name == 'Uncommon':
        pokemon.rarity = Rarity.objects.get(name='Rare')
        
    elif pokemon.rarity.name == 'Rare':
        pokemon.rarity = Rarity.objects.get(name='Epic')
    elif pokemon.rarity.name == 'Epic':
        pokemon.rarity = Rarity.objects.get(name='Ultra')        

    else:
        messages.error(request, "You have reached the Pokémon's max rarity.")
        return redirect('dashboard:index')

    
    pokemon.save()
    user_profile.save()

    messages.success(request, f"You have successfully upgraded {pokemon.name} to {pokemon.next_rarity.name} rarity!")
    return redirect('dashboard:index')




