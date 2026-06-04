from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from .models import Product,Contact,Orders,OrderUpdate
from math import ceil
import json
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from paytm_gateway import checksum



# Create your views here.
def index(request):
    # products = Product.objects.all()
    # n = len(products)
    # nslides = ceil(n / 4)
    # params = {'no_of_slides': nslides, 'range': range(nslides), 'products': products}
    # allProds=[[products, range(1, nslides) , nslides],
    #           [products, range(1, nslides) , nslides]]

    allProds = []
    catprods = Product.objects.values('category', 'id')  # Get categories
    cats = {item['category'] for item in catprods}       # Unique categories
    
    for cat in cats:
        prod = Product.objects.filter(category=cat)
        n = len(prod)
        nslides = ceil(n / 4)
        allProds.append([prod, range(1, nslides), nslides]) 
    params ={'allProds':allProds}
    return render(request, 'shop/index.html', params)

def searchMatch(query, item):
    if query in item.desc.lower() or query in item.product_name.lower() or query in item.category.lower():
        return True
    else:
        return False

def search(request):
    query = request.GET.get('search')
    allProds = []
    catprods = Product.objects.values('category', 'id')  # Get categories
    cats = {item['category'] for item in catprods}       # Unique categories
    
    for cat in cats:
        prodtemp = Product.objects.filter(category=cat)
        prod = [item for item in prodtemp if searchMatch(query, item)]
        n = len(prod)
        nslides = ceil(n / 4)
        if len(prod) != 0:
            allProds.append([prod, range(1, nslides), nslides]) 
    params ={'allProds':allProds, "msg": ""}
    if len(allProds) == 0 or len(query)<4:
        param = {'msg': "No Such Items Found "}
    return render(request,'shop/index.html', params)


def about(request):
    return render(request,'shop/about.html')

def contact(request):
    thank = False
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        desc = request.POST.get('desc')
        print(name,email,phone,desc)
        contact = Contact(name=name,email=email,phone=phone,desc=desc)
        contact.save()
        thank = True

    return render(request,'shop/contact.html', {'thank':thank})


def tracker(request):
    if request.method == "POST":
        orderId = request.POST.get('orderId', '').strip()
        email = request.POST.get('email', '').strip()

        if not orderId or not email:
            return JsonResponse({'error': 'Both Order ID and Email are required.'})
        try:
            orders = Orders.objects.get(order_id=orderId, email=email)
        except Orders.DoesNotExist:
            return JsonResponse({'error': 'No order found with the provided details.'})
            
        
        updates = OrderUpdate.objects.filter(order_id=orderId).order_by('timestamp')
        update_data = [{'text': u.update_desc, 'time': str(u.timestamp)} for u in updates]
            
            
        try:
            items = json.loads(orders.item_json)
        except json.JSONDecodeError:
            item = {}
                
        return JsonResponse({
            'updates': update_data,
            'items': items  # product id => {name, qty, price}
        } , safe = True)
    
    
    return render(request, 'shop/tracker.html')



def productview(request,myid):
    product = get_object_or_404(Product,id=myid)
    half_price = product.price/2
   
    return render(request,'shop/prodview.html',{'product':product, 'half_price': half_price})

def checkout(request):
        if request.method == "POST":
            item_json = request.POST.get('itemjson', '')
            name = request.POST.get('name', '')
            amount = request.POST.get('amount', '')
            email = request.POST.get('email', '')
            city = request.POST.get('city', '')
            address = request.POST.get('address1', '') + " " + request.POST.get('address2', '')
            state = request.POST.get('state', '')
            zip_code = request.POST.get('zip_code', '')
            phone = request.POST.get("phone",'')
           
           # print(name,email,city,address,state,zip_code,phone)
            order = Orders(item_json=item_json,name=name,amount=amount,email=email,city=city,address=address,state=state,zip_code=zip_code,phone=phone)
            order.save()
            update = OrderUpdate(order_id=order.order_id, update_desc="The order has been placed")
            update.save()
            thank = True
            id = order.order_id
        #    return render(request,'shop/checkout.html', {'thank':thank, 'id':id})
            param_dict = {
                
                "MID": "VMLskh33374131769871",
                "ORDER_ID": str(order.order_id),
                "CUST_ID": email,
                "TXN_AMOUNT": str(amount),
                "CHANNEL_ID": "WEB",
                "WEBSITE": "WEBSTAGING",
                "INDUSTRY_TYPE_ID": "Retail",
                "CALLBACK_URL": "https://127.0.0.1:8000/shop/handlerequest/",
            }
            param_dict['CHECKSUMHASH'] = checksum.generateSignature(param_dict, MERCHANT_KEY)

            return render(request, 'shop/paytm.html', {'param_dict': param_dict})
        
        return render(request,'shop/checkout.html')


@csrf_exempt
def handlerequest(request):
    form = request.POST
    response_dict = {}
    for i in form.keys():
        response_dict[i] = form[i]
        if i == 'CHECKSUMHASH':
            checksum = form[i]
            
    verify = checksum.verify_checksum(response_dict, MERCHANT_KEY,checksum)
    if verify: 
        if response_dict['RESPCODE'] == '01':
            print('order successfull')  
        else:
            print('order was not successful because' + response_dict['RESPMSG'])
        
    return render(request, 'shop/paymentstatus.html', {'response' : response_dict})

def cart(request):
    return render(request,'shop/cart.html')

def order_history(request):
    return render(request,'shop/order_history.html')

def profile(request):
    return render(request,'shop/profile.html')

    
