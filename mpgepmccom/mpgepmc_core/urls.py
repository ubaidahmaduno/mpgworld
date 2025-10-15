# mpgepmc/urls.py
from django.urls import path
from . import views

app_name = 'mpgepmc_core'

urlpatterns = [
    # Core pages
    path('', views.home, name='home'),
    path('contact/', views.contact, name='contact'),
    # Note: The contact_form_submit URL can be removed if you merge logic into the main contact view
    path('contact/submit/', views.contact_form_submit, name='contact_form_submit'),
    path('thank-you/', views.thank_you_page, name='thank_you'),

    # -----------------------------------------------------
    # ⭐️ REVISED DONATION URLS ⭐️
    # -----------------------------------------------------
    path('support/', views.support_page, name='support'),
    path('support/checkout/<str:donation_order_number>/', views.donation_checkout_page, name='donation_checkout'),
    # ⭐️ NEW URL ⭐️
    path('support/success/<str:donation_order_number>/', views.donation_success_page, name='donation_success'),

    path('services/', views.services, name='services'),
    path('services/<slug:service_slug>/', views.service_detail, name='service_detail'),
    path('services/<slug:service_slug>/request/', views.request_service, name='request_service'),
    
    # ⭐️ NEW URLS FOR PROJECTS ⭐️
    path('projects/', views.projects, name='projects'),
    path('projects/<slug:project_slug>/', views.project_detail, name='project_detail'),

    # Blog pages
    path('blogs/', views.blogs, name='blogs'),
    path('blogs/<slug:slug>/', views.blog_detail, name='blog_detail'),

    # Checkout and Payment Flow
    path('checkout/<slug:package_slug>/', views.checkout, name='checkout'),
    path('payment/process/', views.process_payment, name='process_payment'),
    path('payment/success/', views.payment_success_page, name='payment_success_page'),

    # ⭐️ NEW URLS FOR LEGAL PAGES ⭐️
    path('privacy-policy/', views.privacy_policy_page, name='privacy_policy'),
    path('terms-and-conditions/', views.terms_and_conditions_page, name='terms_and_conditions'),
]
