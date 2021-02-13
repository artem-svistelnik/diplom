from django.shortcuts import render,redirect,get_object_or_404,reverse

# Create your views here.
from django.contrib.auth.decorators import login_required
from .forms import UserForm,ShopForm, UserFormEdit,ProductForm,ImagesForm, SearchForm,CartAddProductForm,OrderCreateForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login
from .models import  Product,Shop  ,Category,ProductImages,Order,OrderItem
from django.contrib.postgres.search import TrigramSimilarity
from django.views.decorators.http import require_POST
from .cart import Cart

def homeview(request):
    return redirect('diplomapp:sitename_home')

def sitename_home(request):
    return redirect('diplomapp:products')

def sitename_sign_up(request):
    user_form=UserForm()
    shop_form=ShopForm()
    if request.method=='POST':
        user_form=UserForm(request.POST)
        shop_form=ShopForm(request.POST,request.FILES)
        if user_form.is_valid() and shop_form.is_valid():
            new_user=User.objects.create_user(**user_form.cleaned_data)
            new_shop=shop_form.save(commit=False)
            new_shop.owner=new_user
            new_shop.save()
            login(request,authenticate(username=user_form.cleaned_data['username'],
                                       password=user_form.cleaned_data['password']))
            return redirect('diplomapp:sitename_home')
    return render(request,'registration/sign_up.html',{'user_form':user_form,
                                                       'shop_form':shop_form})

@login_required(login_url='/sitename/sign-in/')
def account(request):
    user_form=UserFormEdit(instance=request.user)
    shop_form=ShopForm(instance=request.user.shop)
    if request.method=='POST':
        user_form = UserFormEdit(request.POST,instance=request.user)
        shop_form = ShopForm(request.POST,instance=request.user.shop)
        if user_form.is_valid() and shop_form.is_valid():
            user_form.save()
            shop_form.save()
    return  render(request,'diplomapp/account.html',{'user_form':user_form,
                                                     'shop_form':shop_form})

@login_required(login_url='/sitename/sign-in/')
def my_products(request):
    products=Product.objects.filter(shop=request.user.shop).order_by('-availability','-id')#показ товаров этого юзера
    return  render(request,'diplomapp/my_products.html',{'products':products})




def products(request):
    shop = None
    category = None
    search_form = SearchForm()
    query = None
    products = []
    if 'query' in request.GET:
        search_form = SearchForm(request.GET)
        if search_form.is_valid():
            query = search_form.cleaned_data['query']
            products = Product.objects.annotate(similarity=TrigramSimilarity('product_name',query)+TrigramSimilarity('short_description',query)
                                                ).filter(similarity__gt=0.1).order_by('-similarity')
            print('products', products)
        else:
            print(search_form.errors)
    else:
        products = Product.objects.all().order_by('-availability','-id')
    nodes = Category.objects.all()
    return render(request, 'diplomapp/products.html', {'products': products,
                                                       'nodes': nodes,
                                                       'category': category,
                                                       'shop': shop,
                                                       'search_form': search_form,
                                                       'query': query,
                                                       })



def product_detail(request,product,product_id):
    product_det=get_object_or_404(Product,slug=product,id=product_id)
    images=ProductImages.objects.filter(product=product_det)
    cart_product_form = CartAddProductForm()
    return render(request,'diplomapp/product_detail.html',{'product':product_det,
                                                           'images':images,
                                                           'cart_product_form': cart_product_form
                                                                })

