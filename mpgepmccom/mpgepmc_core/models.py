# mpgepmc_core/models.py
import os
import uuid
from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from django.core.validators import FileExtensionValidator
import random # ⭐️ Import the random module
import string # ⭐️ Import the string module


# Custom upload path for Project images
def project_image_upload_path(instance, filename):
    """
    Generates a unique path for project images.
    Example: 'project_images/my-awesome-project-a1b2c3d4.jpg'
    """
    ext = filename.split('.')[-1]
    sanitized_title = slugify(instance.title)
    unique_hash = uuid.uuid4().hex[:8]
    new_filename = f"{sanitized_title}-{unique_hash}.{ext}"
    return os.path.join('project_images', new_filename)

class Project(models.Model):
    """
    Represents a single welfare or development project.
    """
    class ProjectCategory(models.TextChoices):
        AI_EDUCATION = 'AI_EDUCATION', 'AI Education'
        AI_AWARENESS = 'AI_AWARENESS', 'AI Awareness'
        HUMAN_WELFARE = 'HUMAN_WELFARE', 'Human Welfare'
        DEVELOPMENT = 'DEVELOPMENT', 'Development'

    title = models.CharField(max_length=250, unique=True)
    slug = models.SlugField(max_length=250, unique=True, blank=True, null=True,
                            help_text="A unique URL-friendly version of the project title.")
    category = models.CharField(
        max_length=50,
        choices=ProjectCategory.choices,
        default=ProjectCategory.HUMAN_WELFARE,
        help_text="The main category of the project."
    )
    short_description = models.TextField(max_length=1500, help_text="A brief summary of the project for list pages.")
    full_description = models.TextField(help_text="The full details of the project (HTML is allowed).")
    image = models.ImageField(upload_to=project_image_upload_path, blank=True, null=True,
                                      help_text="Upload a feature image for the project.")
    posted_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=True, help_text="Set to true to make the project visible on the site.")

    class Meta:
        verbose_name = "Welfare Project"
        verbose_name_plural = "Welfare Projects"
        ordering = ['-posted_date']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Auto-generate slug from title if it's not provided
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)




# ⭐️ NEW MODEL FOR BANK ACCOUNT DETAILS ⭐️
class BankAccount(models.Model):
    account_title = models.CharField(max_length=200)
    account_number = models.CharField(max_length=50)
    bank_name = models.CharField(max_length=100)
    iban = models.CharField(max_length=50, verbose_name="IBAN")
    is_active = models.BooleanField(default=True, help_text="Set as the current active account for donations. Only one account should be active at a time.")

    class Meta:
        verbose_name = "Bank Account"
        verbose_name_plural = "Bank Accounts"

    def __str__(self):
        return f"{self.account_title} - {self.bank_name}"


def donation_slip_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    unique_id = instance.donation_order_number or uuid.uuid4().hex[:10]
    new_filename = f"{unique_id}.{ext}"
    return os.path.join('donation_slips', new_filename)


# -----------------------------------------------------
# ⭐️ CORRECTED DONATION MODEL ⭐️
# -----------------------------------------------------
class Donation(models.Model):
    class DonationStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending User Action'
        AWAITING_VERIFICATION = 'AWAITING_VERIFICATION', 'Awaiting Verification'
        COMPLETED = 'COMPLETED', 'Completed'
        FAILED = 'FAILED', 'Failed'

    # Initial Information
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    donation_order_number = models.CharField(max_length=20, unique=True, blank=True)
    status = models.CharField(max_length=30, choices=DonationStatus.choices, default=DonationStatus.PENDING)

    # Verification Information (now required)
    full_name = models.CharField(max_length=150)
    email = models.EmailField()
    transaction_id = models.CharField(max_length=100, verbose_name="Bank Transaction ID / Reference")
    sender_account_name = models.CharField(max_length=150, blank=True, null=True, verbose_name="Sender's Account Name")
    sender_account_number = models.CharField(max_length=50, blank=True, null=True, verbose_name="Sender's Account Number")
    transaction_slip = models.FileField(
        upload_to=donation_slip_upload_path,
        verbose_name="Transaction Slip/Screenshot",
        help_text="Upload a clear JPG, JPEG, PNG, or PDF of the transaction receipt.",
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'pdf'])]
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Store the original status when the model instance is created
        self.__original_status = self.status

    def save(self, *args, **kwargs):
        # ⭐️ UPDATED ORDER NUMBER LOGIC ⭐️
        if not self.donation_order_number:
            # Generate a unique 6-character alphanumeric ID
            while True:
                random_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
                new_order_number = f"MPGepmc-{random_id}"
                # Check if this order number already exists
                if not Donation.objects.filter(donation_order_number=new_order_number).exists():
                    self.donation_order_number = new_order_number
                    break
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Donation Record"
        verbose_name_plural = "Donation Records"
        ordering = ['-created_at']

    def __str__(self):
        return f"Donation {self.donation_order_number} for PKR {self.amount}"



