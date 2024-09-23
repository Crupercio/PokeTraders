from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    pokepeso = models.IntegerField(default=1000)
    experience = models.IntegerField(default=0)  # Total experience points
    level = models.IntegerField(default=1)  # User level
    
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