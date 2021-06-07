from django.test import TestCase
from django.urls import reverse
from .models import Book, Review
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission


class BookTests(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='reviewuser',
            email='review@gmail.com',
            password='testpass123'
        )

        self.special_permission = Permission.objects.get(codename='special_status')
        self.book = Book.objects.create(
            title='harry potter',
            author='jk rowlings',
            price='45.02'
        )

        self.review = Review.objects.create(
            book=self.book,
            author=self.user,
            review='An excellent review',
        )

    def test_book_listing(self):
        self.assertEqual(f'{self.book.title}', 'harry potter')
        self.assertEqual(f'{self.book.author}', 'jk rowlings')
        self.assertEqual(f'{self.book.price}', '45.02')

    # def test_book_list_view(self):
    #     response = self.client.get(reverse('book_list'))
    #     self.assertEqual(response.status_code, 200)
    #     self.assertContains(response, 'harry potter')
    #     self.assertTemplateUsed(response, 'book/book_list.html')

    # def test_book_detail_view(self):
    #     response = self.client.get(self.book.get_absolute_url())
    #     no_response = self.client.get('/books/12345')
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(no_response.status_code, 404)
    #     self.assertContains(response, 'harry potter')
    #     self.assertContains(response, 'An excellent review')
    #     self.assertTemplateUsed(response, 'book/book_detail.html')

    def test_book_list_for_logged_in_user(self):
        self.client.login(email='review@gmail.com', password='testpass123')

        response = self.client.get(reverse('book_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'harry potter')
        self.assertTemplateUsed(response, 'book/book_list.html')

    def test_book_list_view_for_logged_out_user(self):
        self.client.logout()
        response = self.client.get(reverse('book_list'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '%s?next=/books/' % (reverse('account_login')))
        response = self.client.get('%s?next=/books/' % (reverse('account_login')))
        self.assertContains(response, 'Log In')

    def test_book_detail_view_with_permissions(self):
        self.client.login(email='review@gmail.com', password='testpass123')
        self.user.user_permissions.add(self.special_permission)
        response = self.client.get(self.book.get_absolute_url())
        no_response = self.client.get('/book/12345/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(no_response.status_code, 404)
        self.assertContains(response, 'harry potter')
        self.assertContains(response, 'An excellent review')
        self.assertTemplateUsed(response, 'book/book_detail.html')
