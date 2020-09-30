from django import forms
from auctions.models import Bid, Comment, Listing
from django.core.exceptions import ValidationError
from django.core import validators
import re


class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing

        fields = ["title", "desc", "image", "starting_price"]

        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control ml-2 mr-2", "style": "width: 100%;"}),
            "desc": forms.Textarea(attrs={"class": "form-control ml-2 mr-2", "style": "width: 100%;"}),
            "image": forms.ClearableFileInput(attrs={"class": "form-control-file", "name": "image"}),
            "starting_price": forms.NumberInput(attrs={"class": "form-control mt-4"})
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment

        fields = ["body"]

        widgets = {
            "body": forms.Textarea(attrs={"class": "form-control"})
        }


class BidForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        if "listing" in kwargs:
            self.listing = kwargs.pop("listing")
        super().__init__(*args, **kwargs)

    price = forms.FloatField(widget=forms.NumberInput(
        attrs={"class": "form-control", "label": "", "placeholder": "Bid Price"}), label="")

    class Meta:
        model = Bid

        fields = ["price"]

    def clean(self):
        cleaned_data = super().clean()

        price = cleaned_data["price"]
        bids = Bid.objects.filter(listing=self.listing)[::-1]
        
        if len(bids) != 0:
            lastest_bid = bids[0]
            listing = lastest_bid.listing

            if lastest_bid.price >= price:
                raise ValidationError(
                    "The bid should be greater than the last one!")
            elif price < listing.starting_price:
                raise ValidationError(
                    "The bid should be greater or equal to the listing's starting price")

        return cleaned_data
