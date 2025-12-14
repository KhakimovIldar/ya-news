from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects
from pytest_lazy_fixtures import lf

pytestmark = pytest.mark.django_db

HOME_URL = lf('home_url')
LOGIN_URL = lf('login_url')
SIGNUP_URL = lf('signup_url')
LOGOUT_URL = lf('logout_url')
NEWS_DETAIL_URL = lf('news_detail_url')
NEWS_DELETE_URL = lf('news_delete_url')
NEWS_EDIT_URL = lf('news_edit_url')


@pytest.mark.parametrize(
    'name, client_for_test, expected_status',
    (
        (HOME_URL, lf('client'), HTTPStatus.OK),
        (LOGIN_URL, lf('client'), HTTPStatus.OK),
        (SIGNUP_URL, lf('client'), HTTPStatus.OK),
        (LOGOUT_URL, lf('client'), HTTPStatus.METHOD_NOT_ALLOWED),
        (NEWS_DETAIL_URL, lf('client'), HTTPStatus.OK),
        (NEWS_DELETE_URL, lf('author_client'), HTTPStatus.OK),
        (NEWS_DELETE_URL, lf('not_author_client'), HTTPStatus.NOT_FOUND),
        (NEWS_EDIT_URL, lf('author_client'), HTTPStatus.OK),
        (NEWS_EDIT_URL, lf('not_author_client'), HTTPStatus.NOT_FOUND),
    )
)
def test_pages_availability_for_anonymous_user(
        client_for_test, name, expected_status):
    """
    П.1 Главная страница доступна анонимному пользователю.
    П.2 Страница отдельной новости доступна анонимному пользователю.
    П.3 Страницы удаления и редактирования комментария доступны автору.
    П.5 Авторизованный пользователь не может зайти на страницы редактирования.
    Или удаления чужих комментариев.
    П.6 Регистрация, вход и выход доступны анонимным пользователям.
    """
    response = client_for_test.get(name)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name, expected_url',
    (
        (lf('news_edit_url'), lf('expected_url_after_anonymous_edit_comment')),
        (lf('news_delete_url'), lf(
            'expected_url_after_anonymous_delete_comment')),
    ),
)
def test_redirects(client, name, expected_url, comment):
    """
    П4. При попытке перейти на страницу редактирования или удаления коментария.
    Анонимный пользователь перенаправляется на страницу авторизации.
    """
    response = client.get(name)
    assertRedirects(response, expected_url)
