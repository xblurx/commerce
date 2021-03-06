from django.contrib import admin

from .models import User, Listing, Bid, Comment, Watchlist


class UsrAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)
    list_display = ('username', 'email', 'date_joined')


class ListingAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)
    list_display = (
        'title', 'user',
        'starting_bid', 'bids_number',
        'category', 'date_listed',
        'winner', 'closed'
    )


admin.site.register(User, UsrAdmin)
admin.site.register(Listing, ListingAdmin)
admin.site.register(Bid)
admin.site.register(Watchlist)
admin.site.register(Comment)
