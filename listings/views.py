from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404

from .models import Category, Product, ProductImage
from .serializers import CategorySerializer, ProductSerializer, ProductImageSerializer


# ---------------------------
# CATEGORY VIEWS
# ---------------------------
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticatedOrReadOnly])
def category_list_create(request):
    if request.method == "GET":
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

    elif request.method == "POST":
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticatedOrReadOnly])
def category_detail(request, pk):
    category = get_object_or_404(Category, pk=pk)

    if request.method == "GET":
        serializer = CategorySerializer(category)
        return Response(serializer.data)

    elif request.method == "PUT":
        serializer = CategorySerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ---------------------------
# PRODUCT VIEWS
# ---------------------------
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticatedOrReadOnly])
def product_list_create(request):
    if request.method == "GET":
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    elif request.method == "POST":
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(seller=request.user)  # assign seller automatically
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticatedOrReadOnly])
def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)

    if request.method == "GET":
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    elif request.method == "PUT":
        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(seller=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ---------------------------
# PRODUCT IMAGE VIEWS
# ---------------------------
@api_view(["GET", "POST", "DELETE"])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def product_images(request, slug):
    product = get_object_or_404(Product, slug=slug)

    if request.method == "GET":
        images = ProductImage.objects.filter(product=product)
        serializer = ProductImageSerializer(images, many=True)
        return Response(serializer.data)

    elif request.method == "POST":
        files = request.FILES.getlist("images")
        images = []
        for file in files:
            img = ProductImage.objects.create(product=product, image=file)
            images.append(img)
        serializer = ProductImageSerializer(images, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    elif request.method == "DELETE":
        images = ProductImage.objects.filter(product=product)
        images.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ---------------------------
# PRODUCT DESCRIPTION VIEW
# ---------------------------
@api_view(["GET", "PUT"])
@permission_classes([AllowAny])
def product_description(request, slug):
    product = get_object_or_404(Product, slug=slug)

    if request.method == "GET":
        return Response({"slug": product.slug, "description": product.description})

    elif request.method == "PUT":
        description = request.data.get("description")
        if description:
            product.description = description
            product.save()
            return Response({"slug": product.slug, "description": product.description})
        return Response({"error": "Description is required"}, status=status.HTTP_400_BAD_REQUEST)


from rest_framework.pagination import PageNumberPagination
from django.db.models import Q, Avg

# Custom Pagination
class ProductPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50

# ---------------------------
# PRODUCT LIST WITH SEARCH & FILTER
# ---------------------------
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticatedOrReadOnly])
def product_list_create(request):
    if request.method == "GET":
        queryset = Product.objects.all()

        # Search
        search = request.GET.get("search")
        if search:
            queryset = queryset.filter(Q(name__icontains=search) | Q(description__icontains=search))

        # Filter by category
        category_id = request.GET.get("category")
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        # Pagination
        paginator = ProductPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = ProductSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    elif request.method == "POST":
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(seller=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ---------------------------
# PRODUCT REVIEWS
# ---------------------------
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticatedOrReadOnly])
def product_reviews(request, slug):
    product = get_object_or_404(Product, slug=slug)

    if request.method == "GET":
        reviews = ProductReview.objects.filter(product=product)
        serializer = ProductReviewSerializer(reviews, many=True)
        average = reviews.aggregate(avg_rating=Avg("rating"))["avg_rating"]
        return Response({"average_rating": average or 0, "reviews": serializer.data})

    elif request.method == "POST":
        serializer = ProductReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(product=product, user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_product_stock(request, slug):
    product = get_object_or_404(Product, slug=slug)
    stock = request.data.get("stock")
    if stock is not None and int(stock) >= 0:
        product.stock = int(stock)
        product.save()
        return Response({"slug": product.slug, "stock": product.stock})
    return Response({"error": "Invalid stock value"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticatedOrReadOnly])
def product_variant_list_create(request, slug):
    product = get_object_or_404(Product, slug=slug)

    if request.method == "GET":
        variants = ProductVariant.objects.filter(product=product)
        serializer = ProductVariantSerializer(variants, many=True)
        return Response(serializer.data)

    elif request.method == "POST":
        serializer = ProductVariantSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(product=product)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(["GET", "POST", "DELETE"])
@permission_classes([IsAuthenticated])
def wishlist_view(request):
    if request.method == "GET":
        wishlist = Wishlist.objects.filter(user=request.user)
        serializer = WishlistSerializer(wishlist, many=True)
        return Response(serializer.data)

    elif request.method == "POST":
        product_id = request.data.get("product")
        if not product_id:
            return Response({"error": "Product ID required"}, status=status.HTTP_400_BAD_REQUEST)
        product = get_object_or_404(Product, id=product_id)
        wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)
        serializer = WishlistSerializer(wishlist_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    elif request.method == "DELETE":
        product_id = request.data.get("product")
        product = get_object_or_404(Product, id=product_id)
        Wishlist.objects.filter(user=request.user, product=product).delete()
        return Response({"success": "Removed from wishlist"}, status=status.HTTP_204_NO_CONTENT)
