from django.contrib import messages
from django.contrib.auth import logout, login
from django.contrib.auth.hashers import check_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, View, FormView

from core.forms import SubscriptionForm, LoginForm, RegisterModelForm
from core.models import ProductCategory, Product, Favourite, Tag, OrderItem, Order, Post, Subscription, User


class HomeTemplateView(LoginRequiredMixin,ListView):
    login_url = 'login'
    queryset = ProductCategory.objects.all()
    template_name = 'core/index.html'
    context_object_name = 'categories'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        best_sellings = Product.objects.filter(is_featured=False)[:6]
        user_favourites = Favourite.objects.filter(user=self.request.user)
        featured_products = Product.objects.filter(is_featured=True)
        arrived_products = Product.objects.all().order_by('-id')[:6]
        favourite_product_ids = user_favourites.values_list('product_id', flat=True)
        for product in best_sellings:
            product.is_liked = product.id in favourite_product_ids
        for product in featured_products:
            product.is_liked = product.id in favourite_product_ids
        for product in arrived_products:
            product.is_liked = product.id in favourite_product_ids

        latest_order = Order.objects.filter(user=self.request.user).order_by('-id').first()
        data['best_sellings'] = best_sellings
        data['tags'] = Tag.objects.all()
        data['featured_products'] = featured_products
        data['latest_order'] = latest_order
        data['cart_items'] = OrderItem.objects.select_related('order').select_related('product').filter(order__user=self.request.user)
        data['arrived_products'] = arrived_products
        data['posts'] = Post.objects.select_related('category').all()
        return data

class OrderItemView(LoginRequiredMixin, View):
    login_url = 'login'
    def post(self, request):
        product_id = request.GET.get('product_id')
        quantity = int(request.POST.get('quantity', 1))

        if quantity <= 0:
            return redirect('home')

        product = Product.objects.get(id=product_id)

        order, created = Order.objects.get_or_create(user=request.user, order_billing=None)

        order_item, item_created = OrderItem.objects.get_or_create(order=order, product=product)

        if item_created:
            order_item.quantity = quantity
        else:
            order_item.quantity += quantity

        order_item.save()
        return redirect('home')

class FavouriteView(LoginRequiredMixin,View):
    login_url = 'login'
    def get(self, request):
        product_id = request.GET.get('product_id')
        query = Favourite.objects.filter(product_id=product_id, user=request.user)
        if query.exists():
            query = query.first()
            query.delete()
        else:
            Favourite.objects.create(product_id=product_id, user=request.user)
        return redirect('home')

class SearchView(LoginRequiredMixin, View):
    login_url = 'login'
    def post(self, request):
        search = request.POST.get('search')
        category = request.POST.get('category')
        user_favourites = Favourite.objects.filter(user=self.request.user)
        favourite_product_ids = user_favourites.values_list('product_id', flat=True)
        if search and category == 'all':
            products = Product.objects.select_related('category_id').filter(name__icontains=search)
            print(products)
        elif not search and category:
            products = Product.objects.select_related('category_id').filter(category_id__name=category)
        else:
            products = Product.objects.select_related('category_id').filter(category_id__name=category, name__in=search)
            print("second")
        for product in products:
            product.is_liked = product.id in favourite_product_ids
        categories = ProductCategory.objects.all()
        context = {
            'best_sellings': products,
            'categories': categories,
        }
        print(search, category)
        return render(request, 'core/search_results.html', context)
    def get(self, request):
        categories = ProductCategory.objects.all()
        best_sellings = Product.objects.select_related('category_id').all()
        context = {
            'categories': categories,
            'best_sellings': best_sellings,
        }
        return render(request, 'core/search_results.html', context)


class SubscriptionCreateView(CreateView):
    model = Subscription
    form_class = SubscriptionForm
    template_name = 'core/index.html'
    success_url = reverse_lazy('home')



class RegisterCreatView(CreateView):
    queryset = User.objects.all()
    form_class = RegisterModelForm
    template_name = 'core/register.html'
    success_url = reverse_lazy('login')
    context_object_name = 'users'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['categories'] = ProductCategory.objects.all()
        return data


class LoginFormView(FormView):
    form_class = LoginForm
    template_name = 'core/login.html'
    success_url = reverse_lazy('home')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['categories'] = ProductCategory.objects.all()
        return data

    def form_valid(self, form):
        users = {
            'password': form.cleaned_data.get('password'),
            'email': form.cleaned_data.get('email')
        }
        query = User.objects.filter(email=users.get('email'))
        if query.exists():
            user = query.first()
            if check_password(users.get('password'), user.password):
                login(self.request, user)
            else:
                messages.error(self.request, 'Password incorrect!')
                return redirect('login')
        else:
            messages.error(self.request, f'{users.get('email')} exist! ')
            return redirect('login')
        return super().form_valid(form)
    def form_invalid(self, form):
        messages.error(self.request, 'Invalid credentials!')
        return redirect('login')

class LogoutView(View):
    def get(self,request):
        logout(request)
        return redirect('login')