# Custom upload path for MpgService images (existing)
def mpgservice_image_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    sanitized_name = slugify(instance.name)
    unique_hash = uuid.uuid4().hex[:8]
    new_filename = f"{sanitized_name}-{unique_hash}.{ext}"
    return os.path.join('mpgservice_images', new_filename)

# Custom upload path for MpgBlog images (existing)
def mpgblog_image_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    sanitized_title = slugify(instance.title)
    unique_hash = uuid.uuid4().hex[:8]
    new_filename = f"{sanitized_title}-{unique_hash}.{ext}"
    return os.path.join('mpgblog_images', new_filename)


class MpgService(models.Model):
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True, null=True,
                            help_text="A unique URL-friendly version of the service name.") # ADDED SLUG
    short_description = models.TextField(max_length=500, blank=True, null=True)
    full_description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to=mpgservice_image_upload_path, blank=True, null=True,
                              help_text="Upload a feature image for the service (e.g., 800x600 pixels).")
    is_active = models.BooleanField(default=True)
    # New field to indicate if this service has purchasable packages
    has_packages_for_purchase = models.BooleanField(default=False,
        help_text="Check if this service offers distinct packages for direct purchase (e.g., Basic, Premium). If unchecked, only 'Request Service' button will appear.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "MPG Service"
        verbose_name_plural = "MPG Services"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class ServicePackage(models.Model): # NEW MODEL
    service = models.ForeignKey(MpgService, on_delete=models.CASCADE, related_name='packages',
                                help_text="The service this package belongs to.")
    name = models.CharField(max_length=100, help_text="e.g., Basic, Standard, Premium, Enterprise")
    slug = models.SlugField(max_length=100, unique=False, blank=True, null=True,
                            help_text="A unique URL-friendly version of the package name (per service).") # ADDED SLUG
    description = models.TextField(blank=True, null=True, help_text="A short description of this package.")
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price for this package.")
    duration = models.CharField(max_length=100, blank=True, null=True,
                                help_text="e.g., 'Monthly', 'Annually', 'One-time', 'Per Project'")
    is_active = models.BooleanField(default=True, help_text="Is this package currently available for purchase?")
    order = models.IntegerField(default=0, help_text="Order in which packages should be displayed.")

    class Meta:
        verbose_name = "Service Package"
        verbose_name_plural = "Service Packages"
        unique_together = ('service', 'name') # Ensures unique package names per service
        unique_together = ('service', 'slug') # ADDED TO ENSURE SLUG IS UNIQUE PER SERVICE
        ordering = ['order', 'price']

    def __str__(self):
        return f"{self.service.name} - {self.name} (PKR{self.price})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class ServiceFeature(models.Model): # NEW MODEL
    package = models.ForeignKey(ServicePackage, on_delete=models.CASCADE, related_name='features',
                                help_text="The package this feature belongs to.")
    feature_text = models.TextField(help_text="e.g., 10 GB Storage, Priority Support, Custom Reports (HTML allowed)")
    is_included = models.BooleanField(default=True, help_text="Is this feature included in the package?")
    order = models.IntegerField(default=0, help_text="Order in which features should be displayed.")

    class Meta:
        verbose_name = "Service Feature"
        verbose_name_plural = "Service Features"
        ordering = ['order', 'feature_text']

    def __str__(self):
        return f"{self.package.name} - {self.feature_text}"


class MpgBlog(models.Model):
    title = models.CharField(max_length=250, unique=True)
    slug = models.SlugField(max_length=250, unique=True, blank=True, null=True,
                            help_text="A unique URL-friendly version of the title.")
    short_summary = models.TextField(max_length=1500, help_text="A brief summary of the blog post.")
    content = models.TextField(help_text="The full content of the blog post (HTML allowed).")
    feature_image = models.ImageField(upload_to=mpgblog_image_upload_path, blank=True, null=True,
                                      help_text="Upload a feature image for the blog post.")
    posted_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=True, help_text="Set to true to make the blog post live.")

    class Meta:
        verbose_name = "MPG Blog Post"
        verbose_name_plural = "MPG Blog Posts"
        ordering = ['-posted_date']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class ServiceRequest(models.Model):
    mpgservice = models.ForeignKey(MpgService, on_delete=models.SET_NULL, null=True, blank=True,
                                help_text="The MPG service being requested.")
    user_full_name = models.CharField(max_length=100)
    user_email = models.EmailField()
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    user_message = models.TextField(help_text="Details or specific requirements for the service.")
    request_date = models.DateTimeField(auto_now_add=True)
    is_processed = models.BooleanField(default=False)

    class Meta:
        verbose_name = "MPG Service Request"
        verbose_name_plural = "MPG Service Requests"
        ordering = ['-request_date']

    def __str__(self):
        return f"Request for {self.mpgservice.name if self.mpgservice else 'N/A'} by {self.user_full_name}"