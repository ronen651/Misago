import random

from path import Path
from PIL import Image

from django.conf import settings
from django.core.files.base import ContentFile

from . import store


DEFAULT_GALLERY = '__default__'


def get_available_galleries(include_default=False):
    """
    Returns list of dicts containing 'name' and list of images

    Only jpgs, gifs and pngs are supported avatar images.
    Galleries are
    """
    from ..models import AvatarGallery

    galleries = []
    galleries_dicts = {}

    for image in AvatarGallery.objects.all():
        if image.gallery == DEFAULT_GALLERY and not include_default:
            continue

        if image.gallery not in galleries_dicts:
            galleries_dicts[image.gallery] = {
                'name': image.gallery,
                'images': []
            }

            galleries.append(galleries_dicts[image.gallery])

        galleries_dicts[image.gallery]['images'].append(image)

    return galleries


def galleries_exist():
    return bool(get_available_galleries())


def load_avatar_galleries():
    from ..models import AvatarGallery

    galleries = []
    for directory in Path(settings.MISAGO_AVATAR_GALLERY).dirs():
        gallery_name = directory.name

        images = directory.files('*.gif')
        images += directory.files('*.jpg')
        images += directory.files('*.jpeg')
        images += directory.files('*.png')

        for image in images:
            with open(image, 'rb') as image_file:
                galleries.append(AvatarGallery.objects.create(
                    gallery=gallery_name,
                    image=ContentFile(image_file.read(), 'image')
                ))
    return galleries


def set_avatar(user, image):
    store.store_new_avatar(user, Image.open(image.path))


def set_random_avatar(user):
    galleries = get_available_galleries(include_default=True)
    if not galleries:
        raise RuntimeError("no avatar galleries are set")

    avatars_list = []
    for gallery in galleries:
        if gallery['name'] == DEFAULT_GALLERY:
            avatars_list = gallery['images']
            break
        else:
            avatars_list += gallery['images']

    random_image_path = random.choice(avatars_list).path
    store.store_new_avatar(user, Image.open(random_image_path))
