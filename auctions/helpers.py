from functools import wraps
from auctions.models import Listing
from django.http import HttpResponseRedirect
from django.urls import reverse

def ensure_user(f):
    @wraps(f)
    def wrapper(request, listing_id):
        listing = Listing.objects.get(id=listing_id)
        if request.user == listing.owner:
            f(request, listing_id)
        else:
            return HttpResponseRedirect(reverse("error", args=(403, "You shall not pass")))
    return wrapper