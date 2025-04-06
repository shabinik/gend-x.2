from django.shortcuts import render,get_object_or_404
from proapp.models import Products,Size_Varient
from catapp.models import Categories
from django.core.paginator import Paginator



# Create your views here.


def index(request):

    categories = Categories.objects.filter(is_active=True).order_by('-id').all()

    items = Products.objects.order_by('-id').all()[:3]
    username= request.user.username

    return render(request,'index.html',{'categories':categories,'items':items,'username':username})



#Shop
def shop(request):
    # Get all products
    items = Products.objects.filter(is_active = True,category__is_active =True).order_by('-id')

    # Get filter parameters from GET request
    search = request.GET.get('search', '')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    category = request.GET.get('category')
    sort_option = request.GET.get('sort')

    if search:
        items = items.filter(name__icontains=search)

    if min_price:
        try:
            min_price = int(min_price)
            items = items.filter(price__gte=min_price)
        except ValueError:
            pass  

    if max_price:
        try:
            max_price = int(max_price)
            items = items.filter(price__lte=max_price)
        except ValueError:
            pass

    if category:
        try:
            category_id = int(category)  # Convert category ID to integer
            items = items.filter(category__id=category_id)  # Correct filtering
        except ValueError:
            pass  # Ignore invalid category values
    
    if sort_option == "price_low":
        items = items.order_by("price")
    elif sort_option == "price_high":
        items = items.order_by("-price")
        
    #Pagination
    paginator = Paginator(items, 4)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
   
    categories = Categories.objects.all()

    username= request.user.username

    return render(request, 'shop.html', {'items': page_obj, 'categories': categories,'username':username})

#Product Details

def product_detail(request,id):
    product = get_object_or_404(Products,id=id)
    varient = product.size_varient.all()
    return render(request,'product_details.html',{'item':product,'varient':varient})



def wishlist(request):
    return render(request,'wishlist.html')


def cart(request):
    return render(request,'cart.html')






