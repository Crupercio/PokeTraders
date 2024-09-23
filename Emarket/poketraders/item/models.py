from django.db import models
from django.contrib.auth.models import User


class Type(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Region(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name
    
class Rarity(models.Model):
    name = models.CharField(max_length=100)
    level_cap = models.IntegerField(default=20)  # Level cap for each rarity
    
    

    class Meta:
        ordering = ('name',)
        verbose_name_plural = 'Rarities'

    def __str__(self):
        return self.name

    
    class Meta:
        ordering = ('name',)
        verbose_name_plural = 'Rarities'
    
    def __str__(self):
        return self.name


class Generation(models.Model):
    number = models.IntegerField(unique=True)
    name = models.CharField(max_length=100)

    
    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    class Meta:
        ordering = ('name',)
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

class Pokemon(models.Model):
    is_original = models.BooleanField(default=True)
    category = models.ForeignKey(Category, related_name='original_pokemons', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    rarity = models.ForeignKey(Rarity, related_name='original_pokemons', on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    level = models.IntegerField(default=1)
    current_experience = models.IntegerField(default=0)
    is_tradeable = models.BooleanField(default=True)
    types = models.ManyToManyField(Type, related_name='original_pokemons', blank=True)
    region = models.ForeignKey(Region, related_name='original_pokemons', on_delete=models.SET_NULL, null=True, blank=True)
    generation = models.ForeignKey(Generation, related_name='original_pokemons', on_delete=models.SET_NULL, null=True, blank=True)
    image = models.ImageField(upload_to='pokemon_images', blank=True, null=True)
    price = models.FloatField(blank=True, null=True)
    is_sold = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def add_experience(self, amount):
        if self.level >= 100:
            return
        self.current_experience += amount
        while self.current_experience >= 100 and self.level < 100:
            self.current_experience -= 100
            self.level += 1
        if self.level > 100:
            self.level = 100
            self.current_experience = 0
        self.save()

    def __str__(self):
        return self.name


class PokemonOfUser(models.Model):
    is_original = models.BooleanField(default=True)
    category = models.ForeignKey(Category, related_name='user_pokemons', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    rarity = models.ForeignKey(Rarity, related_name='user_pokemons', on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    level = models.IntegerField(default=1)
    current_experience = models.IntegerField(default=0)
    owner = models.ForeignKey(User, related_name='user_pokemons', on_delete=models.CASCADE)
    is_tradeable = models.BooleanField(default=True)
    types = models.ManyToManyField(Type, related_name='user_pokemons', blank=True)
    region = models.ForeignKey(Region, related_name='user_pokemons', on_delete=models.SET_NULL, null=True, blank=True)
    generation = models.ForeignKey(Generation, related_name='user_pokemons', on_delete=models.SET_NULL, null=True, blank=True)
    image = models.ImageField(upload_to='pokemon_images', blank=True, null=True)
    price = models.FloatField(blank=True, null=True)
    is_sold = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def add_experience(self, amount):
        if self.level >= 100:
            return
        self.current_experience += amount
        while self.current_experience >= 100 and self.level < 100:
            self.current_experience -= 100
            self.level += 1
        if self.level > 100:
            self.level = 100
            self.current_experience = 0
        self.save()

    def __str__(self):
        return self.name
