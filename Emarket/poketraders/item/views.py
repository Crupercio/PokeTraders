from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Pokemon, Type
from .forms import NewPokemonForm, EditPokemonPriceForm
# Create your views here.

def pokemons(request):
    query = request.GET.get('query','')
    
    selected_types = request.GET.getlist('types')  # Get the list of selected types
    pokemons = Pokemon.objects.filter(is_sold=False, is_tradeable=True)

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
    pokemon = get_object_or_404(Pokemon, pk=pk)
    
    related_pokemons = Pokemon.objects.filter(types__in=pokemon.types.all(), is_sold=False).exclude(pk=pk).distinct()[:6]

    return render(request, 'pokemon/detail.html',{
        'pokemon': pokemon,
        'related_pokemons': related_pokemons,
    })

@login_required
def new(request):
    if request.method == 'POST':
        form = NewPokemonForm(request.POST, request.FILES)

        if form.is_valid():
            pokemon = form.save(commit=False)
            pokemon.owner = request.user
            pokemon.save()
            form.save_m2m()  # This will save the many-to-many relationships (like types)

            return redirect('item:detail',pk=pokemon.id)
    else:
        form = NewPokemonForm()

    return render(request,'pokemon/form.html', {
        'form': form,
        'title': 'New pokemons',
    })

@login_required
def delete(request, pk):
    pokemon = get_object_or_404(Pokemon, pk=pk, owner=request.user)
    pokemon.delete()

    return redirect('dashboard:index')

@login_required
def edit(request, pk):
    pokemon = get_object_or_404(Pokemon, pk=pk, owner=request.user)
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