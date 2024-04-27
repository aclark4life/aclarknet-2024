# views.py
from django.shortcuts import render, redirect
from .forms import SubscriberForm, NewsletterForm
from .models import Subscriber, Newsletter


def subscribe(request):
    if request.method == "POST":
        form = SubscriberForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("subscribe_success")
    else:
        form = SubscriberForm()
    return render(request, "subscribe.html", {"form": form})


def subscribe_success(request):
    return render(request, "subscribe_success.html")


def send_newsletter(request):
    if request.method == "POST":
        form = NewsletterForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data["subject"]
            content = form.cleaned_data["content"]
            subscribers = Subscriber.objects.all()
            # Code for sending email to subscribers with subject and content
            # You'll need to implement this part using Django's Email functionality
            # For simplicity, let's assume the emails are sent successfully
            Newsletter.objects.create(subject=subject, content=content)
            return redirect("newsletter_sent")
    else:
        form = NewsletterForm()
    return render(request, "send_newsletter.html", {"form": form})


def newsletter_sent(request):
    return render(request, "newsletter_sent.html")


def newsletter(request):
    latest_newsletter = Newsletter.objects.order_by("-created_at").first()
    return render(request, "newsletter.html", {"latest_newsletter": latest_newsletter})
