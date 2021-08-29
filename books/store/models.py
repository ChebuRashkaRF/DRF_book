from django.db import models
from django.contrib.auth.models import User


class Book(models.Model):
    """Книги"""

    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    author_name = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='my_books')
    readers = models.ManyToManyField(User, through='UserBookRelation', related_name='books')
    rating = models.DecimalField(max_digits=3, decimal_places=2, blank=True, default=None, null=True)

    def __str__(self):
        return f'Id {self.id}: {self.name}'


class UserBookRelation(models.Model):
    """Отношение книги и пользователя"""

    RATE_CHOICES = (
        (1, '1.0'),
        (2, '2.0'),
        (3, '3.0'),
        (4, '4.0'),
        (5, '5.0')
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    like = models.BooleanField(default=False)
    in_bookmarks = models.BooleanField(default=False)
    rate = models.PositiveSmallIntegerField(choices=RATE_CHOICES, null=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.old_rate = self.rate

    def __str__(self):
        return f'{self.user.username}: {self.book.name}, RATE {self.rate}'

    def save(self, *args, **kwargs):

        creating = not self.pk

        super().save(*args, **kwargs)

        if self.old_rate != self.rate or creating:
            from store.service import set_rating
            set_rating(self.book)
            self.old_rate = self.rate
