from django.contrib import admin
from .models import Movie, Review
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Sum
from django.template.response import TemplateResponse
from django.urls import path

class MovieAdmin(admin.ModelAdmin):
    ordering = ['name']
    search_fields = ['name']

    change_list_template = 'admin/movies/movie/change_list.html'

    def get_urls(self):
        custom_urls = [
            path(
                'engagement/',
                self.admin_site.admin_view(self.engagement_view),
                name = 'movies_movie_engagement',

            ),
        ]
        return custom_urls + super().get_urls()
    def engagement_view(self, request):
        if not self.has_view_permission(request):
            raise PermissionDenied

        most_bought = (
            Movie.objects
            .annotate(purchase_count=Sum('item__quantity'))
            .filter(purchase_count__gt=0)
            .order_by('-purchase_count', 'name', 'id')
            .first()
        )
        most_review = (
            Movie.objects
            .annotate(review_count=Count('review'))
            .filter(review_count__gt=0)
            .order_by('-review_count', 'name', 'id')
            .first()
        )
        context = {
            **self.admin_site.each_context(request),
            'title': 'Movie engagement',
            'opts': self.model._meta,
            'most_bought': most_bought,
            'most_reviewed': most_review,
        }

        return TemplateResponse(
            request,
            'admin/movies/movie/engagement.html',
            context
        )
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
