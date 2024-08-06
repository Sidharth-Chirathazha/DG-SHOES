// checkout.js
function applyCoupon() {
    const couponCode = document.getElementById('coupon-input').value;

    if (!couponCode) {
        alert('Please enter a coupon code.');
        return;
    }

    fetch('/apply_coupon/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: `coupon_code=${encodeURIComponent(couponCode)}`
    })
    .then(response => response.json())
    .then(data => {
        const messageElement = document.getElementById('coupon-message');
        if (data.status === 'success') {
            messageElement.textContent = data.message;
            messageElement.style.color = 'green';
            updatePriceInfo(data.cart_total, data.discount, data.new_total);
            document.getElementById('remove-coupon').style.display = 'inline-block';
        } else {
            messageElement.textContent = data.message;
            messageElement.style.color = 'red';
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while applying the coupon.');
    });
}

function removeCoupon() {
    fetch('/remove_coupon/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            document.getElementById('coupon-input').value = '';
            document.getElementById('coupon-message').textContent = '';
            document.getElementById('remove-coupon').style.display = 'none';
            updatePriceInfo(data.cart_total, '0', data.cart_total);
        } else {
            alert('Failed to remove coupon.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while removing the coupon.');
    });
}

function updatePriceInfo(cartTotal, discount, newTotal) {
    document.getElementById('discount-info').style.display = 'block';
    document.getElementById('discount-amount').textContent = discount;
    document.getElementById('discounted-total').textContent = newTotal;

    // Update sidebar
    document.getElementById('sidebar-subtotal').textContent = cartTotal;
    document.getElementById('sidebar-discount').textContent = discount;
    document.getElementById('sidebar-grand-total').textContent = newTotal;

    // Update order summary
    document.getElementById('cart-subtotal').textContent = cartTotal;
    document.querySelector('#checkout-review-table tfoot .price-wrapper .price').textContent = discount;
    document.getElementById('cart-grand-total').textContent = newTotal;
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Add event listeners for radio buttons
document.querySelectorAll('input[name="coupon_code"]').forEach(radio => {
    radio.addEventListener('change', function() {
        if (this.checked) {
            document.getElementById('coupon-input').value = this.value;
            applyCoupon();
        }
    });
});