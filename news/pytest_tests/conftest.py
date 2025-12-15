from datetime import datetime, timedelta

import pytest
from django.conf import settings
from django.test.client import Client
from django.urls import reverse

from news.models import Comment, News


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    return News.objects.create(
        title='Заголовок новости',
        text='Tекст новости',
    )


@pytest.fixture
def news_list():
    today = datetime.today()
    News.objects.bulk_create(
        [News(title=f'Заголовок новости {i}',
              text=f'Tекст новости {i}',
              date=today - timedelta(days=i))
         for i in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
         ]
    )


@pytest.fixture
def comment(author, news):
    return Comment.objects.create(
        news=news,
        author=author,
        text='Tекст комментария'
    )


@pytest.fixture
def comments_list(author, news):
    now = datetime.now()
    for i in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1):
        comment = Comment.objects.create(
            news=news,
            text=f'Tекст комментария {i}',
            author=author,
        )
        comment.created = now + timedelta(days=i)
        comment.save()


@pytest.fixture
def expected_url_after_add_comment(news_detail_url):
    return f'{news_detail_url}#comments'


@pytest.fixture
def expected_url_after_anonymous_add_comment(login_url, news_detail_url):
    return f'{login_url}?next={news_detail_url}'


@pytest.fixture
def expected_url_after_anonymous_edit_comment(login_url, news_edit_url):
    return f'{login_url}?next={news_edit_url}'


@pytest.fixture
def expected_url_after_anonymous_delete_comment(login_url, news_delete_url):
    return f'{login_url}?next={news_delete_url}'


@pytest.fixture
def home_url():
    return reverse('news:home')


@pytest.fixture
def login_url():
    return reverse('users:login')


@pytest.fixture
def logout_url():
    return reverse('users:logout')


@pytest.fixture
def news_delete_url(comment):
    return reverse('news:delete', args=(comment.id,))


@pytest.fixture
def news_detail_url(news):
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def news_edit_url(comment):
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
def signup_url(comment):
    return reverse('users:signup')
