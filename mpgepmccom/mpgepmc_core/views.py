# mpgepmc/views.py
import threading
import random # ⭐️ Import the random module
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.views.decorators.http import require_POST

# ⭐️ Make sure Donation and the new forms are imported

import threading
import random
import uuid
from .models import MpgService, MpgBlog, ServiceRequest, ServicePackage, ServiceFeature, Donation, BankAccount, Project
from .forms import ServiceRequestForm, ContactForm, CheckoutForm, DonationAmountForm, DonationVerificationForm

# -----------------------------------------------------
# ⭐️ NEW VIEWS FOR PROJECTS ⭐️
# -----------------------------------------------------

def projects(request):
    """
    Displays a list of all published welfare projects.
    """
    project_list = Project.objects.filter(is_published=True).order_by('-posted_date')
    context = {
        'title': 'Our Projects',
        'projects': project_list,
    }
    return render(request, 'mpgepmc/projects.html', context)


def project_detail(request, project_slug):
    """
    Displays the details for a single project, identified by its slug.
    """
    project = get_object_or_404(Project, slug=project_slug, is_published=True)
    
    # Optional: Get up to 3 other random projects to show as "related"
    related_projects = Project.objects.filter(is_published=True).exclude(pk=project.pk).order_by('?')[:3]

    context = {
        'title': project.title,
        'project': project,
        'related_projects': related_projects,
    }
    return render(request, 'mpgepmc/project_detail.html', context)


# -----------------------------------------------------
# ⭐️ REVISED DONATION VIEWS (THREE-STEP PROCESS) ⭐️
# -----------------------------------------------------

# VIEW 1: Initial page to enter donation amount
def support_page(request):
    if request.method == 'POST':
        form = DonationAmountForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['payment_method'] == 'bank_transfer':
                amount = form.cleaned_data['amount']
                
                # ⭐️ SIMPLIFIED DONATION CREATION ⭐️
                # The model's save() method will now generate the donation_order_number automatically.
                donation = Donation.objects.create(
                    amount=amount,
                    status=Donation.DonationStatus.PENDING
                )
                
                return redirect('mpgepmc_core:donation_checkout', donation_order_number=donation.donation_order_number)
            else:
                messages.error(request, 'The selected payment method is not available yet. Please choose Direct Bank Transfer.')
    else:
        form = DonationAmountForm()

    context = {
        'title': 'Support Our Mission',
        'form': form,
    }
    return render(request, 'mpgepmc/support_initial.html', context)



# ⭐️ NEW VIEW ⭐️

# VIEW 2: Checkout page to display bank details and get verification
def donation_checkout_page(request, donation_order_number):
    donation = get_object_or_404(Donation, donation_order_number=donation_order_number)

    if donation.status != 'PENDING':
        messages.info(request, f"This donation ({donation.donation_order_number}) is already being processed. For updates, please contact us.")
        return redirect('mpgepmc_core:home')

    # ⭐️ Fetch the active bank account from the database ⭐️
    active_bank_account = BankAccount.objects.filter(is_active=True).first()

    if request.method == 'POST':
        form = DonationVerificationForm(request.POST, request.FILES, instance=donation)
        if form.is_valid():
            verified_donation = form.save(commit=False)
            verified_donation.status = Donation.DonationStatus.AWAITING_VERIFICATION
            verified_donation.save()
            
            # --- Send Notification Email ONLY to Admin ---
            admin_email = settings.ADMINS[0][1] if settings.ADMINS else settings.DEFAULT_FROM_EMAIL
            subject_admin = f"Donation Verification Submitted: {verified_donation.donation_order_number}"
            html_message_admin = render_to_string('mpgepmc/email/donation_verification_admin.html', {'donation': verified_donation})
            plain_message_admin = strip_tags(html_message_admin)
            EmailThread(
                subject_admin, plain_message_admin, settings.DEFAULT_FROM_EMAIL, [admin_email], html_message=html_message_admin
            ).start()
            
            return redirect('mpgepmc_core:donation_success', donation_order_number=verified_donation.donation_order_number)
        else:
            messages.error(request, 'Please correct the errors in the form below.')
    else:
        form = DonationVerificationForm(instance=donation)

    context = {
        'title': 'Complete Your Donation',
        'donation': donation,
        'form': form,
        'bank_account': active_bank_account # ⭐️ Pass the account to the template
    }
    
    # ⭐️ Warn the admin in the UI if no bank account is set up
    if not active_bank_account:
        messages.warning(request, 'Bank details are not configured. Please add and activate a bank account in the admin panel to accept donations.')

    return render(request, 'mpgepmc/donation_checkout.html', context)

