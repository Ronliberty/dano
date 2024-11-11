from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, View
from django.urls import reverse_lazy,  reverse
from .models import UserBalance, Wallet, PaymentConfirmation
from django.contrib.auth.models import Group
from django.contrib import messages
from product.models import CartItem
from .forms import WalletForm

# Ensures only managers (staff) can access
class ManagerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name='manager').exists()

    def handle_no_permission(self):
        return redirect('base:index')


# Deposit funds view for Default Users
class DepositFundsView(LoginRequiredMixin, CreateView):
    model = PaymentConfirmation
    fields = ['amount']
    template_name = 'payment/deposit.html'
    success_url = reverse_lazy('payment:confirm_deposit')

    def form_valid(self, form):
        amount = form.cleaned_data['amount']
        if amount < 20.00:
            form.add_error('amount', "Minimum deposit is $20.")
            return self.form_invalid(form)

        # Create a PaymentConfirmation with a 'Pending' status
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.currency = "USD"
        self.object.status = 'Pending'
        self.object.save()

        wallets = Wallet.objects.all()
        currencies = Wallet.objects.values('currency').distinct()



        # Pass transaction details to the template
        return render(self.request, 'payment/confirm_deposit.html', {
            'transaction_id': self.object.transaction_id,
            'amount': self.object.amount,
            'wallets': wallets,
            'currencies': currencies
        })


# View for Default Users to see their balance
class UserBalanceView(LoginRequiredMixin, DetailView):
    model = UserBalance
    template_name = 'payment/balance.html'

    def get_object(self, queryset=None):
        balance, created = UserBalance.objects.get_or_create(user=self.request.user)
        return balance


# View for Managers to manage wallets

class ManageWalletView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Wallet
    form_class = WalletForm

    template_name = 'payment/manage_wallet.html'
    success_url = reverse_lazy('payment:manage_wallet')

    def test_func(self):
        # Ensure only users in the 'manager' group can access
        return self.request.user.groups.filter(name="manager").exists()

    def get_object(self, queryset=None):
        # Get the first Wallet instance, or create a new one if none exists
        wallet, created = Wallet.objects.get_or_create(id=1)
        return wallet

    def form_valid(self, form):
        wallet = form.save(commit=False)
        wallet.save()
        # Add success message
        messages.success(self.request, "Wallet information saved successfully.")
        # Redirect to success URL
        return redirect('dashboard:manager_dashboard')


# View for Managers to see pending payments
class VerifyPaymentView(LoginRequiredMixin, ManagerRequiredMixin, ListView):
    model = PaymentConfirmation
    template_name = 'payment/verify_payments.html'
    context_object_name = 'payment'

    def get_queryset(self):
        return PaymentConfirmation.objects.filter(status='Pending')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['payments'] = self.get_queryset()
        return context


# View for Managers to confirm a payment
class ConfirmPaymentView(LoginRequiredMixin, ManagerRequiredMixin, DetailView):
    model = PaymentConfirmation
    template_name = 'payment/confirm_payment.html'
    pk_url_kwarg = 'transaction_id'  # Use 'transaction_id' as the URL parameter
    context_object_name = 'payment'

    def get_object(self, queryset=None):
        return get_object_or_404(PaymentConfirmation, transaction_id=self.kwargs.get('transaction_id'))

    def post(self, request, *args, **kwargs):
        # Retrieve the PaymentConfirmation object based on the transaction_id
        payment = self.get_object()

        # Ensure balance is updated for the user
        balance, created = UserBalance.objects.get_or_create(user=payment.user)
        balance.balance += payment.amount
        balance.save()

        # Mark payment as verified
        payment.status = 'Verified'
        payment.save()

        # Redirect to the payment verification page
        return redirect('payment:verify_payments')



# View for Managers to see all confirmed transactions
class ConfirmedTransactionsView(LoginRequiredMixin, ManagerRequiredMixin, ListView):
    model = PaymentConfirmation
    template_name = 'payment/confirmed_transactions.html'
    context_object_name = 'confirmed_payments'

    def get_queryset(self):
        return PaymentConfirmation.objects.filter(status='Verified')


class MakePurchaseView(View):
    def post(self, request, *args, **kwargs):
        user = request.user

        # Ensure the user is only in the "Default" group, remove from others
        default_group, created = Group.objects.get_or_create(name="Default")
        user.groups.clear()  # Clear all existing groups
        user.groups.add(default_group)  # Add only the "Default" group

        # Try to retrieve the user's account balance
        try:
            account = UserBalance.objects.get(user=user)
        except UserBalance.DoesNotExist:
            # If no balance exists, redirect to deposit page with a message
            messages.error(request, "You don't have an account balance. Please deposit funds.")
            return redirect(reverse('payment:deposit_funds'))

        # Retrieve all cart items for the user
        cart_items = CartItem.objects.filter(user=user)

        # Check if the account balance is sufficient for all items
        insufficient_funds = False
        for item in cart_items:
            if account.balance < item.product.price * item.quantity:
                insufficient_funds = True
                break

        if insufficient_funds:
            # If the account balance is less than the price of any product, redirect to deposit
            messages.error(request, "Not enough funds for one or more products. Please top up your account.")
            return redirect(reverse('payment:deposit_funds'))
        else:
            # If the account balance is sufficient for all products, proceed to success
            # No actual payment is made, it's for learning purposes
            messages.success(request, "Purchase successful!")

            # Delete the cart items after the "purchase"
            cart_items.delete()

            # Redirect to purchase success page
            return redirect(reverse('product:purchase_success'))