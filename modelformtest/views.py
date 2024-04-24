from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.mixins import UserPassesTestMixin
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DetailView,
    View,
    DeleteView,
)
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import reverse
from django.shortcuts import render
from .forms import MarketingEmailMessageForm
from .forms import TestModelForm
from faker import Faker
from django.urls import reverse_lazy
from .models import TestModel, MarketingEmailMessage
import hashlib

logo = "iVBORw0KGgoAAAANSUhEUgAAAZAAAAGQCAIAAAAP3aGbAAAVp0lEQVR4nO3dZ3hUdb7A8TMzmUmGFNIhBEyoCYFAkBJAEURQ1kJHbGu57nq53udx7+PyqGBjAVEEWa/9rrqLvaxSBAQBBaUtBIi0EEoIBAiEAGkkIW3mvjiTkyGkTGd+7vfz6qTM5JyB/3dOH13qU+sUAJBAf61nAAAcRbAAiEGwAIhBsACIQbAAiEGwAIhBsACIQbAAiEGwAIhBsACIQbAAiEGwAIhBsACIQbAAiEGwAIhBsACIQbAAiEGwAIhBsACIQbAAiEGwAIhBsACIQbAAiEGwAIhBsACIQbAAiEGwAIhBsACIQbAAiEGwAIhBsACIQbAAiEGwAIhBsACIQbAAiEGwAIhBsACIQbAAiEGwAIhBsACIQbAAiEGwAIhBsACIQbAAiEGwAIhBsACIQbAAiEGwAIhBsACIQbAAiEGwAIhBsACIQbAAiEGwAIhBsACIQbAAiEGwAIhBsACIQbAAiEGwAIhBsACIQbAAiEGwAIhBsACIQbAAiEGwAIhBsACIQbAAiEGwAIhBsACIQbAAiEGwAIhBsACIQbAAiEGwAIhBsACIQbAAiEGwAIhBsACIQbAAiEGwAIhBsACIQbAAiEGwAIhBsACIQbAAiEGwAIhBsACIQbAAiEGwAIhBsACIQbAAiEGwAIhBsACIQbAAiEGwAIhBsACIQbAAiEGwAIhBsACIQbAAiEGwAIhBsACIQbAAiEGwAIhBsACIQbAAiEGwAIhBsACIQbAAiEGwAIhBsACIQbAAiEGwAIhBsACIQbAAiEGwAIhBsACIQbAAiEGwAIhBsACIQbAAiEGwAIhBsACIQbAAiEGwAIhBsACIQbAAiEGwAIhBsACIQbAAiEGwAIhBsACIQbAAiEGwAIhBsACIQbAAiEGwAIhBsACIQbAAiEGwAIhBsACIQbAAiEGwAIhBsACIQbAAiEGwAIhBsACIQbAAiEGwAIhBsACIQbAAiEGwAIhBsACIQbAAiEGwAIhBsACIQbAAiEGwAIhBsACIQbAAiEGwAIhBsACIQbAAiEGwAIhBsACIQbAAiEGwAIhBsACIEdDcD/bOH+XL+QAAVZ+n1zf3I9awAIjR7BqWqoXUAYBntbphxxoWADEIFgAxCBYAMQgWADEIFgAxCBYAMQgWADEIFgAxCBYAMQgWADEIFgAxCBYAMQgWADEIFgAxCBYAMVq5H5Y3DOoa8cFj/bUv7387Y19eiTtP2CnKfEuv2LTE8G7tgyODTWaTobyq9uKlmqzTpRk5RWv2nC2vqmvh4aHmgC2zRqjTWw9fmPZhpjszY8+dJV311A2dosyt/lptnbWq1lJcXn266HLW6dKNWYW7c4ub/E3XFvPpsUn339BJ+/KzLSfnf3fIkQeqts+52WwyqNPTPszceviCI48KDNBnvDRSnV6SkT/rm6xGv7D0ySFd2wU7Phv28osuj3llszpt/5q4bFXm2Rlf7nf54e7/9/Pef2DF7cHlcdcgWOMGdLD/ckp6vMvB6t854o8jE4f2iGr0/TCzMcxsTIxpc3ta++l39vh0c977P+VW11pcnGNXeXBJmxNg0AUYDMGB5vhI86CuEQ/flJB5vHjmVwdOX6x085l1OmXmuOSpQzpq3/lkU96ClYddfsJZk3pO/Ou/Ll2udXPG4Bv+Obh8vUkYHGgYnRpr/50xfduFmp3uptlkmD0l5R/T+l/9gl79F//zls5fPZEeFx7k7F9xh6eW1Fn9EsM/fnxAh4jW185aoNMpL0zsaV+rxb+ccKdWiqK0Dw+afmcPd54BvuHPg8vXwbqtb/sgo0FRlAOnStWVySCj4a7r45x6ksgQ0z+m9R9/5fpLy7q2C/748YFuDmOneGRJXRMTGjhvai+XH67X6f4yOWXSoHjtOx9uPL5o1RH3Z2ziwA43JLUyBnBt+fng8vUmofZC7DxWVFBSNbJXjKIoU9I7fr7lpIPPEGjUv/VwWkp8mPadOot1w4HCHw+cyzpVVlhWVVldFxwYkBDTZnC3yEmD4jtE2Nrfrm3got+nPvjOTt+svrq/pKpLl2uHvrixuZ8aDfpQc0DnmOBhyVF3D+4YEmT7B72+c/iw5OhN2eednW29XjdnSop9WN//KffNH3KcfZ7m/GVSyvhF2zy1YVhZXZf+/AaXH15WWdvCpxbMvbvX2P6212Hcwm25heUu/yEp/H9w+XQNKyG6TVpCW3V6z4mSDVmF6nTXdsH9EsMdfJLpd/To3anhBd2RUzTutW1Pfrp3VebZ3MLyS5dr6yzW0sqafXkl7/+UO3bh1o835Wm/nBIf9tBNCZ5ZmBZ5ZEkdUVNnuXipeldu0eurj45fdMWgcmFtTq/XvTy1l/0D/+9HT9ZKUZTYtoFP38WGoZ/y/8Hl02CNH2hb6aits27PubjhQGFtnVX9zt2DOzb/uAYp8WFTBjdsqizbmf/YB7vzzlc09/vVtZaFKw9/uPG49p1HhieEmY0uzLxT3F9SF5wrqXru64YDas6W0aDXLbgv9Xdp7bXvvLPu2NtrPVMr+1WqcQM63JQc7ZGnhQeJGFy+C5Zerxtb/9a9I+diWWVtaWXN1iO249yjU2PD27S+qI/enKjX6dTpzOPFs745aLFYW33Um2tysvPL1OmQoIAxfdu5sgAO88iSumZfXklxRY06HRNmqn+pWhdg0C28P9X+KMGbP+S8t/6Yp2Ys41jRxvrVTEVRXpzU0wfHH+AUGYPLq89ub2j3yJiwQHX6x/3n1ImVu8+oE6YA/bjW9vNFhZhu6RWjTlutypyl2RZr6y+ooigWq1VbUzhfVq3Nhpe4v6Qu0+t0ZqPtvCfFoddGURTFaND/9fd9bundUKvXVx99/6dcz87b7CUHSxpiGvjM2CTPPj/cIWVw+e5dbsJA29pmeVXd97+eVac3HCgsLq8JDzYqijI5Pf6jX0608Aw3Jkfr9bZ3gJ25RUfPXnL8r2/KvvDkp3uzTpXmF112Ze6d4f6SumxESnSg0fYmdK60ypH/cqYA/esP9r3R7uDdolVHFnth9s6XVb/y3aGX7+mtfnnX9XHr9p2zX+3CNSRlcPloDattG+OIFNtui2U787WzY6tqLf/cfkqdTohuM6hrRAtPMqBzuDa99ZBD50xrLFbr+n3nfPCCemRJXdO9fchzE3pqX+5q5pR3e4FG/RsPXVGrBSsPe6NWqlWZZ3860FCoFyb2bOu1rWM4RcTgUnwWrDv6tTca9IqiWK3KF1uvOK7/5dZTNXW2Q6FTWtwh3bVdiDa97chFL8ymB3hkSR2k1+nMJkPHSPPwntGzp6R8+cSg6FCT9lOtj80JMhrefiTN/uTABSsPf2J33Mcb5iw5qO1liw41zRjHhqFfEDG4FJ9tEmonJW0+dL7RcYfCsqo1ewrUQ+m39IqNDDFdvFTd5JPERTScTZt3odmDF9eWR5bUXkhQwN75o5ydjTV7Cpq7qFDVxmR465G0AV2uWNGLDDE19/uecuFS9bxl2a/el6p+eXta+3X7zml7+pxlNhmcenGyTpfe88YO1/7Wb5uIwaX4Zg0rKS40uUOoOv1ZU6dNau/qAQbdhOZ3SIcE2vJaXWvxz0vSPLWkbtqRU3T1BcP22gQGvPtov0a1UhTlP4YnDuke6aW50qzZU7B+X0OhnpuQ7L3DpnCQ/w8ulS+CNX6A7Rj/8cKKbUea2DzOzi/blVukTk9Kj2/uYLzRYPtBhW8vEHecp5bUZZdr6t5df2zah7srqlt6idIS2tqfpXWkfg+rTqe8NLW3D9az5izNLiq3rV1GhZhmjk/29l9Ey/x/cKm8HqwAg+6OfrZh/PmWk80dt9JWPTpGmod0b/pys8oa2w4g7UCYX/HgkjqrsLRqY1bhnCUHR8/b/O66Y9pJqq2yWpW5S7MffCdDu7tDdKhp3tReHi9pI0Xl1S8ta7hNzZi+7UZdeaE4fMzPB5fG6/uwRvSMUY/lK4oyc3zSzPGt72Sdkh7f5I2TisurgwPNiqKYTYbgQIOPb8TTKg8uqb1G1xLqdbogo757XMiDwxK08zyzTpctXHnE2V0PFov1+X9mrdh9RlGUGV/uXzxtgHpge2iPqIduSlj8s7eOFarW7i1Ymxp7ax/beYbPT0jedaxYW+1ykJvXEkLj54NL4/WaunCS5IiUmCZPP8u70HCPp8QYF+/f5j0eXNIWWKzWiuq6PSdK/vzp3rn1Z/cN7xn99f+kD+/pxPUuNXWW6Z/tW1F/OuuvJ0re33Bc++kTt3Xr3TGs6Ud6ztxl2dphh4hg07MOJB5e4ueDS+PdYEWHmm50/nYiBr1u4sAmBv+h+isAFEVJc/4S4lGpsRMGdugcE+yN7R3PLqmDvv7Xqdfq7/rSxmR47YE+g7o6tMu8qsbyxEd71l95bO699cf2nyxVpwMMulfvT9Xu/eAlxeU1c5dma1/e2qfdbX28e2EHmuPPg8ued4N11/VxBr0rSzBxULz+qkXfkdNwesjo3k7v8vjv0V3/Mjll+fQhv7wwPDGmjQtz1QLPLqnjPtmUt3xnvjptCtC/8XDfzg68Pe7KLdpy1cmBdRbrM1/ur6zfW98x0vzCxJ5XPdTD1u8/t2ZPgfbls+OTfbDLH1fz58Flz7tvodpWUlF59ci5m+pau5byg8euV9cR4sKDhiVH/Xzwits5ZeQUXbpcq77t90sMT+4Qmm33ttCy/p0jtLuA19RZ8867ewfhRjy7pE6Zt/xQWmJ4QnQbxbaelXrvWzuqaly5LVHe+Yr5Kw7PmmTr1Ji+7bYdubA0I9/leXPEvGXZA7tGRIWYFEUJDzY+NyF5xheu3yIdrvHnwWXPi2tYfa5r2yXWthhr955rdQwrirJ85xltenJ643PBq2ot2ruxTqfMGJekd2ylxqDXPXl7N+3LH/YWOHhhp4M8vqROqayum/nVAe3C+m7tQ/58R3eXn23JjtP2V8/MGJfkyCqbO4oramZ/e1D7clTvWPtb3MA3/HZwNeLFYNnfZVW7Brhl6/ef004gGpYcdfWNoj/65YQ2Mvslhj8/IbnV7SmdTnl6bI/U62y306uts36yycPHv7yxpE7Zl1fy8eaGS2qmDu6k3T7QBbO+zSosq1Kng4yGBfenBgZ4d9fBhqzCVZkNr9tT3OHvWvDPwdWIt/4jBhr12p1xzhRf/vVEsSOPqqyuW7fXlnm9TjfR7rbiqhPnK77ZcVr7ctKg+Pce7dfCx2FFBJsW3Jd6z5CGD6r6Zscpz16l6aUlddbba3NO1h/o0emUWZNT1EsaXVBcXvP811na22SPuBAffHjEy8sPaZX09s5+NMkPB9fVvBWsUb1jtf92a/YUOL6S+N2uhm2liQM7XL0ne9GqK044Gtw9csX0oYse6PO7tPadosyBRr3RoI8ONd2QFDVzfNKqp4beanfg6XhhxaJVR11bouZ4b0mdUlVjmb2kYcOqS2zwH0YmuvxsWw9f+Nzuyu2pQzqOrL9ZkpeUVtbM/ja79d+DN/nb4Lqat97K7LeSVju2laTamVuUX1SpfgJHTFjgiJSYRlfGVlTXPf73XxdPG6DdmUCv141KjW31VOnCsqo/fbTnck1LZ8QN7RHl4MW0OQXlExZtU7y5pM7afvTi8p352u7/P9ycuHZvQU6Bix+d8Pr3RwZ3i9R2ps6ekpJ1evvZ4iveP+/sFzfvHtvH87j5eaKKovx8sHDFrjN39XfiVvTOXvys+vvG46+v9tjQeuDG67Rt2M82581f4fqHobnw38+zz+DVweURXlnD6hARpJ0QlFtY7vjhBkVRrFZlxe6GYT8lvYltpbzzFQ+9m+HU0+YUlD/y7i6Pf/CJt5fUWQtXHdFOxTQa9C9OSnH5lImqWsszX+zX7ocTZjbOv7e3gztiXfbKikOFpVVe/RNomf8MriZ5JVhj+3fQxsn3mU6sdKi+29VwHH1I96iOkU1sRZ+8UPnA2xmLvj+i3VypOWWVte+tP3b3/273xk0zfLCkTimpqLF/h09LaOvOZ14cOlP2xpqGD6Holxj+X6O6uDV/rSmrrJ1ld8QQ14SfDK4meX6TUKdTxtmt1a+2Oy3QQScvVGYeL1ZvJ6DTKZPT45tcga+utSz++cTnW04O7hZ5Q1JUUlxopyhzSFBAYIC+7HLtxfLq/SdLM3KKfthbUNnirQtc5rMldcrqX8/e2a/9sPqPpfnTmG4bswoLSlxcbfl404kbk6LSu9nWIv84MnHH0YsZx4rcnMkWbMo+v2xnvlMf5AmPu+aDqzm61KfWNfkDdUu4hY+ZBKB5fHSXaaO6/O3H3Lc89MFo/55azY5f30oCkCI6NFBRlAsO3EIW7iBYgAf0ua6toigHT5de6xn5jSNYgLt6dwrrERdy6mLlnrySaz0vv3EEC3BL13bBr96XWltnffarA968ig6KQrAAN4WZjSUVNY/+bVfm8eJrPS+/fVy0Bbgl83jxvW/y0WE+whoWADEIFgAxCBYAMQgWADEIFgAxWjlK6MLNhgDAS1jDAiBGs3drAAB/wxoWADEIFgAxCBYAMQgWADEIFgAxCBYAMQgWADEIFgAxCBYAMQgWADEIFgAxCBYAMQgWADEIFgAxCBYAMQgWADEIFgAxCBYAMQgWADEIFgAxCBYAMQgWADEIFgAxCBYAMQgWADEIFgAxCBYAMQgWADEIFgAxCBYAMQgWADEIFgAxCBYAMQgWADEIFgAxCBYAMQgWADEIFgAxCBYAMQgWADEIFgAxCBYAMQgWADEIFgAxCBYAMQgWADEIFgAxCBYAMQgWADEIFgAxCBYAMQgWADEIFgAxCBYAMQgWADEIFgAxCBYAMQgWADEIFgAxCBYAMQgWADEIFgAxCBYAMQgWADEIFgAxCBYAMQgWADEIFgAxCBYAMQgWADEIFgAxCBYAMQgWADEIFgAxCBYAMQgWADEIFgAxCBYAMQgWADEIFgAxCBYAMQgWADEIFgAxCBYAMQgWADEIFgAxCBYAMQgWADEIFgAxCBYAMQgWADEIFgAxCBYAMQgWADEIFgAxCBYAMQgWADEIFgAxCBYAMQgWADEIFgAxCBYAMQgWADEIFgAxCBYAMQgWADEIFgAxCBYAMQgWADEIFgAxCBYAMQgWADEIFgAxCBYAMQgWADEIFgAxCBYAMQgWADEIFgAxCBYAMQgWADEIFgAxCBYAMQgWADEIFgAxCBYAMQgWADEIFgAxCBYAMQgWADEIFgAxCBYAMQgWADEIFgAxCBYAMQgWADEIFgAxCBYAMQgWADEIFgAxCBYAMQgWADEIFgAxCBYAMQgWADEIFgAxCBYAMQgWADEIFgAxCBYAMQgWADEIFgAxCBYAMQgWADEIFgAxCBYAMQgWADEIFgAxCBYAMQgWADEIFgAxCBYAMQgWADEIFgAxCBYAMQgWADEIFgAxCBYAMf4fuMa0lu/oFl4AAAAASUVORK5CYII="


