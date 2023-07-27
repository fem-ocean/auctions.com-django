from django.contrib.auth import authenticate, login, logout
from django.db.models import Max
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from .models import Listing, Category, User, WatchList, Comment, Bid
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from decimal import Decimal



def index(request):
    # Show the categories on the index page
    categories = Category.objects.all()

    #Get the number of watchlist items for a user
    if request.user.is_authenticated:
        user_watchlists = WatchList.objects.filter(user=request.user)
        watchlistNum = sum(watchlist.listing.count() for watchlist in user_watchlists)
    
    
        listings = Listing.objects.filter(is_active=True)

        if listings:
            return render(request, "auctions/index.html", {
                "listings": listings,
                "watchlistNum": watchlistNum,
                "categories": categories
            })
    else:
        return render(request, "auctions/index.html", {
            "listings": Listing.objects.filter(is_active=True),
            "categories": categories
        })



def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    # Show the categories on the register page
    categories = Category.objects.all()

    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html", {
            "categories": categories
        })


def new_listing(request):
    # Show the categories on the new_listing page
    categories = Category.objects.all()

    #Get the number of watchlist items for a user
    if request.user.is_authenticated:
        user_watchlists = WatchList.objects.filter(user=request.user)
        watchlistNum = sum(watchlist.listing.count() for watchlist in user_watchlists)

    #get input data from the frontend
    if request.method == "POST":
        title = request.POST["title"]
        description = request.POST["description"]
        quantity = request.POST["quantity"]
        starting_bid = request.POST["starting_bid"]
        listing_img = request.POST["listing_img"]
        category = int(request.POST["category"])
        user = request.user.id
       
    #Create a new instance of the Listing class
        auction_listing = Listing(
            title=title, 
            description=description, 
            quantity=quantity, 
            starting_bid=starting_bid, 
            listing_img=listing_img, 
            category=Category.objects.get(pk=category), 
            user=User.objects.get(pk=user),
            current_bid=starting_bid
        )

    #Save new Listing class instance to our database
        auction_listing.save()
        
        return HttpResponseRedirect(reverse("index"))
        
    
    return render(request, "auctions/newListing.html", {
        "categories": categories,
        "watchlistNum": watchlistNum
    })


def listing(request, listing_id):
    # Show the categories on the listing detail page
    categories = Category.objects.all()

    #Get the number of watchlist items for a user to display in nav
    if request.user.is_authenticated:
        user_watchlists = WatchList.objects.filter(user=request.user)
        watchlistNum = sum(watchlist.listing.count() for watchlist in user_watchlists)

    # Find out if the user is the owner of the listing
    singleListing = Listing.objects.get(pk=listing_id)
    listingOwner = request.user == singleListing.user
    print(f"listingOwner: {listingOwner}")
   
    # Check if current listing exist in watchlist
    if request.user is None:
        listingInWatchlist = False
    else:
        listingInWatchlist = request.user.mywatchlists.filter(listing=singleListing.pk).exists()
   
    #for comments
    comments = Comment.objects.filter(listing=singleListing)

    # Get all bids, order in descending order of bid_price and get the first instance of bid
    bids = singleListing.listings.all()
    winnerBid = bids.order_by('-bid_price').first()
    print(f"winnerBid{winnerBid}")

    # check if the user on the page is the winner of the listing auction
    if winnerBid is not None:
        auctionWinner = winnerBid.bidder
        print(auctionWinner)
    
        if auctionWinner.pk == request.user.pk:
            winner=True
        else:
            winner=False

        print(f"Winner{winner}")
    else:
        winner = False
    
    
    return render(request, "auctions/listing.html", {
        "listing": singleListing,
        "watchlistNum": watchlistNum,
        "comments": comments,
        "categories": categories,
        "listingInWatchlist": listingInWatchlist,
        "isOwner": listingOwner,
        "winner": winner
    })
       


def category(request, id):
    # Show the categories on the listing detail page
    categories = Category.objects.all()

    #Get the number of watchlist items for a user
    if request.user.is_authenticated:
        user_watchlists = WatchList.objects.filter(user=request.user)
        watchlistNum = sum(watchlist.listing.count() for watchlist in user_watchlists)
    else:
        watchlistNum = 0

    #Get category instance and get listings of the category based on the related_name
    categoryInstance = Category.objects.get(pk=id)
    categoryListings = categoryInstance.categoryAuction.all()
    
    #render the page passing it the instance of d category class and listings of that category
    return render(request, "auctions/category.html", {
        "categoryInstance": categoryInstance,
        "categoryListings": categoryListings,
        "categories": categories,
        "watchlistNum": watchlistNum
    })



