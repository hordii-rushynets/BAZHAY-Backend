from django.contrib import admin
from .models import Wish, Reservation, CandidatesForReservation


@admin.register(Wish)
class WishAdmin(admin.ModelAdmin):
    """
    Admin interface for the Wish model.

    Displays a list of wishes with the following fields:
    - name
    - display_author

    Provides search functionality on:
    - author's email
    - brand author's nickname
    - wish's name
    """
    list_display = ['name', 'display_author']
    search_fields = ['author__email', 'brand_author__nickname', 'name']
    exclude = ('name', 'description', 'additional_description')


class CandidatesForReservationInline(admin.TabularInline):
    model = CandidatesForReservation
    extra = 1


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ['wish', 'selected_user', 'is_active']
    inlines = [CandidatesForReservationInline]

    def is_active(self, obj):
        return obj.is_active()
    is_active.boolean = True


@admin.register(CandidatesForReservation)
class CandidatesForReservationAdmin(admin.ModelAdmin):
    list_display = ['reservation', 'bazhay_user']
