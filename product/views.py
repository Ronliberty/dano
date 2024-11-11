from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View, TemplateView
from .models import Category, Product, ProductVariant, ProductImage, DiscountCode, Review, ProductQuestion, ProductAnswer, ProductAnalytics, Wishlist, CartItem, Order, OrderStatusHistory
from django.urls import reverse
from .forms import ProductForm
from django.contrib.auth.models import Group
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import UserPassesTestMixin


class ManagerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        # Check if the user is authenticated and belongs to the 'manager' group
        return self.request.user.is_authenticated and self.request.user.groups.filter(name='manager').exists()

    def handle_no_permission(self):
        # Optional: Redirect to login or raise PermissionDenied
        raise PermissionDenied("You do not have permission to access this page.")

# List all categories
class CategoryListView(ManagerRequiredMixin,ListView):
    model = Category
    template_name = 'product/category_list.html'  # Updated with app name
    context_object_name = 'categories'


# Detailed view of a specific category
class CategoryDetailView(ManagerRequiredMixin,DetailView):
    model = Category
    template_name = 'product/category_detail.html'  # Updated with app name
    context_object_name = 'category'


# Create a new category
class CategoryCreateView(ManagerRequiredMixin,CreateView):
    model = Category
    fields = ['name', 'description']
    template_name = 'product/category_form.html'  # Updated with app name
    success_url = reverse_lazy('product:category-list')


# Update an existing category
class CategoryUpdateView(ManagerRequiredMixin,UpdateView):
    model = Category
    fields = ['name', 'description']
    template_name = 'product/category_form.html'  # Updated with app name
    success_url = reverse_lazy('product:category-list')


# Delete a category
class CategoryDeleteView(ManagerRequiredMixin,DeleteView):
    model = Category
    template_name = 'product/category_confirm_delete.html'  # Updated with app name
    success_url = reverse_lazy('product:category-list')


### Product Views ###

# List all products
class ProductListView(ListView):
    model = Product
    template_name = 'product/product_list.html'  # Updated with app name
    context_object_name = 'products'

class ProductUpdatedListView(ManagerRequiredMixin, LoginRequiredMixin, ListView):
    model = Product
    template_name = 'product/product_updated_list.html'
    context_object_name = 'updated_products'

    def get_queryset(self):
        # Filter products to include only those updated by the logged-in user
        return super().get_queryset().filter(manager=self.request.user).order_by('-updated_at')

# Detailed view of a product
class ProductDetailView(DetailView):
    model = Product
    template_name = 'product/product_detail.html'  # Updated with app name
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['variants'] = self.object.variants.all()
        context['reviews'] = self.object.reviews.all()
        context['analytics'] = getattr(self.object, 'analytics', None)
        return context


# Create a new product
class ProductCreateView(ManagerRequiredMixin,CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'product/product_form.html'
    login_url = '/login/'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Populate the category choices
        form.fields['category'].queryset = Category.objects.all()  # Fetch all categories
        return form

    def form_valid(self, form):
        form.instance.seller = self.request.user
        self.object = form.save()
        return super().form_valid(form)

    def get_success_url(self):
        # Redirect to the product detail page of the created product
        return reverse('product:product-detail', kwargs={'pk': self.object.pk})

# Update a product
class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    fields = ['category', 'name', 'description', 'price', 'discount_percentage', 'stock', 'image']
    template_name = 'product/product_form.html'
    success_url = reverse_lazy('product:product-list')

    def dispatch(self, request, *args, **kwargs):
        # Check if the user belongs to the 'manager' group
        if not request.user.groups.filter(name="manager").exists():
            raise PermissionDenied("You do not have permission to edit this product.")
        return super().dispatch(request, *args, **kwargs)


# Delete a product
class ProductDeleteView(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = 'product/product_confirm_delete.html'
    success_url = reverse_lazy('product:product-list')

    def get_queryset(self):
        # Filter by the 'manager' field to ensure only the products managed by the user are available for deletion
        return super().get_queryset().filter(manager=self.request.user)

    def dispatch(self, request, *args, **kwargs):
        # Check if the user belongs to the 'manager' group
        if not request.user.groups.filter(name='manager').exists():
            raise PermissionDenied("You do not have permission to delete this product.")
        return super().dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        # Ensure that the user is the manager of the product
        self.object = self.get_object()
        if self.object.manager != request.user:
            raise PermissionDenied("You do not have permission to delete this product.")
        return super().delete(request, *args, **kwargs)

### Review Views ###

# Create a review for a product
class ReviewCreateView(CreateView):
    model = Review
    fields = ['rating', 'comment']
    template_name = 'product/review_form.html'  # Updated with app name

    def form_valid(self, form):
        form.instance.product = get_object_or_404(Product, pk=self.kwargs['product_id'])
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('product:product-detail', kwargs={'pk': self.kwargs['product_id']})


### Wishlist Views ###

# Display a user's wishlist
class WishlistView(ListView):
    model = Wishlist
    template_name = 'product/wishlist.html'  # Updated with app name
    context_object_name = 'wishlist'

    def get_queryset(self):
        return Wishlist.objects.get_or_create(user=self.request.user)


def add_to_wishlist(request, product_id):

    product = get_object_or_404(Product, pk=product_id)


    wishlist, created = Wishlist.objects.get_or_create(user=request.user)


    wishlist.products.add(product)

    return redirect('product:wishlist')


### Order Views ###

# List all orders for a user
class OrderListView(ListView):
    model = Order
    template_name = 'product/order_list.html'  # Updated with app name
    context_object_name = 'orders'

    def get_queryset(self):
        return Order.objects.filter(customer=self.request.user)



class OrderDetailView(DetailView):
    model = Order
    template_name = 'product/order_detail.html'  # Updated with app name
    context_object_name = 'order'

    def get_queryset(self):
        return Order.objects.filter(customer=self.request.user)


# Update the status of an order (for admin or staff)
class OrderStatusUpdateView(UpdateView):
    model = Order
    fields = ['status']
    template_name = 'product/order_status_form.html'  # Updated with app name
    success_url = reverse_lazy('product:order-list')


class AddToCartView(View):
    def post(self, request, pk):
        # Get the product using the pk
        product = get_object_or_404(Product, pk=pk)

        # Add product to cart (your logic here)
        cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)

        # You can adjust the quantity or other cart item properties here
        cart_item.quantity += 1  # Example increment
        cart_item.save()

        # Redirect to the cart page or a success page
        return redirect('product:cart-detail')



class CartView(LoginRequiredMixin, View):
    login_url = '/login/'  # Optional, specify where users should be redirected if not logged in
    template_name = 'product/cart_detail.html'

    def get(self, request):
        # Retrieve all cart items for the logged-in user
        cart_items = CartItem.objects.filter(user=request.user)
        return render(request, self.template_name, {'cart_items': cart_items})

class PurchaseSuccessView(TemplateView):
    template_name = 'product/purchase_success.html'

