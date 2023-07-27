from django.contrib.auth.models import AbstractUser
from django.db import models



class User(AbstractUser):
    # fname = models.CharField(max_length=64)
    # lname = models.CharField(max_length=64)
    # email = models.EmailField(max_length=254)
    # phone = models.CharField(max_length=12)
    # REQUIRED_FIELDS= ['email']

    def __str__(self):
        return f"{self.id} {self.first_name} {self.username} {self.email}"
    


class Category(models.Model):
    category = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.id} {self.category}"


class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField()
    quantity  = models.PositiveIntegerField()
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)
    listing_img = models.CharField(max_length=200, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="categoryAuction")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="auctionowner", null=True)

    current_bid = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    is_active = models.BooleanField(default=True)


    
    def __str__(self):
        return f"{self.id} {self.title} {self.description} {self.quantity} {self.starting_bid} {self.listing_img} {self.category} {self.user} {self.current_bid} {self.created_at}"


class Bid(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="listings", null=True)
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bidder", null=True)
    timestamp = models.DateTimeField(auto_now_add=True, null=True)
    bid_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f" {self.id} Bid at {self.timestamp} {self.bid_price} by {self.bidder}"

class Comment(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="listingcomments", null=True)
    comment = models.TextField()
    commenter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="usercomments", null=True)
    # timestamp = models.DateTimeField(auto_now_add=True, null=True)
    
    def __str__(self):
        return f"{self.id} Comment on {self.listing} by {self.commenter.username}: {self.comment}"

class WatchList(models.Model):
    # user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="mywatchlists")
    # listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name = "listing")

    #A listing can have many instances of watchlist.
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="mywatchlists")
    listing = models.ManyToManyField(Listing, blank=True, null=True, related_name="listingwatchlist")

    def __str__(self):
        return f"{self.id} {self.listing} {self.user}"