# ... (The rest of your views.py file remains the same) ...



# VIEW 3: Dedicated success page after submitting verification
def donation_success_page(request, donation_order_number):
    donation = get_object_or_404(Donation, donation_order_number=donation_order_number)
    context = {
        'title': 'Donation Submitted',
        'donation': donation
    }
    return render(request, 'mpgepmc/donation_success.html', context)

# ... (keep EmailThread class and all other views like home, blogs, contact, etc.) ...


# --- EmailThread class remains the same ---
class EmailThread(threading.Thread):
    def __init__(self, subject, plain_message, from_email, recipient_list, html_message):
        self.subject = subject
        self.plain_message = plain_message
        self.from_email = from_email
        self.recipient_list = recipient_list
        self.html_message = html_message
        threading.Thread.__init__(self)

    def run(self):
        try:
            send_mail(
                self.subject,
                self.plain_message,
                self.from_email,
                self.recipient_list,
                html_message=self.html_message,
                fail_silently=False
            )
        except Exception as e:
            print(f"ERROR: Email sending failed in background thread: {e}")


# ⭐️ UPDATED HOME VIEW ⭐️
def home(request):
    # Fetch the 4 most recent services and blogs to create a pool of candidates
    latest_blogs_qs = MpgBlog.objects.filter(is_published=True).order_by('-posted_date')[:4]
    featured_services_qs = MpgService.objects.filter(is_active=True).order_by('-created_at')[:4]

    # Combine the querysets into a single list
    combined_items = list(latest_blogs_qs) + list(featured_services_qs)

    # Randomly shuffle the combined list
    random.shuffle(combined_items)

    # Ensure we don't have more than 8 slides
    slider_items = combined_items[:8]

    # Keep the original queries for the "Our Core Offerings" and "Latest Articles" sections
    featured_services = MpgService.objects.filter(is_active=True).order_by('-created_at')[:4]
    latest_blogs = MpgBlog.objects.filter(is_published=True).order_by('-posted_date')[:4]


    context = {
        'title': 'Home',
        'slider_items': slider_items, # Pass the new shuffled list to the template
        'featured_services': featured_services, # Pass original featured services for the relevant section
        'latest_blogs': latest_blogs, # Pass original latest blogs for the relevant section
    }
    return render(request, 'index.html', context)

# --- Other views (blogs, blog_detail, services, etc.) remain unchanged ---
def blogs(request):
    blog_posts = MpgBlog.objects.filter(is_published=True).order_by('-posted_date')
    context = {
        'title': 'Our Blog',
        'blog_posts': blog_posts,
    }
    return render(request, 'mpgepmc/blogs.html', context)


def blog_detail(request, slug):
    blog_post = get_object_or_404(MpgBlog, slug=slug, is_published=True)

    # Get previous and next posts for navigation
    # Previous post is the first one with a posted_date *before* the current one, in descending order.
    previous_post = MpgBlog.objects.filter(
        is_published=True, 
        posted_date__lt=blog_post.posted_date
    ).order_by('-posted_date').first()

    # Next post is the first one with a posted_date *after* the current one, in ascending order.
    next_post = MpgBlog.objects.filter(
        is_published=True, 
        posted_date__gt=blog_post.posted_date
    ).order_by('posted_date').first()

    # Get up to 4 random posts, excluding the current one
    related_posts = MpgBlog.objects.filter(
        is_published=True
    ).exclude(pk=blog_post.pk).order_by('?')[:3]

    context = {
        'title': blog_post.title,
        'blog_post': blog_post,
        'previous_post': previous_post,
        'next_post': next_post,
        'related_posts': related_posts,
    }
    return render(request, 'mpgepmc/blog_detail.html', context)




def services(request):
    mpgservices_list = MpgService.objects.filter(is_active=True).order_by('name')
    context = {
        'title': 'Our Services',
        'services': mpgservices_list,
    }
    return render(request, 'mpgepmc/services.html', context)

def service_detail(request, service_slug):
    service = get_object_or_404(MpgService, slug=service_slug, is_active=True)
    packages = service.packages.filter(is_active=True).order_by('order')

    context = {
        'title': f'{service.name} Packages',
        'service': service,
        'packages': packages,
    }
    return render(request, 'mpgepmc/service_detail.html', context)

