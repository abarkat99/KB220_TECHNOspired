from django.shortcuts import render, reverse, redirect, get_object_or_404

def home(request):
    return render(request, 'home.html')