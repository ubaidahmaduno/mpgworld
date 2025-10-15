# mpgepmc_core/forms.py
from django import forms
from .models import ServiceRequest, Donation

class ServiceRequestForm(forms.ModelForm):
    user_full_name = forms.CharField(
        label="Your Full Name", max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Enter your full name'}),
        help_text="E.g., John Doe"
    )
    user_email = forms.EmailField(
        label="Your Email Address",
        widget=forms.EmailInput(attrs={'placeholder': 'you@example.com'}),
        help_text="We'll use this to contact you back."
    )
    phone_number = forms.CharField(
        label="Phone Number (Optional)", max_length=20, required=False,
        widget=forms.TextInput(attrs={'placeholder': '+92 3XX XXXXXXX'}),
        help_text="For a quicker response if needed."
    )
    user_message = forms.CharField(
        label="Your Message/Requirements",
        widget=forms.Textarea(attrs={'rows': 5, 'placeholder': 'Describe your specific needs or questions...'}),
        help_text="Tell us more about what you're looking for."
    )
    class Meta:
        model = ServiceRequest
        fields = ['user_full_name', 'user_email', 'phone_number', 'user_message']

class ContactForm(forms.Form):
    user_full_name = forms.CharField(
        label="Your Full Name", max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Enter your full name', 'class': 'form-control'}),
    )
    user_email = forms.EmailField(
        label="Your Email Address",
        widget=forms.EmailInput(attrs={'placeholder': 'you@example.com', 'class': 'form-control'}),
    )
    user_phone_number = forms.CharField(
        label="Phone Number (Optional)", max_length=20, required=False,
        widget=forms.TextInput(attrs={'placeholder': '+92 3XX XXXXXXX', 'class': 'form-control'}),
    )
    user_message = forms.CharField(
        label="Your Message",
        widget=forms.Textarea(attrs={'rows': 6, 'placeholder': 'Type your message or inquiry here...', 'class': 'form-control'}),
    )

class CheckoutForm(forms.Form):
    user_full_name = forms.CharField(
        label="Your Full Name", max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Enter your full name', 'class': 'form-control'}),
    )
    user_email = forms.EmailField(
        label="Your Email Address",
        widget=forms.EmailInput(attrs={'placeholder': 'you@example.com', 'class': 'form-control'}),
    )
    package_id = forms.IntegerField(widget=forms.HiddenInput())


class DonationAmountForm(forms.Form):
    PAYMENT_CHOICES = [
        ('bank_transfer', 'Direct Bank Transfer'),
        ('paypal', 'PayPal'),
        ('card', 'Credit/Debit Card'),
    ]

    amount = forms.DecimalField(
        min_value=1.00,
        max_digits=12,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control form-control-lg text-center',
            'placeholder': 'Enter Donation Amount (PKR)',
            'aria-label': 'Donation Amount'
        }),
        label=""
    )
    payment_method = forms.ChoiceField(
        choices=PAYMENT_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        initial='bank_transfer',
        label="Select Payment Method"
    )


class DonationVerificationForm(forms.ModelForm):
    full_name = forms.CharField(
        label="Full name",
        widget=forms.TextInput(attrs={'placeholder': 'Your full name as per bank records'}),
        required=True
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={'placeholder': 'you@example.com'}),
        required=True
    )
    transaction_id = forms.CharField(
        label="Bank Transaction ID / Reference",
        widget=forms.TextInput(attrs={'placeholder': 'The reference from your transaction'}),
        required=True
    )
    transaction_slip = forms.FileField(
        label="Transaction Slip/Screenshot",
        help_text="Upload a clear JPG, JPEG, PNG, or PDF of the transaction receipt.",
        required=True
    )

    class Meta:
        model = Donation
        fields = [
            'full_name', 'email', 'transaction_id',
            'sender_account_name', 'sender_account_number', 'transaction_slip'
        ]
        widgets = {
            'sender_account_name': forms.TextInput(attrs={'placeholder': "Optional: Sender's Account Name"}),
            'sender_account_number': forms.TextInput(attrs={'placeholder': "Optional: Sender's Account Number"}),
            # The FileInput widget is handled by the explicit field definition above
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply the 'form-control' class to all visible fields for consistent styling
        for field_name, field in self.fields.items():
            # The custom file input in the template handles its own styling
            if field_name != 'transaction_slip':
                current_attrs = field.widget.attrs
                current_attrs.update({'class': 'form-control'})





