import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Configuration for your chosen payment gateway (example placeholders)
    PAYMENT_GATEWAY_PUBLIC_KEY = os.environ.get('PAYMENT_GATEWAY_PUBLIC_KEY')
    PAYMENT_GATEWAY_SECRET_KEY = os.environ.get('PAYMENT_GATEWAY_SECRET_KEY')
    # You'll need to define your own premium feature tiers and prices
    PREMIUM_TIER_PRICE = 9.99 # Example price in USD
    PREMIUM_TIER_CURRENCY = 'usd'