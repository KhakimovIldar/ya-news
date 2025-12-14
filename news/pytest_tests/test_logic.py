from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

COMMENT_FORM_DATA = {'text': 'text'}
pytestmark = pytest.mark.django_db


def test_anonymous_user_cant_create_comment(
    client, news, news_detail_url, login_url,
    expected_url_after_anonymous_add_comment
):
    """Анонимный пользователь не может отправить комментарий."""
    response = client.post(news_detail_url, COMMENT_FORM_DATA)
    assertRedirects(response, expected_url_after_anonymous_add_comment)
    assert Comment.objects.count() == 0


def test_user_can_create_comment(author_client, author, news, news_detail_url):
    """Авторизованный пользователь может отправить комментарий."""
    author_client.post(news_detail_url, COMMENT_FORM_DATA)
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.text == COMMENT_FORM_DATA['text']
    assert new_comment.author == author
    assert new_comment.news == news


def test_author_can_comment(
    author, author_client, comment, expected_url_after_add_comment, news,
    news_edit_url
):
    """Авторизованный пользователь может редактировать комментарии."""
    response = author_client.post(news_edit_url, COMMENT_FORM_DATA)
    assertRedirects(response, expected_url_after_add_comment)
    edit_comment = Comment.objects.get()
    assert edit_comment.text == COMMENT_FORM_DATA['text']
    assert edit_comment.author == author
    assert edit_comment.news == news


def test_author_can_delete_note(author_client, news_delete_url,
                                expected_url_after_add_comment):
    """Авторизованный пользователь может удалять комментарии."""
    response = author_client.post(news_delete_url)
    assertRedirects(response, expected_url_after_add_comment)
    assert Comment.objects.count() == 0


def test_other_user_cant_edit_comment(not_author_client, comment,
                                      news_edit_url):
    """Авторизованный пользователь не может редактировать чужие комментарии."""
    response = not_author_client.post(news_edit_url, COMMENT_FORM_DATA)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.news == comment_from_db.news
    assert comment.text == comment_from_db.text
    assert comment.author == comment_from_db.author


def test_other_user_cant_delete_comment(not_author_client, comment,
                                        news_delete_url):
    """Авторизованный пользователь не может удалить чужие комментарии."""
    response = not_author_client.post(news_delete_url)
    comment_from_db = Comment.objects.get(id=comment.id)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
    assert comment.news == comment_from_db.news
    assert comment.text == comment_from_db.text
    assert comment.author == comment_from_db.author


def test_user_cant_use_bad_words(not_author_client, news, news_detail_url):
    """
    Если комментарий содержит запрещённые слова, он не будет опубликован.
    А форма вернёт ошибку.
    """
    response = not_author_client.post(news_detail_url, {'text': BAD_WORDS[0]})
    assert response.status_code == HTTPStatus.OK
    form = response.context['form']
    assert not form.is_valid()
    assert 'text' in form.errors
    assert WARNING in form.errors['text']
    assert news.comment_set.count() == 0
