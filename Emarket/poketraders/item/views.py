from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from .models import Pokemon, Type, PokemonOfUser, Rarity
from  core.models import UserProfile
from .forms import NewPokemonForm, EditPokemonPriceForm
from django.contrib import messages
from django.db import transaction  
from django.utils import timezone
import random
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
    can_upgrade = False  # Default value
    if request.user.is_authenticated:
        user_profile = UserProfile.objects.get(user=request.user)
        can_upgrade = pokemon.can_upgrade(user_profile)  # Check upgrade eligibility
        # Debugging output
        print(f"User Tokens: {user_profile.fire_tokens}, Required Tokens: {pokemon.get_next_rarity_tokens()}, Can Upgrade: {can_upgrade}")


    return render(request, 'pokemon/detail.html', {
        'pokemon': pokemon,
        'related_pokemons': related_pokemons,
        'user_profile': user_profile,
        'can_upgrade': can_upgrade,  # Pass the flag to the template
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
def claim_pokemon(request):
    user_profile = request.user.userprofile

    if not user_profile.can_claim():
        messages.error(request, "You can only claim a new Pokémon once every 24 hours.")
        return redirect('dashboard:index')

    # Get all original Pokémon
    original_pokemons = Pokemon.objects.filter(is_original=True)

    # Check if there are any original Pokémon to choose from
    if not original_pokemons.exists():
        messages.error(request, "No original Pokémon available for claim.")
        return redirect('dashboard:index')

    # Select a random original Pokémon
    selected_pokemon = random.choice(original_pokemons)

    # Create a new Pokémon instance
    new_pokemon = PokemonOfUser.objects.create(
        owner=user_profile,
        name=selected_pokemon.name,
        description=selected_pokemon.description,
        level=1,
        current_experience=0,
        is_tradeable=selected_pokemon.is_tradeable,
        is_original=False,
        image=selected_pokemon.image,
        category=selected_pokemon.category,  # Ensure category is valid
        region=selected_pokemon.region,
        generation=selected_pokemon.generation,
        rarity=selected_pokemon.rarity
    )

    # Set the types for the new Pokémon
    new_pokemon.types.set(selected_pokemon.types.all())

    # Update last claimed time
    user_profile.last_claimed = timezone.now()
    user_profile.save()

    messages.success(request, f"You have successfully claimed a new Pokémon: {new_pokemon.name}!")
    return redirect('dashboard:index')

@login_required
def claim_pokepesos(request):
    user_profile = request.user.userprofile

    # Check if the user can claim Pokepesos
    if not user_profile.can_claim_pokepesos():
        messages.error(request, "You can only claim Pokepesos once every 2 hours.")
        return redirect('dashboard:index')

    # Define the amount of Pokepesos to claim
    amount_to_claim = 100  # Adjust the amount as needed

    # Update the user's Pokepesos
    user_profile.pokepeso += amount_to_claim
    user_profile.last_claimed_pokepesos = timezone.now()  # Track last claim time
    user_profile.save()

    messages.success(request, f"You have successfully claimed {amount_to_claim} Pokepesos!")
    return redirect('dashboard:index')

@login_required
def free(request, pk):
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
    type_count = pokemon_types.count()  # Count the number of types

    # Determine the rarity of the Pokémon
    rarity = pokemon.rarity  # Assuming the Pokemon model has a field for rarity

    # Check rarity and award tokens accordingly
    if rarity:
        if rarity.name == 'Common':
            # Award 1 token for each type if the rarity is Common
            tokens_awarded = 1 
        elif rarity.name in ['Uncommon', 'Rare', 'Epic', 'Ultra']:
            # Award 1/4 of the level cap in tokens for each type
            if rarity.name == "Uncommon":
                tokens_awarded = rarity.level_cap / 4 / type_count
            elif rarity.name == "Rare":
                tokens_awarded = rarity.level_cap / 2 / type_count
            elif rarity.name == "Epic":
                tokens_awarded = rarity.level_cap / 1 / type_count
            elif rarity.name == "Ultra":
                tokens_awarded = (rarity.level_cap / 2 / type_count) + random.randint(1,30)

            
        else:
            tokens_awarded = 0  # For any other rarity, no tokens awarded

        # Update the user's token count based on the Pokémon's type(s)
        for pokemon_type in pokemon_types:
            if pokemon_type.name == 'Fire':
                user_profile.fire_tokens += tokens_awarded
            elif pokemon_type.name == 'Water':
                user_profile.water_tokens += tokens_awarded
            elif pokemon_type.name == 'Grass':
                user_profile.grass_tokens += tokens_awarded
            elif pokemon_type.name == 'Electric':
                user_profile.electric_tokens += tokens_awarded
            elif pokemon_type.name == 'Ice':
                user_profile.ice_tokens += tokens_awarded
            elif pokemon_type.name == 'Fighting':
                user_profile.fighting_tokens += tokens_awarded
            elif pokemon_type.name == 'Poison':
                user_profile.poison_tokens += tokens_awarded
            elif pokemon_type.name == 'Ground':
                user_profile.ground_tokens += tokens_awarded
            elif pokemon_type.name == 'Flying':
                user_profile.flying_tokens += tokens_awarded
            elif pokemon_type.name == 'Psychic':
                user_profile.psychic_tokens += tokens_awarded
            elif pokemon_type.name == 'Bug':
                user_profile.bug_tokens += tokens_awarded
            elif pokemon_type.name == 'Rock':
                user_profile.rock_tokens += tokens_awarded
            elif pokemon_type.name == 'Ghost':
                user_profile.ghost_tokens += tokens_awarded
            elif pokemon_type.name == 'Dragon':
                user_profile.dragon_tokens += tokens_awarded
            elif pokemon_type.name == 'Dark':
                user_profile.dark_tokens += tokens_awarded
            elif pokemon_type.name == 'Fairy':
                user_profile.fairy_tokens += tokens_awarded
            elif pokemon_type.name == 'Steel':
                user_profile.steel_tokens += tokens_awarded
            elif pokemon_type.name == 'Normal':
                user_profile.normal_tokens += tokens_awarded

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
    # Fetch the Pokémon
    pokemon = get_object_or_404(PokemonOfUser, pk=pk)

    # Check if the Pokémon is tradeable and has a price
    if not is_tradeable(pokemon):
        messages.error(request, "This Pokémon is not available for purchase.")
        return redirect('item:detail', pk=pokemon.id)

    # Check if the user has enough Pokepesos
    buyer_profile = request.user.userprofile
    if buyer_profile.pokepeso < pokemon.price:
        messages.error(request, "You do not have enough Pokepesos to buy this Pokémon.")
        return redirect('item:detail', pk=pokemon.id)

    seller_profile = pokemon.owner  # Get the current owner (seller)

    with transaction.atomic():
        # Deduct Pokepesos from buyer
        buyer_profile.pokepeso -= pokemon.price
        buyer_profile.save()

        # Transfer Pokepesos to seller
        seller_profile.pokepeso += pokemon.price
        seller_profile.save()

        # Transfer ownership of the Pokémon
        pokemon.owner = buyer_profile
        pokemon.is_tradeable = False  # Mark as not tradeable after purchase
        pokemon.save()

        # Award experience points
        award_experience(buyer_profile, 10)  # Fixed 10 XP for the buyer
        pokemon.add_experience(10)  # Fixed experience for Pokémon

        messages.success(request, f"You have successfully bought {pokemon.name}!")
    
    return redirect('dashboard:index')


def is_tradeable(pokemon):
    """Check if the Pokémon is tradeable and has a valid price."""
    return pokemon.is_tradeable and pokemon.price is not None


def award_experience(user_profile, amount):
    """Award experience points to a user profile."""
    user_profile.add_experience(amount)

  
@login_required    
def upgrade_rarity(request, pk):
    pokemon = get_object_or_404(PokemonOfUser, pk=pk)

    if pokemon.owner != request.user.userprofile:
        messages.error(request, "You can only upgrade your own Pokémon.")
        return redirect('dashboard:index')

    user_profile = request.user.userprofile

    # Check if the user can upgrade the Pokémon
    if not pokemon.can_upgrade(user_profile):
        messages.error(request, "You do not have enough tokens to upgrade this Pokémon.")
        return redirect('dashboard:index')

    # Proceed with the upgrade since the user has enough tokens
    if pokemon.rarity.name == 'Common':
        next_rarity = Rarity.objects.get(name='Uncommon')
    elif pokemon.rarity.name == 'Uncommon':
        next_rarity = Rarity.objects.get(name='Rare')
    elif pokemon.rarity.name == 'Rare':
        next_rarity = Rarity.objects.get(name='Epic')
    elif pokemon.rarity.name == 'Epic':
        next_rarity = Rarity.objects.get(name='Ultra')
    else:
        messages.error(request, "You have reached the Pokémon's max rarity.")
        return redirect('dashboard:index')

    # Deduct the required tokens after confirming the upgrade
    required_tokens = pokemon.get_next_rarity_tokens()
    pokemon_type = pokemon.types.first()
    token_attribute = f"{pokemon_type.name.lower()}_tokens"
    
    # Deduct tokens
    current_tokens = getattr(user_profile, token_attribute)
    setattr(user_profile, token_attribute, current_tokens - required_tokens)

    # Upgrade the Pokémon's rarity
    pokemon.rarity = next_rarity
    pokemon.save()
    user_profile.save()

    messages.success(request, f"You have successfully upgraded {pokemon.name} to {next_rarity.name} rarity!")
    return redirect('dashboard:index')





