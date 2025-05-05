from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from product.models import Product, FeaturedCategory
from product.serializers import ProductSerializer, ProductDetailSerializer, FeaturedCategorySerializer

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.prefetch_related('variants__images').order_by('-created_at')
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProductDetailSerializer
        return ProductSerializer

class FeaturedCategoryListView(APIView):
    def get(self, request):
        categories = FeaturedCategory.objects.all()
        serializer = FeaturedCategorySerializer(categories, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
