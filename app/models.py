from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

class ChatMessage(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_messages", null=True, blank=True)  # ✅ Make nullable
    message = models.TextField()
    sendtime = models.DateTimeField(default=now)

    def __str__(self):
        return f"{self.sender.username} to {self.receiver.username if self.receiver else 'N/A'}: {self.message[:30]}"
