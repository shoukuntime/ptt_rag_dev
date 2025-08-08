from django.db import models

class Article(models.Model):
    board = models.CharField(max_length=100)
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=100)
    content = models.TextField()
    post_time = models.DateTimeField()
    url = models.URLField(max_length=255)

    def __str__(self):
        return f"[{self.board}] {self.title}"