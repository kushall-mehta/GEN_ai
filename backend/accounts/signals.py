## for automation of model !! like when role = tainer is selected then it will added to out other application also


from django.apps import apps ## we cannot directly import the app so we used django.apps(means from installed app we import our apps)
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User


@receiver(post_save, sender=User) #used to Connect the function below to a particular signal ##sender means that Which model is used !! like to which model
def create_trainer_profile(sender, instance, created, **kwargs): #post_save is a Django signal ##the obj is saved in instance
    """
    when user.save() method is called then  it updates db and then this post_save signal fires
    """
    if created and instance.role == "trainer":
        TrainerProfile = apps.get_model("fitness", "TrainerProfile") #so the tainer profile will be created if it adds the user
        TrainerProfile.objects.create(user=instance)



# @receiver(post_save, sender=User)
# def create_trainer_profile(sender, instance, created, **kwargs):
#     if created and instance.role == "trainer":
#         TrainerProfile = apps.get_model("fitness", "TrainerProfile")
#         TrainerProfile.objects.create(user=instance)


#
# @receiver       → connects function to signal
# post_save       → runs after model is saved
# sender=User     → listen only to User
# instance        → actual saved User object
# created         → True if newly created
# apps.get_model  → gets model from Django app registry
# objects.create  → creates database record
# user=instance   → connects TrainerProfile to that User