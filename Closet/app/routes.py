from flask import render_template, redirect, url_for, flash, request, jsonify, Blueprint, current_app
from flask_login import current_user, login_user, logout_user, login_required
from app import db, login_manager
from app.models import User, Item
from app.forms import LoginForm, RegistrationForm # Assume you have these forms
import os

bp = Blueprint('main', __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@bp.route('/')
@bp.route('/index')
def index():
    return render_template('index.html', title='Home')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('main.login'))
    return render_template('register.html', title='Register', form=form)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('main.login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('main.index'))
    return render_template('login.html', title='Sign In', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/closet')
@login_required
def closet():
    items = current_user.items.all()
    return render_template('closet.html', title='My Closet', items=items)

# --- Premium Features and Payment Gateway Integration (Placeholder) ---

@bp.route('/premium')
@login_required
def premium_page():
    # Display information about premium features and offer a payment option
    return render_template('premium.html', title='Premium Features',
                           public_key=current_app.config['PAYMENT_GATEWAY_PUBLIC_KEY'],
                           price=current_app.config['PREMIUM_TIER_PRICE'],
                           currency=current_app.config['PREMIUM_TIER_CURRENCY'])

# This is a placeholder for initiating a payment
# In a real scenario, you'd interact with your chosen gateway's SDK/API
@bp.route('/initiate-payment', methods=['POST'])
@login_required
def initiate_payment():
    # --- Replace this with your chosen payment gateway's logic ---
    # Example: If using a gateway that requires a client-side redirect or token
    try:
        # Simulate creating a payment session or obtaining a token
        # For example, with PayPal, you'd create an order and get an orderID
        # For other gateways, you might generate a payment token or redirect URL

        # For demonstration, we'll just pretend it worked and redirect to a payment form
        # In a real integration, you'd likely return JSON with details for JS to handle
        # or redirect directly to the gateway's payment page.

        # Placeholder for payment initiation logic
        payment_details = {
            'amount': current_app.config['PREMIUM_TIER_PRICE'],
            'currency': current_app.config['PREMIUM_TIER_CURRENCY'],
            # Add any other necessary details like return URLs, customer info, etc.
        }

        # Flash a message indicating payment initiation and redirect to a form
        # where the actual payment might be processed client-side or via redirect.
        flash("Redirecting to payment processor...")
        # You'd likely redirect to a page that handles the actual payment form
        # or a JS SDK call. For simplicity, let's simulate success and update the user.
        # In a real app, this would be a more complex flow.

        # For simulation purposes:
        return jsonify({"success": True, "message": "Payment initiated. Please complete on the next page."})

    except Exception as e:
        current_app.logger.error(f"Payment initiation failed: {e}")
        return jsonify({"success": False, "message": "Payment initiation failed. Please try again."}), 500

# This route would be called after a successful payment
# (e.g., via a webhook from your payment gateway or a redirect)
@bp.route('/payment-callback', methods=['GET', 'POST'])
@login_required
def payment_callback():
    # --- This route handles the result of a payment ---
    # You'll need to parse the request based on how your payment gateway
    # communicates the payment status (e.g., query parameters in GET,
    # webhook events, or data posted from a payment form).

    payment_successful = request.args.get('payment_status') == 'success' # Example parameter

    if payment_successful:
        # Update the user's premium status
        current_user.is_premium = True
        # Store relevant payment gateway details (e.g., subscription ID, transaction ID)
        # current_user.payment_gateway_customer_id = request.args.get('customer_id')
        # current_user.payment_gateway_subscription_id = request.args.get('subscription_id')
        db.session.commit()
        flash('Congratulations! Your account has been upgraded to premium.')
        return render_template('success.html', title='Payment Successful')
    else:
        flash('Payment failed or was cancelled. Please try again.')
        return redirect(url_for('main.premium_page'))

# Example of a route that requires premium access
@bp.route('/premium-feature')
@login_required
def premium_feature():
    if not current_user.is_premium:
        flash('You need to be a premium user to access this feature.')
        return redirect(url_for('main.premium_page'))

    return render_template('premium_feature.html', title='Premium Feature') # Create this template