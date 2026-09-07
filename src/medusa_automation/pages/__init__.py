"""Page objects for the Medusa automation framework."""

from .account_page import AccountPage
from .base_page import BasePage
from .cart_page import CartPage
from .catalog_page import CatalogPage
from .checkout_page import CheckoutAddress, CheckoutPage
from .customer_login_page import CustomerLoginPage
from .login_page import LoginPage
from .order_confirmation_page import OrderConfirmationPage
from .product_page import ProductPage

__all__ = [
    "AccountPage",
    "BasePage",
    "CartPage",
    "CatalogPage",
    "CheckoutAddress",
    "CheckoutPage",
    "CustomerLoginPage",
    "LoginPage",
    "OrderConfirmationPage",
    "ProductPage",
]
