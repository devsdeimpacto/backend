from http import HTTPStatus

from jwt import decode

from app.security import create_access_token
from app.settings import Settings


def test_jwt():
    data = {'sub': 'test@test.com'}
    token = create_access_token(data)

    decoded = decode(
        token, Settings().JWT_SECRET, algorithms=Settings().JWT_ALGORITHM
    )

    assert decoded['sub'] == data['sub']
    assert decoded['exp']


def test_jwt_invalid_token(client):
    response = client.delete(
        '/users/1',
        headers={'Authorization': 'Bearer tokeninvalido'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}
