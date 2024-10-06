from django.conf import settings
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.signals import user_logged_in
from .models.invoice import Invoice
from .models.profile import Profile
from .models.time import Time


@receiver(post_save, sender=Time)
def send_email_on_time_creation(sender, instance, created, **kwargs):
    if created:
        user = instance.user
        username = user.username if user else "Unknown User"
        if user.profile:
            if user.profile.mail:
                subject = f"New Time object created by {username}"
                time_object_url = "https://aclark.net" + reverse(
                    "time_view", kwargs={"pk": instance.pk}
                )
                from_email = settings.DEFAULT_FROM_EMAIL
                html_content = render_to_string(
                    "email_template.html",
                    {
                        "time_object_url": time_object_url,
                        "username": username,
                        "from_email": from_email,
                    },
                )
                plain_message = strip_tags(html_content)
                email = EmailMultiAlternatives(
                    subject,
                    plain_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.DEFAULT_FROM_EMAIL],
                )
                email.attach_alternative(html_content, "text/html")
                email.send()


@receiver(user_logged_in)
def create_profile(sender, user, request, **kwargs):
    if not hasattr(user, "profile"):
        Profile.objects.create(user=user)


@receiver(post_save, sender=Invoice)
def update_invoice(sender, instance, **kwargs):
    if getattr(instance, "_updating", False):
        return
    setattr(instance, "_updating", True)
    # Disconnect the signal temporarily to avoid recursion
    post_save.disconnect(update_invoice_on_time_save, sender=Time)

    times = Time.objects.filter(invoice=instance)
    instance.amount = 0  # Invoice line item "Amount" and total amount
    instance.cost = 0
    instance.hours = 0
    instance.paid_amount = 0
    for time in times:
        if instance.reset:
            time.amount = 0
            time.cost = 0
            time.net = 0
        else:
            try:
                time.cost = time.user.profile.rate * time.hours
            except (AttributeError, TypeError):
                time.cost = 0
            time.amount = time.project.task.rate * time.hours
            time.net = time.amount - time.cost

        if time.amount > 0:
            instance.amount += time.amount

        if time.amount < 0:
            instance.paid_amount += time.amount

        instance.cost += time.cost

        instance.save()
        time.save()

    instance.net = instance.amount - instance.cost

    instance.paid_amount = instance.paid_amount.__neg__()

    instance.balance = instance.amount - instance.paid_amount

    instance.save(
        update_fields=["amount", "cost", "hours", "net", "paid_amount", "balance"]
    )

    # Reconnect the signal after updating the invoice
    post_save.connect(update_invoice_on_time_save, sender=Time)
    delattr(instance, "_updating")


@receiver(post_save, sender=Time)
def update_invoice_on_time_save(sender, instance, **kwargs):
    invoice = instance.invoice
    if invoice:
        update_invoice(Invoice, invoice)


@receiver(post_delete, sender=Time)
def update_invoice_on_time_delete(sender, instance, **kwargs):
    invoice = instance.invoice
    if invoice:
        update_invoice(Invoice, invoice)
