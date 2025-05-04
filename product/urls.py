from django.urls import path
from product.views import ProductViewSet, FeaturedCategoryListView

product_list = ProductViewSet.as_view({'get': 'list'})
product_detail = ProductViewSet.as_view({'get': 'retrieve'})

urlpatterns = [
    path('', product_list, name='product-list'),
    path('<uuid:pk>/', product_detail, name='product-detail'),
    path('featured-categories/', FeaturedCategoryListView.as_view(), name='featured-category-list'),
]