def checkout(request, package_slug):
    package = get_object_or_404(ServicePackage, slug=package_slug, is_active=True)
    service = package.service

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            messages.success(request, f'Proceeding to payment for {package.name}.')
            return redirect('mpgepmc_core:process_payment')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CheckoutForm(initial={'package_id': package.id})

    context = {
        'title': f'Checkout: {package.name}',
        'package': package,
        'service': service,
        'form': form,
    }
    return render(request, 'mpgepmc/checkout.html', context)


@require_POST
def process_payment(request):
    package_id = request.POST.get('package_id_hidden_input')
    package = get_object_or_404(ServicePackage, pk=package_id)

    payment_successful = True

    if payment_successful:
        messages.success(request, f'Your payment for {package.name} was successful! Your order has been placed.')
        return redirect('mpgepmc_core:payment_success_page')
    else:
        messages.error(request, 'Payment failed. Please try again or contact support.')
        return redirect('mpgepmc_core:checkout', package_slug=package.slug)


def payment_success_page(request):
    return render(request, 'mpgepmc/payment_success.html', {'title': 'Payment Successful!'})

def contact(request):
    form = ContactForm()
    context = {
        'title': 'Contact Us',
        'form': form,
    }
    return render(request, 'mpgepmc/contact.html', context)

def contact_form_submit(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            user_full_name = form.cleaned_data['user_full_name']
            user_email = form.cleaned_data['user_email']
            user_phone_number = form.cleaned_data.get('user_phone_number', 'N/A')
            user_message = form.cleaned_data['user_message']

            admin_email = settings.ADMINS[0][1] if settings.ADMINS else settings.DEFAULT_FROM_EMAIL
            subject = f"New Contact Form Submission from {user_full_name}"

            html_message = render_to_string('mpgepmc/email/contact_notification.html', {
                'user_full_name': user_full_name,
                'user_email': user_email,
                'user_phone_number': user_phone_number,
                'user_message': user_message,
                'submission_date': request.META.get('HTTP_REFERER', 'N/A')
            })
            plain_message = strip_tags(html_message)

            EmailThread(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [admin_email],
                html_message=html_message
            ).start()
            
            messages.success(request, 'Your message has been sent successfully! We will get back to you soon.')
            return redirect('mpgepmc_core:thank_you')
        else:
            messages.error(request, 'Please correct the errors below.')
            context = {
                'title': 'Contact Us',
                'form': form,
            }
            return render(request, 'mpgepmc/contact.html', context)
    else:
        return redirect('mpgepmc_core:contact')

def request_service(request, service_slug):
    mpgservice = get_object_or_404(MpgService, slug=service_slug, is_active=True)

    if request.method == 'POST':
        form = ServiceRequestForm(request.POST)
        if form.is_valid():
            service_request = form.save(commit=False)
            service_request.mpgservice = mpgservice
            service_request.save()

            admin_email = settings.ADMINS[0][1] if settings.ADMINS else settings.DEFAULT_FROM_EMAIL
            subject = f"New Service Request: {mpgservice.name} from {service_request.user_full_name}"

            html_message = render_to_string('mpgepmc/email/service_request_notification.html', {
                'service_request': service_request,
                'service_name': mpgservice.name,
                'user_name': service_request.user_full_name,
                'user_email': service_request.user_email,
                'phone_number': service_request.phone_number,
                'user_message': service_request.user_message,
                'request_date': service_request.request_date.strftime("%Y-%m-%d %H:%M %Z")
            })
            plain_message = strip_tags(html_message)

            EmailThread(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [admin_email],
                html_message=html_message
            ).start()

            messages.success(request, 'Your service request has been sent successfully! We will get back to you soon.')
            return redirect('mpgepmc_core:services')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ServiceRequestForm()

    context = {
        'title': f'Request {mpgservice.name}',
        'service': mpgservice,
        'form': form,
    }
    return render(request, 'mpgepmc/request_service.html', context)

def thank_you_page(request):
    return render(request, 'mpgepmc/thank_you.html', {'title': 'Thank You!'})


# ⭐️ NEW VIEW FOR PRIVACY POLICY ⭐️
def privacy_policy_page(request):
    """
    Renders the Privacy Policy page.
    """
    context = {
        'title': 'Privacy Policy'
    }
    return render(request, 'mpgepmc/privacy_policy.html', context)

# ⭐️ NEW VIEW FOR TERMS AND CONDITIONS ⭐️
def terms_and_conditions_page(request):
    """
    Renders the Terms and Conditions page.
    """
    context = {
        'title': 'Terms and Conditions'
    }
    return render(request, 'mpgepmc/terms_and_conditions.html', context)


