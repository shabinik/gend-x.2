from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
import pandas as pd
import io
from django.http import HttpResponse
from django.utils.timezone import now
from order_app.models import Order,OrderItem
from django.core.paginator import Paginator
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.db.models import Sum
from proapp.models import Products
from catapp.models import Categories


# Create your views here.

def admin_login(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('admin_home')

    error = None
    if request.method == 'POST':
        username=request.POST.get('username')
        password=request.POST.get('password')
        admin=authenticate(request,username=username,password=password)
        if admin is not None:
            if admin.is_superuser:
                login(request,admin)
                return redirect('admin_home')
        else:
            error = 'invalid Username or password'
    return render(request,'admin_pages/admin_login.html',{'error':error})


def admin_home(request):
    if not request.user.is_superuser:
        return redirect('admin_login')
    
    orders = Order.objects.all()
    
    total_sales = orders.count()
    total_amount = sum(order.total_price for order in orders)
    total_discount = sum(order.discount_amount for order in orders)

    filter_type = request.GET.get('filter','monthly')
    today = datetime.today()

    if filter_type == 'yearly':
        start_date = today.replace(month=1,day=1)
    elif filter_type == 'monthly':
        start_date = today.replace(day=1)
    elif filter_type == 'weekly':
        start_date = today - timedelta(days=today.weekday())
    elif filter_type == 'daily':
        start_date = today
    else:
        start_date = today.replace(day=1)

    sales_data = (Order.objects.filter(created_at__gte=start_date).values('created_at__date')
                  .annotate(total_sales=Sum('total_price')).order_by('created_at__date'))
    
    # Prepare data for Chart.js
    labels = [entry["created_at__date"].strftime("%Y-%m-%d") for entry in sales_data]
    sales_values = [float(entry["total_sales"]) for entry in sales_data]

    top_products = Products.objects.annotate(total_sold=Sum('orderitem__quantity')).order_by('-total_sold')[:5]
    top_categories = Categories.objects.annotate(total_units_sold=Sum('products__orderitem__quantity')).order_by('-total_units_sold')[:5]
    

    context = {
        'total_sales': total_sales,
        'total_amount': total_amount,
        'total_discount': total_discount,
        'labels': labels,
        'sales_values': sales_values,
        'top_products':top_products,
        'top_categories':top_categories
    }
    
    return render(request,'admin_pages/index.html',context)



def get_sales_data(request):
    filter_type = request.GET.get("filter", "monthly")
    today = datetime.today()
    
    if filter_type == "yearly":
        start_date = today.replace(month=1, day=1)
    elif filter_type == "monthly":
        start_date = today.replace(day=1)
    elif filter_type == "weekly":
        start_date = today - timedelta(days=today.weekday())
    elif filter_type == "daily":
        start_date = today
    else:
        start_date = today.replace(day=1)

    sales_data = (
        Order.objects.filter(created_at__gte=start_date)
        .values("created_at__date")
        .annotate(total_sales=Sum("total_price"))
        .order_by("created_at__date")
    )

    labels = [entry["created_at__date"].strftime("%Y-%m-%d") for entry in sales_data]
    sales_values = [float(entry["total_sales"]) for entry in sales_data]

    return JsonResponse({"labels": labels, "sales_values": sales_values})




def sales_report(request):
    filter_type = request.GET.get('filter','monthly')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    page_number = request.GET.get('page',1)

    try:
        page_number = int(page_number)
    except ValueError:
        page_number = 1

    orders = Order.objects.all()

    if filter_type == 'yearly':
        orders = orders.filter(created_at__year=now().year)
    elif filter_type == 'weekly':
        orders = orders.filter(created_at__week=now().date().isocalendar()[1])
    elif filter_type == 'monthly':
        orders = orders.filter(created_at__month=now().month)
    elif filter_type == 'custom' and start_date and end_date:
        orders = orders.filter(created_at__range=[start_date,end_date])



    orders = orders.order_by('-created_at')

    paginator = Paginator(orders, 10)
    page_obj = paginator.get_page(page_number)

    context = {
        'orders': page_obj,
        'filter_type': filter_type,
        'start_date':start_date,
        'end_date': end_date,
        'paginator':paginator,
        'page_obj':page_obj,
    }

    return render(request,'admin_pages/sales_report.html',context)




def admin_logout(request):
    logout(request)
    return redirect('admin_login')


def users_list(request):
    if not request.user.is_superuser:
        return redirect('admin_login')
    
    user=User.objects.order_by('-id').all()

    search = request.GET.get('search','')
    if search:
        users= User.objects.filter(
            Q(username__icontains=search) | Q(email__icontains=search)
        )
    else:
        users = user

    return render(request,'admin_pages/users.html',{'users':users})

def block_user(request,id):
    if not request.user.is_superuser:
        return redirect('admin_login')
    
    user = get_object_or_404(User,id=id)
    
    user.is_active=not user.is_active
    user.save()
    return redirect('users_list')



#___________________DOWNLOAD report__________________-

def download_report(request, file_type):
    orders = Order.objects.all()
    
    
    data = [
        {
            'Order ID': order.id,
            'User': order.user.username,
            'Address': str(order.address),
            'Payment Method': order.payment_method,
            'Total Amount': order.total_price,
            'Real Price': order.real_price,
            'Discount': order.discount_amount,
            'Status': order.status,
            'Created At': order.created_at.replace(tzinfo=None),
        }
        for order in orders
    ]
    
    if file_type == 'excel':
        df = pd.DataFrame(data)
        output = io.BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        df.to_excel(writer, index=False, sheet_name='Sales Report')
        writer.close()
        output.seek(0)
        response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="sales_report.xlsx"'
        return response
    
    elif file_type == 'pdf':
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="sales_report.pdf"'
        p = canvas.Canvas(response, pagesize=letter)
        p.drawString(100, 750, 'Sales Report')
        y = 720
        for order in data:
            p.drawString(100, y, f"Order {order['Order ID']} - {order['User']} - {order['Payment Method']} - ${order['Total Amount']} (Discount: ${order['Discount']})")
            y -= 20
        p.showPage()
        p.save()
        return response
    
    return redirect('admin_home')


