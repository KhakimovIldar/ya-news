import pytest
from http import HTTPStatus

from django.urls import reverse
from pytest_django.asserts import assertRedirects

from news.forms import WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, news, form_data):
    """Анонимный пользователь не может отправить комментарий."""
    url = reverse('news:detail', args=(news.id,))
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_user_can_create_comment(author_client, author, news, form_data):
    """Авторизованный пользователь может отправить комментарий."""
    assert Comment.objects.count() == 0
    url = reverse('news:detail', args=(news.id,))
    author_client.post(url, data=form_data)
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.text == form_data['text']
    assert new_comment.author == author


def test_author_can_comment(author_client, form_data, comment, news):
    """Авторизованный пользователь может редактировать комментарии."""
    url = reverse('news:edit', args=(comment.id,))
    response = author_client.post(url, form_data)
    expected_url = reverse('news:detail', args=(news.id,)) + '#comments'
    assertRedirects(response, expected_url)
    comment.refresh_from_db()
    assert comment.text == form_data['text']


def test_author_can_delete_note(author_client, comment, news):
    """Авторизованный пользователь может удалять комментарии."""
    url = reverse('news:delete', args=(comment.id,))
    response = author_client.post(url)
    expected_url = reverse('news:detail', args=(news.id,)) + '#comments'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


def test_other_user_cant_edit_comment(
        not_author_client, form_data, comment, news):
    """Авторизованный пользователь не может редактировать чужие комментарии."""
    url = reverse('news:edit', args=(news.id,))
    response = not_author_client.post(url, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = comment.__class__.objects.get(id=comment.id)
    assert comment.text == comment_from_db.text


def test_other_user_cant_delete_comment(not_author_client, comment):
    """Авторизованный пользователь не может удалить чужие комментарии."""
    url = reverse('news:delete', args=(comment.id,))
    response = not_author_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


def test_user_cant_use_bad_words(not_author_client, form_bad_data, news):
    """
    Если комментарий содержит запрещённые слова, он не будет опубликован.
    А форма вернёт ошибку.
    """
    url = reverse('news:detail', args=(news.id,))
    response = not_author_client.post(url, data=form_bad_data)
    assert response.status_code == HTTPStatus.OK
    form = response.context['form']
    assert not form.is_valid()
    assert 'text' in form.errors
    assert WARNING in form.errors['text']
    assert news.comment_set.count() == 0
