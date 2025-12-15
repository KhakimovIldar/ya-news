from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects
from pytest_lazy_fixtures import lf

pytestmark = pytest.mark.django_db


# Константы редиректорв
HOME_URL = lf('home_url')
LOGIN_URL = lf('login_url')
SIGNUP_URL = lf('signup_url')
LOGOUT_URL = lf('logout_url')
NEWS_DETAIL_URL = lf('news_detail_url')
NEWS_DELETE_URL = lf('news_delete_url')
NEWS_EDIT_URL = lf('news_edit_url')
EXPECTED_URL_AFTER_ANONYMOUS_EDIT_COMMENT = (
    lf('expected_url_after_anonymous_edit_comment')
)
EXPECTED_URL_AFTER_ANONYMOUS_DELETE_COMMENT = (
    lf('expected_url_after_anonymous_delete_comment')
)
# Константы клиентов
CLIENT = lf('client')
AUTHOR_CLIENT = lf('author_client')
NOT_AUTHOR_CLIENT = lf('not_author_client')


@pytest.mark.parametrize(
    'name, client_for_test, expected_status',
    (
        (HOME_URL, CLIENT, HTTPStatus.OK),
        (LOGIN_URL, CLIENT, HTTPStatus.OK),
        (SIGNUP_URL, CLIENT, HTTPStatus.OK),
        (LOGOUT_URL, CLIENT, HTTPStatus.METHOD_NOT_ALLOWED),
        (NEWS_DETAIL_URL, CLIENT, HTTPStatus.OK),
        (NEWS_DELETE_URL, AUTHOR_CLIENT, HTTPStatus.OK),
        (NEWS_DELETE_URL, NOT_AUTHOR_CLIENT, HTTPStatus.NOT_FOUND),
        (NEWS_EDIT_URL, AUTHOR_CLIENT, HTTPStatus.OK),
        (NEWS_EDIT_URL, NOT_AUTHOR_CLIENT, HTTPStatus.NOT_FOUND),
        (NEWS_EDIT_URL, CLIENT, HTTPStatus.FOUND),
        (NEWS_DELETE_URL, CLIENT, HTTPStatus.FOUND)

    )
)
def test_pages_availability_for_anonymous_user(
        client_for_test, name, expected_status):
    assert client_for_test.get(name).status_code == expected_status


@pytest.mark.parametrize(
    'name, expected_url',
    (
        (NEWS_EDIT_URL, EXPECTED_URL_AFTER_ANONYMOUS_EDIT_COMMENT),
        (NEWS_DELETE_URL, EXPECTED_URL_AFTER_ANONYMOUS_DELETE_COMMENT),
    ),
)
def test_redirects(client, name, expected_url, comment):
    """
    П4. При попытке перейти на страницу редактирования или удаления коментария.
    Анонимный пользователь перенаправляется на страницу авторизации.
    """
    assertRedirects(client.get(name), expected_url)
