from django.contrib import admin
from .models import Movie, Review
class MovieAdmin(admin.ModelAdmin):
    ordering = ['name']
    search_fields = ['name']
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['id', 'movie', 'user', 'reported', 'date']
    list_filter = ['reported', 'movie']
    search_fields = ['comment', 'movie_name', 'user_username']
    actions= ['restore_reviews']

    def restore_reviews(self, request, queryset):
        queryset.update(reported=False)
    restore_reviews.short_description = 'Restore selected reviews'
    
admin.site.register(Movie, MovieAdmin)
# Register your models here.
admin.site.register(Review)
