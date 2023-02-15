from django.db import models

from accounts.models import User, UserProfile
from accounts.utils import send_notification
from datetime import time, date, datetime



class Vendor(models.Model):
    user = models.OneToOneField(User, related_name="user", on_delete=models.CASCADE)
    user_profile = models.OneToOneField(
        UserProfile, related_name="userprofile", on_delete=models.CASCADE
    )
    vendor_name = models.CharField(max_length=100)
    vendor_slug = models.SlugField(max_length=100, unique=True)
    vendor_license = models.ImageField(upload_to="vendor/license")
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.vendor_name


    def is_open(self):
        today = date.today()
        today = today.isoweekday()
        
        current_opening_hours = OpeningHour.objects.filter(vendor=self, day=today)
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        
        is_open=None
        for i in current_opening_hours:
            if not i.is_closed:
                start = str(datetime.strptime(i.from_hour, '%I:%M %p').time())
                end = str(datetime.strptime(i.to_hour, '%I:%M %p').time())
                is_open = current_time>start and current_time<end
            
        return is_open
    
        

    def save(self, *args, **kwargs):
        if self.pk:
            orig = Vendor.objects.get(pk=self.pk)
            if orig.is_approved != self.is_approved:
                mail_template = "accounts/emails/admin_approval_email.html"
                context = {
                    "user": self.user,
                    "is_approved": self.is_approved,
                }
                if self.is_approved:
                    mail_subject = "Your restaurant has been approved"
                else:
                    mail_subject = (
                        "Your restaurant is not eligible for FoodOnline Marketplace"
                    )
                send_notification(mail_subject, mail_template, context)
        return super(Vendor, self).save(*args, **kwargs)



class OpeningHour(models.Model):
    DAYS = [
    (1, ("Monday")),
    (2, ("Tuesday")),
    (3, ("Wednesday")),
    (4, ("Thursday")),
    (5, ("Friday")),
    (6, ("Saturday")),
    (7, ("Sunday")),
    ]

    HOURS_OF_DAY_24 = [
        (time(h, m).strftime('%I:%M %p'), time(h, m).strftime('%I:%M %p'))
        for h in range(24)
        for m in range(0, 60, 30)
    ]


    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    day = models.IntegerField(choices=DAYS)
    from_hour = models.CharField(choices=HOURS_OF_DAY_24, max_length=10, blank=True)
    to_hour = models.CharField(choices=HOURS_OF_DAY_24, max_length=10, blank=True)
    is_closed =  models.BooleanField(default=False)

    class Meta:
        ordering = ('day', '-from_hour')
        # simply add from_hour and to_hour to the unique_together tuple to allow multiple opening hours for the same day (i.e 11am-2pm and 5pm-8pm)
        unique_together = ('vendor', 'day')
        
    def __str__(self):
        return self.get_day_display()