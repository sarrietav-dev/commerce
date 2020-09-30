from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core import validators
import datetime as dt
from django.utils import timezone
from PIL import Image


class User(AbstractUser):
    pass


class Category(models.Model):
    name = models.CharField(max_length=30)


class Listing(models.Model):
    title = models.CharField(max_length=100)
    desc = models.TextField()
    image = models.ImageField(null=True, blank=True)
    creation_date = models.DateTimeField(auto_now=True)
    starting_price = models.FloatField(default=0)
    # If the listing is closed or not.
    active = models.BooleanField(default=True)

    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="listings", blank=True)
    category = models.ForeignKey(
        Category, related_name="listings", blank=True, on_delete=models.SET_NULL,
        null=True, validators=[validators.RegexValidator("^[a-zA-Z]+$", "Enter a valid category")])

    @property
    def get_time_active(self):
        return timezone.now() - self.creation_date


    @property
    def image_url(self):
        if self.image and hasattr(self.image, "url"):
            return self.image.url

    @property
    def is_not_thumbnail(self):
        if self.image:
            img = Image.open(self.image.path)
            return img.width > 300 and img.height > 300

    @property
    def is_image_too_large(self):
        if self.image:
            img = Image.open(self.image.path)
            return img.width > 450 and img.height > 450

    def __str__(self):
        return f"{self.title} of {self.owner.username}"


class Bid(models.Model):
    price = models.FloatField()
    date = models.DateTimeField(auto_now=True)

    bidder = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="bids")
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="bids")

    def __str__(self):
        return f"{self.bidder.username} to {self.listing.title}"


class Comment(models.Model):
    date = models.DateTimeField(auto_now=True)
    body = models.TextField()

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="comments")
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="comments")

    def __str__(self):
        return f"Of {self.user.username} on {self.listing.title}"


class Watchlist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    listings = models.ManyToManyField(
        Listing, related_name="watchlists", blank=True)

    def __str__(self):
        return f"Of {self.user.username}"
