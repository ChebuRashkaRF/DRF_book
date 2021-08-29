from django.test import TestCase
from django.contrib.auth.models import User
from django.db.models import Count, Case, When, F
from unittest import mock

from store.models import Book, UserBookRelation
from store.serializers import BooksSerializer


class BooksSerializerTestCase(TestCase):
    def test_ok(self):
        user1 = User.objects.create(username='test_username1',
                                    first_name='Ivan', last_name='Petrov')
        user2 = User.objects.create(username='test_username2',
                                    first_name='Petr', last_name='Ivanov')
        user3 = User.objects.create(username='test_username3',
                                    first_name='Sergey', last_name='Lubinec')
        book_1 = Book.objects.create(name='Test book 1', price=25, author_name='Auther 1', owner=user1)
        book_2 = Book.objects.create(name='Test book 2', price=55, author_name='Auther 2')

        UserBookRelation.objects.create(user=user1, book=book_1, like=True, rate=5)
        UserBookRelation.objects.create(user=user2, book=book_1, like=True, rate=5)
        user_book_3 = UserBookRelation.objects.create(user=user3, book=book_1, like=True)
        user_book_3.rate = 4
        user_book_3.save()


        UserBookRelation.objects.create(user=user1, book=book_2, like=True, rate=3)
        UserBookRelation.objects.create(user=user2, book=book_2, like=True, rate=4)
        UserBookRelation.objects.create(user=user3, book=book_2, like=False)

        books = Book.objects.all().annotate(
            annotated_likes=Count(Case(When(userbookrelation__like=True, then=1))),
            owner_name=F('owner__username')
        ).order_by('id')
        data = BooksSerializer(books, many=True).data
        expected_data = [
            {
                'id': book_1.id,
                'name': 'Test book 1',
                'price': '25.00',
                'author_name': 'Auther 1',
                'annotated_likes': 3,
                'rating': '4.67',
                'owner_name': 'test_username1',
                'readers': [
                    {
                        'first_name': 'Ivan',
                        'last_name': 'Petrov'
                    },
                    {
                        'first_name': 'Petr',
                        'last_name': 'Ivanov'
                    },
                    {
                        'first_name': 'Sergey',
                        'last_name': 'Lubinec'
                    }
                ]
            },
            {
                'id': book_2.id,
                'name': 'Test book 2',
                'price': '55.00',
                'author_name': 'Auther 2',
                'annotated_likes': 2,
                'rating': '3.50',
                'owner_name': None,
                'readers': [
                    {
                        'first_name': 'Ivan',
                        'last_name': 'Petrov'
                    },
                    {
                        'first_name': 'Petr',
                        'last_name': 'Ivanov'
                    },
                    {
                        'first_name': 'Sergey',
                        'last_name': 'Lubinec'
                    }
                ]
            },
        ]
        self.assertEqual(expected_data, data)

        with mock.patch('store.service.set_rating') as mock_foo:
            user_book_3.like = False
            user_book_3.save()
            self.assertEqual(False, mock_foo.called)
