from django.shortcuts import render,redirect,get_object_or_404
from . models import Products,Size_Varient
from catapp.models import Categories
from django.core.paginator import Paginator
from decimal import Decimal,ROUND_DOWN

# Create your views here.

#Create New Product

def create_product(request):
    if not request.user.is_superuser:
        return redirect('admin_login')
    

    error = None
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        category_id = request.POST.get('category_id')
        price = request.POST.get('price')
        offer = request.POST.get('offer')
        image1 = request.FILES.get('image1')
        image2 = request.FILES.get('image2')
        image3 = request.FILES.get('image3')
        
        try:
            if not name or not description or not category_id or not price or not offer or not image1 or not image2 or not image3:
                error = 'All fields are Compelsory'
            if name.strip()=='':
                error = 'Enter a valid name'

            price=int(price)
            if price < 0:
                error = 'Price should be Positive Integer'

            if not error:
                category=Categories.objects.get(id=category_id)

                category_offer = Decimal(category.offer or 0)
                product_offer = Decimal(offer or 0)

                best_offer = max(category_offer, product_offer)
                discounted_price = price - (price * (best_offer / Decimal(100)))


                discounted_price = discounted_price.quantize(Decimal('1'), rounding=ROUND_DOWN)


                discounted_price = int(discounted_price)

                product=Products.objects.create(category=category,name=name,
                                                description=description,price=discounted_price,
                                                offer=best_offer,image1=image1,image2=image2,image3=image3)
                product.save()

                return redirect('product_list')
            
        except(ValueError,Categories.DoesNotExist):
            error = "Invalid input. Please check your entries."
    
    categories=Categories.objects.all()
    return render(request,'admin_pages/create_product.html',{'categories':categories,'error':error})

# List your Products

def product_list(request):
    if not request.user.is_superuser:
        return redirect('admin_login')
    products=Products.objects.order_by('-id').all()

    paginator = Paginator(products, 4)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request,'admin_pages/product.html',{'item':page_obj})


# Unlist the product

def product_unlist(request,id):
    if not request.user.is_superuser:
        return redirect('admin_login')
    
    item = get_object_or_404(Products,id=id)

    item.is_active = not item.is_active
    item.save()
    
    return redirect('product_list')


#Edit the product

def edit_product(request,id):
    if not request.user.is_superuser:
        return redirect('admin_login')
    
    product = get_object_or_404(Products,id=id)
    categories = Categories.objects.all()

    error = None

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        category_id = request.POST.get('category_id')
        price = request.POST.get('price')
        offer = request.POST.get('offer')
        image1 = request.FILES.get('image1')
        image2 = request.FILES.get('image2')
        image3 = request.FILES.get('image3')

        price = int(price)
        category=Categories.objects.get(id=category_id)

        category_offer = Decimal(category.offer or 0)
        product_offer = Decimal(offer or 0)

        best_offer = max(category_offer, product_offer)
       
        discounted_price = price - (price * (best_offer / Decimal(100)))
        discounted_price = discounted_price.quantize(Decimal('1'), rounding=ROUND_DOWN)
        discounted_price = int(discounted_price)


        product.name=name
        product.description=description
        product.price = discounted_price
        product.offer=best_offer
        if image1:
            product.image1=image1
        if image2:
            product.image2=image2
        if image3:
            product.image3=image3
        

        product.category=category

        product.save()

        return redirect('product_list')
    
    return render(request,'admin_pages/edit_product.html',{'item':product, 'categories':categories})


# List Size Varients

def list_varient(request,id):
    if not request.user.is_superuser:
        return redirect('admin_login')

    product = get_object_or_404(Products,id=id)
    product_id=product.id

    varients= Size_Varient.objects.filter(product=product.id).order_by('-id')
    
    return render(request,'admin_pages/varient_list.html',{'item':varients,'product_id':product_id})


#Create Size varient

def create_varient(request,id):
    if not request.user.is_superuser:
        return redirect('admin_login')
    
    error = None
    product=get_object_or_404(Products,id=id)
    valid_sizes = ['S', 'M', 'L', 'XL', 'XXL']
    if request.method=='POST':
        size = request.POST.get('size')
        stock = request.POST.get('stock')
        
        try:
            if not size or not stock:
                error = 'All fields are Compalsory'
            if int(stock)<0:
                error = 'Stock will not be negative'
            if not error:
                size_varient=Size_Varient.objects.create(product=product,size=size,stock=stock)
                size_varient.save()

                return redirect('list_varient',id=id)
        except(ValueError):
            error =  "Invalid input. Please check your entries."
    return render(request,'admin_pages/create_varient.html',{'item':product,'valid_sizes':valid_sizes,'error':error})


#Edit varient

def edit_varient(request,id,varient_id):
    if not request.user.is_superuser:
        return redirect('admin_login')
    
    varient = get_object_or_404(Size_Varient,id=varient_id)
    product = get_object_or_404(Products,id=id)

    if request.method=='POST':
        size = request.POST.get('size')
        stock = request.POST.get('stock')
        varient.product=product
        varient.size=size
        varient.stock=stock
        varient.save()
        return redirect('list_varient',id=id)

    return render(request,'admin_pages/edit_varient.html',{'item':varient})
