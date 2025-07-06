from django.db.models.signals import pre_delete
from django.dispatch import receiver

from shopping.models import ProductImage


@receiver(pre_delete, sender=ProductImage)
def delete_image_file(sender, instance: ProductImage, **kwargs):
    if instance.image:
        instance.image.delete(save=False)
