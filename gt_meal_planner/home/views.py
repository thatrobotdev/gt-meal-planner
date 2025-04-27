import random
from django.shortcuts import render
from movies.models import Movie

def index(request):
    movies = list(Movie.objects.all()) 

    template_data = {}
    template_data['title'] = 'Movies Store'
    return render(request, 'home/index.html', {'template_data': template_data})

def about(request):
    template_data = {}
    template_data = {'title': 'About'}
    return render(request, 'home/about.html', {'template_data': template_data})
