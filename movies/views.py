from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Review
from django.contrib.auth.decorators import login_required
from cart.models import Item
from django.db.models import Sum

# Create your views here.

@login_required
def create_review(request, id):
    if request.method == 'POST' and request.POST['comment'] != '':
        movie = Movie.objects.get(id=id)
        review = Review()
        review.comment = request.POST['comment']
        review.movie = movie
        review.user = request.user
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)

def index(request):
    search_term = request.GET.get('search')
    if search_term:
        movies = Movie.objects.filter(name__icontains=search_term)
    else:
        movies = Movie.objects.all()
    template_data = {}
    template_data['title'] = 'Movies'
    template_data['movies'] = movies
    return render(request, 'movies/index.html',
                  {'template_data': template_data})
def show(request, id):
    movie = Movie.objects.get(id=id)
    reviews = Review.objects.filter(movie=movie, reported=False)

    template_data = {}
    template_data['title'] = movie.name
    template_data['movie'] = movie
    template_data['reviews'] = reviews

    return render(request, 'movies/show.html',
                  {'template_data': template_data})
@login_required
def edit_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.user != review.user:
        return redirect('movies.show', id=id)
    if request.method == 'GET':
        template_data = {}
        template_data['title'] = 'Edit Review'
        template_data['review'] = review
        return render(request, 'movies/edit_review.html', {'template_data': template_data})
    elif request.method == 'POST' and request.POST['comment'] != '':
        review = Review.objects.get(id=review_id)
        review.comment = request.POST['comment']
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)
@login_required
def delete_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id,
        user=request.user)
    review.delete()
    return redirect('movies.show', id=id)

@login_required
def report_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.method == 'POST':
        review.reported = True
        review.save()
    return redirect('movies.show', id=id)

def map_view(request):
    regions = [
        {'name': 'Atlanta, GA', "lat": 33.7490, "lng": -84.3880},
        {'name': 'New York, NY', "lat": 40.7128, "lng": -74.0060},
        {'name': 'Los Angeles, CA', "lat": 34.0522, "lng": -118.2437},
        {'name': 'Chicago, IL', "lat": 41.8781, "lng":-87.6298},
        {'name': 'Dallas, TX', "lat":32.7767, "lng": -96.7970},
        {'name': 'Seattle, WA', "lat":47.6062, "lng":-122.3321},
    ]
    regional_data = []
    for r in regions:
        items = (
            Item.objects.filter(order__region=r['name']).values('movie__id', 'movie__name').annotate(total=Sum('quantity')).order_by('-total')
        )
        regional_data.append({
            'name': r['name'],
            'lat': r['lat'],
            'lng': r['lng'],
            'top_movie': items[0]['movie__name'] if items else "No purchases yet",
            'top_count': items[0]['total'] if items else 0,
        })
    user_orders = []
    if request.user.is_authenticated:
        user_orders = Item.objects.filter(order__user = request.user).select_related('movie', 'order')[:5]
    template_data = {
        'title': 'Local Popularity Map',
        'regional_data': regional_data,
        'user_orders': user_orders,
    }
    return render(request, 'movies/map.html',{'template_data':template_data})