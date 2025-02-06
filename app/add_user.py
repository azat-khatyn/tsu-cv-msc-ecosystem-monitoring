from app.repository_models import User, SessionLocal  # Импортируем модель и сессию из предыдущего шага

# Создаем сессию
db = SessionLocal()

# Добавляем пользователя
new_user = User(user_id=379017783, username="daniilShd")
db.add(new_user)
db.commit()
db.close()