class CartMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if 'cart' not in request.session:
            request.session['cart'] = {}
        
        # Calculate cart total
        cart = request.session.get('cart', {})
        cart_count = sum(item.get('quantity', 0) for item in cart.values())
        request.cart_count = cart_count
        
        response = self.get_response(request)
        return response
