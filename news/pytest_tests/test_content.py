from django.conf import settings
import pytest
from pytest_lazy_fixtures import lf

from news.forms import CommentForm

pytestmark = pytest.mark.django_db


def test_news_count(client, home_url, news_list):
    """Количество новостей на главной странице — не более 10."""
    response = client.get(home_url)
    news = response.context['object_list']
    assert news.count() == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_sorted(client, home_url, news_list):
    """
    Новости отсортированы от самой свежей к самой старой.
    Свежие новости в начале списка.
    """
    response = client.get(home_url)
    news = response.context['object_list']
    all_dates = [news.date for news in news]
    assert all_dates == sorted(all_dates, reverse=True)


def test_comments_sorted(client, news, news_detail_url, comments_list):
    """
    Новости отсортированы от самой свежей к самой старой.
    Свежие новости в начале списка.
    """
    response = client.get(news_detail_url)
    news = response.context['news']
    all_comments = news.comment_set.all()
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    assert all_timestamps == sorted(all_timestamps)


def test_author_client_form_availability(author_client, news, news_detail_url):
    """Авторизованному пользователю доступна форма для комментариев."""
    response = author_client.get(news_detail_url)
    assert isinstance(response.context.get('form'), CommentForm)


def test_anonymous_client_have_no_form_availability(client, news,
                                                    news_detail_url):
    """Анонимномк пользователю не доступна форма для комментариев."""
    response = client.get(news_detail_url)
    assert response.context.get('form') is None