def remove_from_watchlist(request, watchlist_id):
    #once this function is called, It receives a post method to remove the instance of watchlist that has the listing and user as pk

    #Get the user
    userSignedIn = request.user

    #Identify the listing
    auctionListing = get_object_or_404(Listing, pk=watchlist_id)

    #Get the watchlist instance that have the signed-in user and the auction listing item
    watchlistInstance, created = WatchList.objects.get_or_create(user=userSignedIn)
    # watchlistInstance = WatchList(user=userSignedIn, listing=auctionListing)
    
    #Remove the listing from that instance of Watchlist of the user
    watchlistInstance.listing.remove(auctionListing)
    

    #Redirect to the listing page
    return HttpResponseRedirect(reverse('listing', args=(watchlist_id, )))

    

def add_to_watchlist(request, watchlist_id):
    
    #once this function is called, It receives a post method to add the instance of a watchlist that has the listing and user as pk

    #Get the user
    userSignedIn = request.user

    #Identify the listing
    auction_listing = get_object_or_404(Listing, pk=watchlist_id)
    watchlist, created = WatchList.objects.get_or_create(user=userSignedIn)
    watchlist.listing.add(auction_listing)

    
    #Redirect to the listing page
    return HttpResponseRedirect(reverse("listing", args=(watchlist_id, )))


def watchlist(request):
    # Show the categories on the watchlist page
    categories = Category.objects.all()


   #Get the number of watchlist items for a user
    if request.user.is_authenticated:
        user_watchlists = WatchList.objects.filter(user=request.user)
        watchlistNum = sum(watchlist.listing.count() for watchlist in user_watchlists)
        

    #get the listings in a user's watchlist
    for x in user_watchlists:
        allWatchLists = x.listing.all()

    
    return render(request, "auctions/watchlist.html", {
        "listings": allWatchLists,
        "watchlistNum": watchlistNum,
        "categories": categories,
    })


def comment(request, listing_id):
    user = request.user
    listing = Listing.objects.get(pk=listing_id)
    comment = request.POST["comment"]

    newComment = Comment(
        listing=listing,
        comment=comment,
        commenter=user,
    )
    newComment.save()

    return redirect('listing', listing_id=listing_id)


def bid(request, listing_id):
    # Show the categories on the listing detail page when a bid is placed
    categories = Category.objects.all()

    #Get the number of watchlist items for a user
    if request.user.is_authenticated:
        user_watchlists = WatchList.objects.filter(user=request.user)
        watchlistNum = sum(watchlist.listing.count() for watchlist in user_watchlists)

    #for adding or removing listing item from watchlist
    userid = request.user.id
    user = User.objects.get(pk=userid)
    singleListing = Listing.objects.get(pk=listing_id)
    listingInWatchlist = user.mywatchlists.filter(listing=singleListing.pk).exists()

    #display comments for a particular listing
    comments = Comment.objects.filter(listing=singleListing)

    #check if listing is for a particular user
    listingOwner = request.user == singleListing.user
    
    #get the instance of Listing class to know what listing i am placing the bid on.
    listing = Listing.objects.get(pk=listing_id)
    
    #get the bid_price from the form on the frontend and convert it to an integer
    bid_price = Decimal(request.POST["bidPrice"])
    
    #compare the bid_price with current_bid. If its greater, show a successful notification and replace current_bid with bid_price else show an unsuccessful notification and do not replace.
    if bid_price >= listing.current_bid:
        newBid = Bid(listing=listing, bidder=request.user, bid_price=bid_price)
        newBid.save()
        listing.current_bid = newBid.bid_price
        listing.save()

        return render(request, "auctions/listing.html", {
            "listing": listing,
            "message": "Bid successfully placed",
            "update": True,
            "categories": categories,
            "listingInWatchlist": listingInWatchlist,
            "comments": comments,
            "isOwner": listingOwner,
            "watchlistNum": watchlistNum
        })

    else:
        return render(request, "auctions/listing.html", {
            "listing": listing,
            "message": "Bid failed! Increase your bid",
            "update": False,
            "categories": categories,
            "listingInWatchlist": listingInWatchlist,
            "comments": comments,
            "isOwner": listingOwner,
            "watchlistNum": watchlistNum
        })


def closeAuction(request, listing_id):
    # Show the categories when an auction is closed
    categories = Category.objects.all()

    #Get the number of watchlist items for a user
    if request.user.is_authenticated:
        user_watchlists = WatchList.objects.filter(user=request.user)
        watchlistNum = sum(watchlist.listing.count() for watchlist in user_watchlists)

    #change listing status to inactive
    singleListing = Listing.objects.get(pk=listing_id)
    singleListing.is_active = False
    singleListing.save()

    listingOwner = request.user == singleListing.user

    #for adding and removing listing from watchlist
    userid = request.user.id
    user = User.objects.get(pk=userid)
    singleListing = Listing.objects.get(pk=listing_id)
    listingInWatchlist = user.mywatchlists.filter(listing=singleListing.pk).exists()

    #for comment
    comments = Comment.objects.filter(listing=singleListing)

    return render(request, "auctions/listing.html", {
        "listing": singleListing,
        "comments": comments,
        "categories": categories,
        "listingInWatchlist": listingInWatchlist,
        "message": "You have successfully closed your listing",
        "isOwner": listingOwner,
        "update": True,
        "watchlistNum": watchlistNum
    })
