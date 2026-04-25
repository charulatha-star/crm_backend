from django.db import models
from django.utils import timezone
from django.contrib.auth.hashers import make_password


class Customer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()

    def __str__(self):
        return self.name


class Client(models.Model):

    COUNTRY = [('India', 'India'), ('USA', 'USA'), ('UK', 'UK'), ('China', 'China')]
    BILLING_CURRENCY = [('INR', 'INR'), ('USD', 'USD')]
    PAYMENT_TYPE = [('Prepaid', 'Prepaid'), ('Postpaid', 'Postpaid')]
    PAYMENT_TERM = [('15 Days', '15 Days'), ('30 Days', '30 Days'), ('45 Days', '45 Days')]

    # CLIENT BASIC
    client_id = models.CharField(max_length=20, unique=True, editable=False)
    reporting_id = models.CharField(max_length=20, blank=True, null=True)

    client_name = models.CharField(max_length=100)
    phone_no = models.CharField(max_length=10)
    email = models.EmailField()

    address_line1 = models.CharField(max_length=300)
    address_line2 = models.CharField(max_length=200, blank=True, null=True)
    country = models.CharField(max_length=50, choices=COUNTRY)
    zipcode = models.CharField(max_length=10)

    # PAYMENT
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE)
    payment_term = models.CharField(max_length=20, choices=PAYMENT_TERM)
    billing_currency = models.CharField(max_length=10, choices=BILLING_CURRENCY)

    # TAX
    gst_no = models.CharField(max_length=20, blank=True, null=True)
    cin_no = models.CharField(max_length=30, blank=True, null=True)

    # STATUS
    is_active = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True)

    # CONTACT
    contact_name = models.CharField(max_length=255)
    contact_phone = models.CharField(max_length=10, blank=True, null=True)
    contact_email = models.EmailField()
    contact_country = models.CharField(max_length=100)
    contact_zipcode = models.CharField(max_length=20)
    contact_address_1 = models.CharField(max_length=300)
    contact_address_2 = models.CharField(max_length=300, blank=True, null=True)
    contact_designation = models.CharField(max_length=255, blank=True, null=True)
    #contact_signature = models.FileField(upload_to="signatures/")
    contact_signature = models.FileField(upload_to="signatures/",null=True,blank=True)

    # COMPANY ADDRESS
    company_address_line1 = models.CharField(max_length=300)
    company_address_line2 = models.CharField(max_length=300, blank=True, null=True)
    company_country = models.CharField(max_length=50, choices=COUNTRY)
    company_zipcode = models.CharField(max_length=10)

    # LOGIN
    user_email = models.EmailField(unique=True, blank=True, null=True)
    user_password = models.CharField(max_length=128, blank=True, null=True)

    # ✅ FIXED SAVE METHOD
    def save(self, *args, **kwargs):

        # 🔐 Hash password
        if self.user_password and not self.user_password.startswith('pbkdf2_'):
            self.user_password = make_password(self.user_password)

        # 🔥 Generate Client ID
        if not self.client_id:
            year = timezone.now().year

            last_client = Client.objects.filter(
                client_id__startswith=f"CLT-{year}-"
            ).order_by('id').last()

            if last_client:
                last_number = int(last_client.client_id.split('-')[-1])
                new_number = last_number + 1
            else:
                new_number = 1

            self.client_id = f"CLT-{year}-{new_number:05d}"

        super().save(*args, **kwargs)

    # ✅ Correct position
    def __str__(self):
        return f"{self.client_id} - {self.client_name}"










'''
    def save(self, *args, **kwargs):
        if not self.client_id:
            year = timezone.now().year

            last_client = Client.objects.filter(
                client_id__startswith=f"CLT-{year}-"
            ).order_by('id').last()

            if last_client:
                last_number = int(last_client.client_id.split('-')[-1])
                new_number = last_number + 1
            else:
                new_number = 1

            self.client_id = f"CLT-{year}-{new_number:05d}"

        super().save(*args, **kwargs)

        def __str__(self):
            return f"{self.client_id} - {self.client_name}"
    '''
