import pytest

from django.conf import settings
from django.urls import reverse
from pytest_lazy_fixtures import lf

from news.forms import CommentForm

HOME_URL = reverse('news:home')


@pytest.mark.django_db
def test_news_count(client, news_list):
    """Количество новостей на главной странице — не более 10."""
    news_list = news_list
    response = client.get(HOME_URL)
    object_list = response.context['object_list']
    assert object_list.count() == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_sorted(client, news_list):
    """
    Новости отсортированы от самой свежей к самой старой.
    Свежие новости в начале списка.
    """
    news_list = news_list
    response = client.get(HOME_URL)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_sorted(client, news, comments_list):
    """
    Новости отсортированы от самой свежей к самой старой.
    Свежие новости в начале списка.
    """
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    comments_list = comments_list
    news = response.context['news']
    all_comments = news.comment_set.all()
    comment_count = all_comments.count()
    assert comment_count == 11

    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


@pytest.mark.django_db
@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    [
        (lf('client'), False),
        (lf('author_client'), True)
    ],
)
def test_form_availability(news, parametrized_client,
                           expected_status):
    """
    Анонимному пользователю недоступна форма для отправки комментария на.
    Cтранице отдельной новости, а авторизованному доступна.
    """
    url = reverse('news:detail', args=(news.id,))
    response = parametrized_client.get(url)
    flag = 'form' in response.context
    assert flag == expected_status
    if flag:
        assert isinstance(response.context['form'], CommentForm)