def shop_products(request,shop_slug,shop_id):
    search_form = SearchForm()
    query = None
    products = []
    category=None
    shop=get_object_or_404(Shop,slug=shop_slug,id=shop_id)
    if 'query' in request.GET:
        search_form = SearchForm(request.GET)

        if search_form.is_valid():
            query = search_form.cleaned_data['query']
            products=Product.objects.annotate(
                similarity=TrigramSimilarity('product_name', query) + TrigramSimilarity('short_description', query)
                ).filter(similarity__gt=0.5).order_by('similarity','-availability',)
        else:
            print(search_form.errors)
    else:
        products=Product.objects.filter(shop=shop).order_by('-availability')
    nodes = Category.objects.all()
    return render(request, 'diplomapp/products.html', {'products': products,
                                                       'nodes': nodes,
                                                       'category':category,
                                                       'shop':shop,
                                                       'search_form': search_form,
                                                       'query': query,
                                                       })

def test(category,n,query):
    if query:
        cats=Category.objects.filter(parent=category)
        products = Product.objects.annotate(
            similarity=TrigramSimilarity('product_name', query) + TrigramSimilarity('short_description', query)
        ).filter(similarity__gt=0.5,category=category ).order_by('-similarity')
        n += 1
        for cat in cats:
            products = products.union(products,Product.objects.annotate(
            similarity=TrigramSimilarity('product_name', query) + TrigramSimilarity('short_description', query)
        ).filter(similarity__gt=0.5,category=cat ).order_by('-similarity'))

            products=products.union(products,test(cat,n,query))
        return products
    else:
        cats = Category.objects.filter(parent=category)
        products=Product.objects.filter(category=category)
        n += 1
        for cat in cats:
            products=products.union(products,Product.objects.filter(category=cat))
            products=products.union(products,test(cat,n,query))
        return products



def product_on_category(request,category_id,category_slug):
    search_form = SearchForm()
    query = None
    products = []
    shop=None
    category=get_object_or_404(Category,id=category_id,slug=category_slug)
    if 'query' in request.GET:
        search_form = SearchForm(request.GET)
        if search_form.is_valid():
            query = search_form.cleaned_data['query']
            products = test(category, 0,query)
        else:
            print(search_form.errors)
    else:
        products=test(category,0,query)
    nodes = Category.objects.all()
    return render(request, 'diplomapp/products.html', {'products': products,
                                                       'nodes': nodes,
                                                       'category':category,
                                                       'shop': shop,
                                                       'search_form': search_form,
                                                       'query': query,
                                                       })




@login_required(login_url='/sitename/sign-in/')
def add_products(request):#zbs add
    form = ProductForm()
    images_form=ImagesForm()
    if request.method=='POST':
        form=ProductForm(request.POST,request.FILES)
        images_form = ImagesForm(request.POST, request.FILES)
        if form.is_valid() and images_form.is_valid():
            product=form.save(commit=False)

            product.shop=request.user.shop
            product=form.save()
            product.save()
            for field in request.FILES.keys():
                if field=='image':
                    for img_1 in request.FILES.getlist(field):
                        product=Product.objects.get(id=product.id)
                        product.image=img_1
                        print(product)
                        product.save()
                if field=='product_image':
                    for img in request.FILES.getlist(field):
                        image=ProductImages(product_image=img)
                        image.product=product
                        image.save()
            return redirect('diplomapp:products')
        else:
            form = ProductForm()
            images_form=ImagesForm()
    return  render(request,'diplomapp/add_products.html',{'form':form,
                                                          'images_form':images_form})



@login_required(login_url='/sitename/sign-in/')
def edit_product(request,product_id):
    product_get=Product.objects.get(id=product_id)
    images=ProductImages.objects.filter(product=product_get)
    if request.user.shop==product_get.shop:
        form = ProductForm(instance=Product.objects.get(id=product_id))
        form_img = ImagesForm(ProductImages.objects.filter(product=product_get))
        if request.method=='POST':
            form=ProductForm(request.POST,request.FILES,instance=Product.objects.get(id=product_id))
            form_img = ImagesForm(request.POST,request.FILES,instance=Product.objects.get(id=product_id))
            if form.is_valid() and form_img.is_valid() :
                product=form.save()
                product.save()
                n = 0
                for field in request.FILES.keys():
                    if field =='image':
                        for img_1 in request.FILES.getlist(field):
                            product = Product.objects.get(id=product.id)
                            product.image = img_1
                            product.save()
                    if field=='product_image':
                        for img in request.FILES.getlist(field):
                            image = ProductImages(product_image=img)
                            image.product = product
                            image.save()
                return  redirect('diplomapp:my_products')
            else:
                print(form.errors)
                print(form_img)
    else:
        return redirect('diplomapp:page_404')
    return render(request, 'diplomapp/edit_product.html', {'form': form,
                                                            'images':images,
                                                           'form_img': form_img,
                                                           'product':product_get
                                                           })
