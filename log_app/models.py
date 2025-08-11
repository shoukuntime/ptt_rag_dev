from django.db import models

class Log(models.Model):
    level = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    message = models.TextField()
    traceback = models.TextField(null=True, blank=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.level} - {self.created_at}'