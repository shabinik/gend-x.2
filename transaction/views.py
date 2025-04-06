from django.shortcuts import render
from . models import Transaction
from order_app.models import Order
from django.core.paginator import Paginator

# Create your views here.


def transactions_list(request):
    transctions = Transaction.objects.order_by('-id').all()

    paginator = Paginator(transctions,10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request,'admin_pages/transactions.html',{'transactions':page_obj})

