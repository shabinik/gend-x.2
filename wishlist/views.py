from django.shortcuts import render,redirect,get_object_or_404
from .models import Wishlist,WishlistItem
from proapp.models import Products,Size_Varient
from django.contrib import messages

# Create your views here.

def wishlist(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    user = request.user
    wishlist, created =Wishlist.objects.get_or_create(user=user)
    wishlist_items = wishlist.wishlistitems.all()

    return render(request,'wishlist.html',{'wishlist_item':wishlist_items})


def add_to_wishlist(request,product_id,size):

    product = get_object_or_404(Products, id=product_id)
    size_varient = product.size_varient.filter(size=size).first()

    if not size_varient:
        size = 'M'

    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    wishlist_item, created = WishlistItem.objects.get_or_create(
        wishlist=wishlist,
        product=product,
        size=size
    )
    wishlist_item.save()

    if not created:
        messages.error(request,"Item already in wishlist")
    else:
        messages.success(request, "Item added to wishlist!")
        
    return redirect('wishlist')


#DELETE WISHLIST ITEM FROM WISHLIST

def del_wish_item(request,item_id):
    wishlist_item = get_object_or_404(WishlistItem,id=item_id,wishlist__user=request.user)
    wishlist_item.delete()

    return redirect('wishlist')
    

