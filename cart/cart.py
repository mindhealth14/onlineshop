from decimal import Decimal
from django.conf import settings
from shop.models import Product




class Cart:
    def __init__(self, request):
        """
           initialize the Cart.           
        """
        
        self.session = request.session 
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            #Save on empty cart in session
            cart = self.session[settings.CART_SESSION_ID] = {}
            #move self.cart outside the if statement
        self.cart = cart

     # We are creating a method to add product to the empty cart
    def add(self, product, quantity=1, override_quantity = False):
        """
        Add a product to the cart of update its quantity
        """
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {
                'quantity': 0,
                'price': str(product.price)
            }
        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()

    def save(self):
        #mark the session as "modified" to make sure it get saved
        self.session.modified = True

    def remove(self, product):
        """
        Remove a product from cart
        """
        product_id = str(product.id)

        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):

        """
        To iterate over the items in the cart and get products from database
        """

        product_ids = self.cart.keys()
        #get the product object and add them to the cart
        products = Product.objects.filter(id__in=product_ids)
        cart = self.cart.copy()
        for product in products:
            cart[str(product.id)] ['product'] = product
        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        """
        Count all items in the cart
        """
        return sum(item['quantity'] for item in self.cart.values())
    
    def get_total_price(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())
    
    def clear(self):
        # clear or empty the cart method 
        del self.session[settings.CART_SESSION_ID]
        self.save()




