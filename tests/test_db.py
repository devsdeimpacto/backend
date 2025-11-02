from sqlalchemy import select

from app.models import User


def test_create_user(session):
    user = User(username='test', email='test@test.com', password='test')

    session.add(user)
    session.commit()

    result = session.scalar(select(User).where(User.email == 'test@test.com'))

    assert result.username == 'test'