@login_required(login_url='/sitename/sign-in/')
def delete_product(request,product_id):
    try:
        product=get_object_or_404(Product,id=product_id)
        product.delete()
        return redirect('diplomapp:my_products')
    except Product.DoesNotExist:
        print('error')
        return redirect('diplomapp:my_products')

@login_required(login_url='/sitename/sign-in/')
def delete_img(request,img_id):
    img=ProductImages.objects.get(id=img_id)
    product=img.product
    try:
        img.delete()
    except:
        pass
    return  redirect('diplomapp:edit_product' ,product_id=product.id)


def page_404(request):
    return render(request,'diplomapp/page_404.html',{})


@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = CartAddProductForm()
    if request.method=='POST':
        form = CartAddProductForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            cart.add(product=product,
                    quantity=cd['quantity'],
                    update_quantity=cd['update'])
    else:
        form=CartAddProductForm()
    return redirect('diplomapp:cart_detail')

def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('diplomapp:cart_detail')

def cart_detail(request):
    cart = Cart(request)
    for item in cart:
        item['update_quantity_form'] = CartAddProductForm(
            initial={'quantity': item['quantity'],
                     'update': True})
    return render(request, 'diplomapp/cart/detail.html', {'cart': cart})


def order_create(request):
    cart=Cart(request)
    shop_list = []
    if request.method=='POST':
        form=OrderCreateForm(request.POST)
        if form.is_valid():
            order=form.save()
            for item in cart:
                OrderItem.objects.create(order=order,
                                         product=item['product'],
                                         price=item['price'],
                                         quantity=item['quantity'],)
            # Очищаем корзину.
            cart.clear()
            return render(request,
                              'diplomapp/order/created.html',
                              {'order': order})
    else:
        form = OrderCreateForm()
    return render(request,
                          'diplomapp/order/create.html',
                      {'cart': cart, 'form': form})


@login_required(login_url='/sitename/sign-in/')
def orders_list_page(request):
    shop=request.user.shop
    order_num=OrderItem.objects.filter(product__shop=shop).values('order').distinct()
    order_num_list=[]
    for order in order_num:
        order_num_list.append(order['order'])
    orders=Order.objects.filter(id__in=order_num_list).order_by('status','created')
    return render(request,'diplomapp/order/orders_list.html',{'orders':orders,})

@login_required(login_url='/sitename/sign-in/')
def order_remove(request,order_id):
    order = Order.objects.get(id=order_id)
    order.delete()
    return redirect('diplomapp:orders_list_page')

@login_required(login_url='/sitename/sign-in/')
def order_detail(request,order_id):
    shop=request.user.shop
    order=Order.objects.get(id=order_id)
    order_items=OrderItem.objects.filter(order__id=order_id,product__shop=shop)
    total_price=0
    for item in order_items:
        total_price+=(item.price*item.quantity)
    print(total_price)
    return  render(request,'diplomapp/order/order_detail.html',{'order':order,
                                                                 'order_items':order_items,
                                                                'total_price':total_price})

@login_required(login_url='/sitename/sign-in/')
def update_status_order(request,order_id):
    order = Order.objects.get(id=order_id)
    print(order.status)
    if order.status==True:
        order.status=False
    else:
        order.status =True
    order.save()
    return  redirect('diplomapp:order_detail',order_id=order_id)
