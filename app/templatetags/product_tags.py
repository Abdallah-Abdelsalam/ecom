from django import template
import math

register = template.Library()

@register.simple_tag
def call_sellprice(price, discount):
    try:
        # Ensure price and discount are converted to floats before operations
        price = float(price)
        discount = float(discount) if discount else 0  # Convert discount to float or default to 0 if None
        
        if discount == 0:
            return price
        
        # Calculate the sell price after applying discount
        sellprice = price - (price * discount / 100)
        
        # Use math.floor to return the rounded-down price
        return math.floor(sellprice)
    
    except (ValueError, TypeError):
        # If there are any issues with type conversion, return the original price
        return price
