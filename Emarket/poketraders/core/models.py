from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    pokepeso = models.IntegerField(default=1000)
       # Token fields for each Pokémon type
    fire_tokens = models.IntegerField(default=0)
    water_tokens = models.IntegerField(default=0)
    grass_tokens = models.IntegerField(default=0)
    electric_tokens = models.IntegerField(default=0)
    ice_tokens = models.IntegerField(default=0)
    fighting_tokens = models.IntegerField(default=0)
    poison_tokens = models.IntegerField(default=0)
    ground_tokens = models.IntegerField(default=0)
    flying_tokens = models.IntegerField(default=0)
    psychic_tokens = models.IntegerField(default=0)
    bug_tokens = models.IntegerField(default=0)
    rock_tokens = models.IntegerField(default=0)
    ghost_tokens = models.IntegerField(default=0)
    dragon_tokens = models.IntegerField(default=0)
    dark_tokens = models.IntegerField(default=0)
    fairy_tokens = models.IntegerField(default=0)
    steel_tokens = models.IntegerField(default=0)
    normal_tokens = models.IntegerField(default=0)
    experience = models.IntegerField(default=0)  # Total experience points
    level = models.IntegerField(default=1)  # User level
    
    last_claimed = models.DateTimeField(null=True, blank=True)

    def can_claim(self):
        """Check if the user can claim a new Pokémon."""
        if self.last_claimed is None:
            return True
        # Check if a day has passed since the last claim
        return (timezone.now() - self.last_claimed).days >= 1

    def __str__(self):
        return self.user.username

    def add_experience(self, amount):
        if self.level >= 100:
            return  # Prevent adding experience if already at level 100
        
        self.experience += amount

        # Level up logic
        while self.experience >= 100 and self.level < 100:
            self.experience -= 100
            self.level += 1

        if self.level > 100:
            self.level = 100  # Cap the level at 100
            self.experience = 0  # Optional: reset experience to 0 after hitting level cap

        self.save()

    

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()