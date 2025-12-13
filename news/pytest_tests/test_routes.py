from http import HTTPStatus
import pytest

from django.urls import reverse
from pytest_django.asserts import assertRedirects
from pytest_lazy_fixtures import lf


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, expected_status',
    (
        ('news:home', HTTPStatus.OK, ),
        ('users:login', HTTPStatus.OK),
        ('users:signup', HTTPStatus.OK),
        ('users:logout', HTTPStatus.METHOD_NOT_ALLOWED),
    )
)
def test_pages_availability_for_anonymous_user(
        client, name, expected_status, ):
    """
    П.1 Главная страница доступна анонимному пользователю.
    П.5 Регистрация, вход и выход доступны анонимным пользователям.
    """
    url = reverse(name)
    response = client.get(url)
    assert response.status_code == expected_status


@pytest.mark.django_db
def test_news_detail_for_anonymous_user(client, news):
    """П.2 Страница отдельной новости доступна анонимному пользователю."""
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (lf('not_author_client'), HTTPStatus.NOT_FOUND),
        (lf('author_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete',),
)
def test_pages_availability(parametrized_client, name, comment,
                            expected_status):
    """
    П.3 Страницы удаления и редактирования комментария доступны автору.
    П.5 Авторизованный пользователь не может зайти на страницы редактирования.
    Или удаления чужих комментариев.
    """
    url = reverse(name, args=(comment.id,))
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete',),
)
def test_redirects(client, name, comment):
    """
    При попытке перейти на страницу редактирования или удаления комментария.
    Анонимный пользователь перенаправляется на страницу авторизации.
    """
    url = reverse(name, args=(comment.id,))
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
