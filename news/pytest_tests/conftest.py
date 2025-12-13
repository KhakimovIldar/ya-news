import pytest
from datetime import datetime, timedelta

from django.conf import settings
from django.test.client import Client

from news.forms import BAD_WORDS
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
    news = News.objects.create(
        id=1,
        title='Заголовок новости',
        text='Tекст новости',
    )
    return news


@pytest.fixture
def news_list():
    today = datetime.today()
    news_list = []
    for i in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1):
        news = News(
            title=f'Заголовок новости {i}',
            text=f'Tекст новости {i}',
            date=today - timedelta(days=i)
        )
        news_list.append(news)
    News.objects.bulk_create(news_list)
    return news_list


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Tекст комментария'
    )
    return comment


@pytest.fixture
def comments_list(author, news):
    today = datetime.today()
    comments_list = []
    for i in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1):
        comment = Comment(
            news=news,
            text=f'Tекст комментария {i}',
            created=today - timedelta(days=i),
            author=author,
        )
        comments_list.append(comment)
    Comment.objects.bulk_create(comments_list)
    return comments_list


@pytest.fixture
def form_data(not_author):
    return {
        'auhtor': f'{not_author}',
        'text': 'text',
    }


@pytest.fixture
def form_bad_data(not_author):
    return {
        'author': f'{not_author}',
        'text': f'text {BAD_WORDS[0]} text',
    }
