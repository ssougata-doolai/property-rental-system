from django.contrib.gis import admin
from .models import (
    Mess,
    MessRoom,
    MessImage,
    MessAddress,
    MessDetails,
    MessAmenities,
    Wishlist,
    MessInWishlist
)

class MessRoomAdmin(admin.ModelAdmin):
    list_display = ['mess','persons_per_room']

    class Meta:
        model = MessRoom

class MessImageInline(admin.TabularInline):
    model = MessImage
    list_display = ['image_tag',]
    readonly_fields = ['image_tag']

class MessAddressInline(admin.TabularInline):
    model = MessAddress
    # readonly_fields = ["location", ]

class MessAdmin(admin.OSMGeoAdmin):
    inlines = [MessImageInline, MessAddressInline]
    list_display = ('mess_id', 'active', 'available', )
    list_filter = ('active', 'available', )
    # filter_horizontal = ('MessAddressInline', )

    class Meta:
        model = Mess

class MessAddressAdmin(admin.OSMGeoAdmin):
    # readonly_fields = ['location', ]
    class Meta:
        model = MessAddress

admin.site.register(Mess, MessAdmin)
admin.site.register(MessRoom, MessRoomAdmin)
admin.site.register(MessImage)
admin.site.register(MessAddress, MessAddressAdmin)
admin.site.register(MessDetails)
admin.site.register(MessAmenities)
admin.site.register(Wishlist)
admin.site.register(MessInWishlist)
