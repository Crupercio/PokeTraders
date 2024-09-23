from django import forms

from .models import Pokemon

INPUT_CLASSES = 'w-full py-4 px-6 rounded-xl border'

class NewPokemonForm(forms.ModelForm):
    class Meta:
        model = Pokemon
        fields = ('category', 'name', 'description', 'types', 'region', 'generation', 'image','price',)
        widgets = {
            'category': forms.Select(attrs={
                'class': INPUT_CLASSES
            }),
             'name': forms.TextInput(attrs={
                'class': INPUT_CLASSES
            }),
             'description': forms.Textarea(attrs={
                'class': INPUT_CLASSES
            }),
             'types': forms.SelectMultiple(attrs={
                'class': INPUT_CLASSES
            }),
             'generation': forms.Select(attrs={
                'class': INPUT_CLASSES
            }),
             'image': forms.FileInput(attrs={
                'class': INPUT_CLASSES
            }),
             'price': forms.TextInput(attrs={
                'class': INPUT_CLASSES
            }),
        }

class EditPokemonPriceForm(forms.ModelForm):
    class Meta:
        model = Pokemon
        fields = ('is_tradeable','price',)
        widgets = {
            'price': forms.TextInput(attrs={
                'class': INPUT_CLASSES
            }),
            
        }
    