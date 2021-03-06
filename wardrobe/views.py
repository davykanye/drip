from django.shortcuts import render, redirect
from wardrobe.models import *
from django.shortcuts import (get_object_or_404, HttpResponseRedirect)
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
###########################################
import os
import json
from bs4 import BeautifulSoup
from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile
import requests
from ast import literal_eval
import random
import time
from wardrobe.scrapers import *
from wardrobe.algorithm import *
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
# Create your views here.

@login_required
def gallery(request):
    start = time.time()
    user = request.user

    categories = Category.objects.all()
    photos = Photos.objects.filter(user=user)

    category = request.GET.get('category')
    if category == None:
        pass
    else:
        photos = photos.filter(category__name=category)



    outfits = Outfit.objects.filter(user=user)

    context = {'categories': categories, 'photos': photos, 'outfits': outfits, 'user': user}
    template_name = 'wardrobe/wardrobe.html'
    end = time.time()
    time_taken = end - start
    print(time_taken)
    return render(request, template_name, context)

# adding clothe items
@login_required
def add_pic(request):
    categories = Category.objects.all()
    styles = Style.objects.all()

    if request.method == 'POST':
        data = request.POST
        image = request.FILES.get('image')

        if data['category'] != 'none':
            category = Category.objects.get(id=data['category'])
        else:
            category = None

        photo = Photos.objects.create(
            user = request.user,
            category = category,
            description=data['description'],
            image=image,
        )
        return redirect('gallery')

    context = {'categories': categories, 'styles': styles}
    template_name = 'wardrobe/add_pic.html'
    return render(request, template_name, context)

# Gathering Pins
@login_required
def gather_pins(request):
    fashion = Inspiration.objects.all()
    if request.method == 'POST':
        start = time.time()
        data = request.POST
        if fashion.filter(name=data["Inspiration"]).exists():
            messages.info(request, "Already done this")
        else:
            I = Inspiration.objects.create(name=data["Inspiration"])
            pins = pinterest_scraper(data["Inspiration"])
            for pin in pins:
                Pin.objects.create(image=pin, Inspiration=I)
            time_taken = time.time() - start    
            messages.info(request, "Success" + "|"+ str(time_taken))

    context = {"fashion": fashion}
    template_name = 'wardrobe/Gather.html'
    return render(request, template_name, context)

# viewing clothe items
@login_required
def detail(request, pk):
    start = time.time()
    photo = Photos.objects.get(id=pk)
    styles = photo.styles
    context = {'photo' : photo, 'styles': styles}
    template_name = 'wardrobe/detail.html'

    end = time.time()
    time_taken = end - start
    print(time_taken)
    return render(request, template_name, context)

# editing clothe items
@login_required
def edit_pic(request, pk):
    categories = Category.objects.all()
    photo = Photos.objects.get(id=pk)

    if request.method == 'POST':
        data = request.POST

        if data['category'] != 'none':
            category = Category.objects.get(id=data['category'])
        else:
            category = None

        photo.category = category
        photo.description = data['description']
        photo.save()

        return redirect('gallery')

    context = {'categories': categories, 'photo': photo}
    template_name = 'wardrobe/edit_pic.html'
    return render(request, template_name, context)


# deleting clothe items

# Profile View man
@login_required
def delete(request, pk):
    photo = Photos.objects.get(id=pk)

    photo.delete()

    return HttpResponseRedirect('/')


def settings(request):

    context = {}
    template_name = 'wardrobe/settings.html'
    return render(request, template_name, context)

def feedback(request):
    try:
        data = request.GET.get('feedback')

        feedback = FeedBack.objects.create(
        user = request.user,
        rating = rating,
        message = message
        )
    except Exception as e:
        print(e)

################## OUTFITS SECTION ###############################

# Creating Outfits
@login_required
def create_outfit(request):
    photos = Photos.objects.filter(user=request.user)

    if request.method == 'POST':
        data = request.POST
        selected_clothes = request.POST.getlist('clothe')
        items = []
        for i in selected_clothes:
            i = int(i)
            items.append(i)

        #then create outfit in the models

        outfit_name = 'wow'

        outfit = Outfit.objects.create(user=request.user, name = outfit_name)
        outfit.items.set(items)

        return redirect('gallery')

    context = {'photos': photos}
    template_name = 'wardrobe/create_outfit.html'

    return render(request, template_name, context)


# ################These were the two hardest views in the entire MVP###########

########### THE OUTFIT_FEED #################
@login_required
def outfit_feed(request):
    start_time = time.time()
    user = request.user
    items = Photos.objects.filter(user=user)
    ######### FIlTERING BY STYLES ##########
    seed = pick_seeds(items)
    outfit = make_outfit(seed[0], items)

    time_taken = time.time() - start_time
    print('The outfit of the day is', outfit)
    print(time_taken)

    context = {}
    template_name = 'wardrobe/outfit_feed.html'
    return render(request, template_name, context)



@login_required
def outfit_view(request):

    context = {}
    template_name = 'wardrobe/outfit_view.html'
    return render(request, template_name, context)

############# ADD ITEMS IN A SPECIAL WAY #####################
@login_required
def search(request):
    if request.method == 'POST':
        query = request.POST['query']
    else:
        query = 'grey shirt'

#     GOOGLE_IMAGE = \
#     'https://www.google.com/search?site=&tbm=isch&source=hp&biw=1873&bih=990&'

#     usr_agent = {
#     'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
#     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#     'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
#     'Accept-Encoding': 'none',
#     'Accept-Language': 'en-US,en;q=0.8',
#     'Connection': 'keep-alive',
# }


#     search = GOOGLE_IMAGE + "q=" + query
#     html = requests.get(search, headers=usr_agent)
#     response = html.text

#     soup = BeautifulSoup(response, 'html.parser')
#     results = soup.find_all('img')

#     links = []
#     for img in results:
#         link = img['src']
#         links.append(link)
#     links.pop(0)

    global proper
    def proper():
        return query

    links = item_scraper(query)

    context = {'images': links, 'query': query}
    template_name = 'wardrobe/search.html'

    return render(request, template_name, context)



@login_required
def search_item(request, image):

    SAVE_FOLDER = 'staticfiles/searched'
    name = proper()
    id = random.randint(1, 99)

    categories = Category.objects.all()
    styles = Style.objects.all()

    user = request.user
    category = Category.objects.get(name='top')
    style = Style.objects.all()
    response = requests.get(image)

    photo = SAVE_FOLDER + '/' + name + str(id) + '.jpg'
    with open(photo, 'wb') as file:
        file.write(response.content)

    img = Image.open(photo)
    image_bytes = BytesIO()
    img.save(image_bytes, format='JPEG')


    hope = InMemoryUploadedFile(
    image_bytes, None, name, 'image/jpeg', None, None, None
    )


    print(type(img))
    print(img.size)

    if request.method == 'POST':
        data = request.POST
        selected_style = request.POST.getlist('style')
        styles = []
        name = 'saved_picture'
        for i in selected_style:
            i = int(i)
            styles.append(i)

        if data['category'] != 'none':
            category = Category.objects.get(id=data['category'])
        else:
            category = None

        photo = Photos.objects.create(
            user = request.user,
            category = category,
            description=name,
            image=hope,
        )
        photo.style.set(styles)

        return redirect('gallery')



    template_name = 'wardrobe/search_item.html'
    context = {'image': image, 'name': name, 'categories': categories, 'styles': styles}
    return render(request, template_name, context)
