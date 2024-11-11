
from django.urls import path
from .views import (
    DepositFundsView, UserBalanceView, ManageWalletView,
    VerifyPaymentView, ConfirmPaymentView, ConfirmedTransactionsView
)
from . import views

app_name = 'payment'
urlpatterns = [
    path('deposit/', DepositFundsView.as_view(), name='deposit_funds'),
    path('balance/', UserBalanceView.as_view(), name='user_balance'),
    path('manage_wallet/', ManageWalletView.as_view(), name='manage_wallet'),
    path('verify_payments/', VerifyPaymentView.as_view(), name='verify_payments'),
    path('confirm_payment/<int:transaction_id>/', ConfirmPaymentView.as_view(), name='confirm_payment'),
    path('confirmed_transactions/', ConfirmedTransactionsView.as_view(), name='confirmed_transactions'),
    path('make_purchase/', views.MakePurchaseView.as_view(), name='make_purchase'),
]
