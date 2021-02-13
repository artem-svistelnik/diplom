from django.contrib import admin
from django.urls import path,include
from django.contrib.auth import views as auth_views
#from django.contrib.auth import views.D
from . import  views
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
app_name='diplomapp'
urlpatterns = [
    path('',views.homeview,name='homeview'),
    path('sitename/', views.sitename_home, name='sitename_home'),
    path('sitename/404/', views.page_404, name='page_404'),

    path('sitename/sign-in/',auth_views.LoginView.as_view(),name='sitename_login'),
    path('sitename/sign-out/',auth_views.LogoutView.as_view(next_page='diplomapp:products'),name='sitename_logout'),
    path('sitename/sign-up/',views.sitename_sign_up,name='sign_up'),
    path('sitename/account/',views.account,name='account'),

    path('sitename/products/', views.products, name='products'),
    path('sitename/products/add/',views.add_products,name='add_products'),

    path('sitename/products/edit/delete/<int:img_id>/',views.delete_img,name='delete_img'),
    path('sitename/products/edit/<int:product_id>/', views.edit_product, name='edit_product'),

#################################
    path('sitename/products/category/<int:category_id>/<slug:category_slug>/', views.product_on_category, name='product_on_category'),
    path('sitename/products/<slug:product>/<int:product_id>/',views.product_detail,name='product_detail'),
    path('sitename/products-shop/<slug:shop_slug>/<int:shop_id>/', views.shop_products, name='shop_products'),
    path('sitename/my-products/', views.my_products, name='my_products'),
    path('sitename/my-products/delete/<int:product_id>/',views.delete_product,name='delete_product'),
   ##############################
    # path('sitename/products/search/',views.search,name='search'),

############################ KORZINA
    path('sitename/cart/', views.cart_detail, name='cart_detail'),
    path('sitename/cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('sitename/cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),


################### ORDER
    path('sitename/order/create/',views.order_create,name='order_create'),

    # path('sitename/products/test/<int:category_id>/<slug:category_slug>/',views.test_cat,name='test_cat'),
    path('sitename/order/orders_page/',views.orders_list_page,name='orders_list_page'),
    path('sitename/order/order_detail/<int:order_id>/',views.order_detail,name='order_detail'),
    path('sitename/order/order_remove/<int:order_id>/',views.order_remove,name='order_remove'),
    path('sitename/order/update_status_order/<int:order_id>',views.update_status_order,name='update_status_order')

]
