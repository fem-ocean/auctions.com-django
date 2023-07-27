from django.contrib import admin
from .models import User, Bid, Comment, Category, Listing, WatchList
from django.contrib.auth.admin import UserAdmin

# Register your models here.
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "first_name", "last_name", "email"  )

class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "category" )

class WatchlistAdmin(admin.ModelAdmin):
    filter_horizontal = ("listing", )

class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "listing", "commenter", "comment" )

class BidAdmin(admin.ModelAdmin):
    list_display = ("id", "bidder", "bid_price", "timestamp" )


admin.site.register(User, UserAdmin)
admin.site.register(Listing)
admin.site.register(Bid, BidAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(WatchList, WatchlistAdmin)

