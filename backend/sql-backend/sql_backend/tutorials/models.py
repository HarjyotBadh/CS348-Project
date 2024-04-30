from django.db import models


class Tutorial(models.Model):
    title = models.CharField(max_length=70, blank=False, default='')
    description = models.CharField(max_length=200,blank=False, default='')
    published = models.BooleanField(default=False)
    users = models.ManyToManyField('auth.User', related_name='tutorials')

    class Meta:
        indexes = [
            models.Index(fields=['title'], name='title_idx'),
            models.Index(fields=['published'], name='published_idx'),
        ]