from django.shortcuts import render,redirect,get_object_or_404
from . models import Categories


# Create your views here.
# List category

def category_list(request):
    if not request.user.is_superuser:
        return redirect('admin_login')
    
    item = Categories.objects.order_by('-id').all()
    return render(request,'admin_pages/category.html',{'item':item})


#Create category

def create_category(request):
    if not request.user.is_superuser:
        return redirect('admin_login')

    error = None
    item= Categories.objects.order_by('-id').all()

    if request.method == 'POST':
        name=request.POST.get('name')
        description=request.POST.get('description')
        offer=request.POST.get('offer') or None
        image=request.FILES.get('image')

        if not name or not description or not image:
            error="Name and description are required."
            return render(request, 'admin/category.html', {'item': item})


        category=Categories.objects.create(name=name,description=description,offer=offer,image=image)
        category.save()
        return redirect('category_list')
    return render(request,'admin/category.html',{'item':item})



#Edit Category

def edit_category(request,id):
    if not request.user.is_superuser:
        return redirect('admin_login')
    
    category = get_object_or_404(Categories,id=id)
    error=None

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        offer = request.POST.get('offer') or None
        image = request.FILES.get('image')

        category.name = name
        category.description = description
        category.offer = offer
        if image:
            category.image=image
        category.save()
        
        return redirect('category_list')
    
    return render(request,'admin_pages/edit_category.html',{'item':category})


#Unlist category

def unlist_category(request,id):
    if not request.user.is_superuser:
        return redirect('admin_login')

    category = get_object_or_404(Categories,pk=id)

    category.is_active=not category.is_active
    category.save()
    return redirect('category_list')



