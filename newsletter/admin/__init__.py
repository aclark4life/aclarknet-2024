from django.contrib import admin

from .newsletter import NewsletterAdmin
from .submission import SubmissionAdmin
from .message import MessageAdmin
from .subscription import SubscriptionAdmin

from ..models.newsletter import Newsletter
from ..models.submission import Submission
from ..models.message import Message
from ..models.subscription import Subscription

admin.site.register(Newsletter, NewsletterAdmin)
admin.site.register(Submission, SubmissionAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