def generate_token(email):
    token = hashlib.sha256(email.encode()).hexdigest()
    return token


def verify_token(email, token):
    generated_token = generate_token(email)
    return token == generated_token


class TestModelBaseView(UserPassesTestMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["modelformtest_nav"] = True
        return context

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        raise PermissionDenied


class TestModelDeleteView(TestModelBaseView, DeleteView):
    model = TestModel
    success_url = reverse_lazy("test_model_list")
    template_name = "test_model_confirm_delete.html"


class TestModelListView(TestModelBaseView, ListView):
    model = TestModel
    template_name = "test_model_list.html"
    context_object_name = "test_models"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["marketing_email_messages"] = MarketingEmailMessage.objects.all()
        return context
        for test_model in context["test_models"]:
            test_model.unsubscribe_token = test_model.unsubscribe_token


class TestModelCreateView(TestModelBaseView, CreateView):
    model = TestModel
    form_class = TestModelForm
    template_name = "test_model_form.html"

    def get_initial(self):
        fake = Faker()
        return {
            "name": fake.name(),
            "email": fake.email(),
            "age": fake.random_int(min=18, max=100),
        }

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class TestModelUpdateView(TestModelBaseView, UpdateView):
    model = TestModel
    form_class = TestModelForm
    template_name = "test_model_form.html"


class TestModelDetailView(TestModelBaseView, DetailView):
    model = TestModel
    template_name = "test_model_detail.html"
    context_object_name = "test_model"


class TestModelSendMarketingEmailView(TestModelBaseView, View):
    def get(self, request, *args, **kwargs):
        test_models = TestModel.objects.all()
        recipients = []
        marketing_email_message = MarketingEmailMessage.objects.first()
        if not marketing_email_message:
            messages.info(request, "No marketing email message found!")
            return HttpResponseRedirect(reverse("test_model_list"))

        for test_model in test_models:
            subject = marketing_email_message.subject
            sender = settings.DEFAULT_FROM_EMAIL
            email_address = test_model.email
            recipients.append(email_address)
            html_message = render_to_string(
                "marketing_email.html",
                {
                    "test_model": test_model,
                    "message": marketing_email_message.message,
                    "logo": logo,
                },
            )

            text_message = strip_tags(html_message)
            email = EmailMultiAlternatives(
                marketing_email_message.subject, text_message, sender, [email_address]
            )
            email.attach_alternative(html_message, "text/html")
            email.send()

        messages.success(
            request, f"Marketing emails sent! {', '.join([i for i in recipients])}"
        )

        return HttpResponseRedirect(reverse("test_model_list"))


class TestModelCreateMarketingEmailView(TestModelBaseView, CreateView):
    model = MarketingEmailMessage
    form_class = MarketingEmailMessageForm
    template_name = "create_marketing_email_message.html"
    success_url = reverse_lazy("test_model_list")


class TestModelUpdateMarketingEmailView(TestModelBaseView, UpdateView):
    model = MarketingEmailMessage
    form_class = MarketingEmailMessageForm
    template_name = "update_marketing_email_message.html"
    success_url = reverse_lazy("test_model_list")


class TestModelDeleteMarketingEmailView(TestModelBaseView, DeleteView):
    model = MarketingEmailMessage
    success_url = reverse_lazy("test_model_list")
    template_name = "delete_marketing_email_message.html"


# class TestModelUnsubscribeView(UpdateView):
#     model = TestModel
#     template_name = "unsubscribe.html"
#     success_url = reverse_lazy("unsubscribe_success")
#
#     def get_object(self, queryset=None):
#         token = self.kwargs.get("token", None)
#         email = self.kwargs.get("email", None)
#         if not verify_token(email, token):
#             return None
#         queryset = TestModel.objects.filter(email=email)
#         return queryset.first()
#
#     def get_form(self, form_class=None):
#         # Override get_form to include only the is_subscribed field
#         form = super().get_form(form_class)
#         form.fields = ["is_subscribed"]
#         return form
#
#     def form_valid(self, form):
#         form.instance.is_subscribed = False
#         return super().form_valid(form)
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context["unsubscribe_email"] = self.kwargs.get("email")
#         return context


def unsubscribe_view(request, email, token):
    test_model = get_object_or_404(TestModel, email=email, unsubscribe_token=token)
    test_model.is_subscribed = False
    test_model.save()
    return HttpResponse(
        "You have been successfully unsubscribed from our mailing list."
    )


def unsubscribe_success(request):
    return render(request, "unsubscribe_success.html")
