from http import HTTPStatus


def test_read_root(client):
    response = client.get('/')  # Act
    assert response.status_code == HTTPStatus.OK  # Assert
    assert response.json() == {'message': 'Server Ok'}  # Assert
