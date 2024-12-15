import unittest
from app import app, db, User


class AppTestCase(unittest.TestCase):
    def setUp(self):
        # Настроим приложение для тестирования
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Используем in-memory базу данных
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        self.client = app.test_client()

        # Инициализируем базу данных внутри контекста приложения
        with app.app_context():
            db.create_all()
            self.create_test_user()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    # Создание тестового пользователя
    def create_test_user(self):
        user = User(username='testuser', password='password', role='user')
        db.session.add(user)
        db.session.commit()

    # Тестируем функциональность входа
    def test_login_functionality(self):
        # Выполняем POST-запрос с данными для входа
        response = self.client.post('/login', data=dict(
            username='testuser',
            password='password'
        ), follow_redirects=True)

        # Проверка, что статус код ответа 200
        self.assertEqual(response.status_code, 200)

        # Проверка, что в ответе содержится строка приветствия с именем пользователя
        self.assertIn('Привет, testuser!', response.data.decode('utf-8'))

        # Также можно проверить, что страница действительно является главной
        self.assertIn('Большая Тропа Севастополя',
                      response.data.decode('utf-8'))



# Тестируем доступность главной страницы
    def test_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Большая Тропа Севастополя', response.data.decode('utf-8'))

    # Тестируем доступность страницы регистрации
    def test_register_page(self):
        response = self.client.get('/register')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Регистрация',
                      response.data.decode('utf-8'))  # Проверяем, что слово "Регистрация" есть на странице

    # Тестируем доступность несуществующей страницы (404)
    def test_404_page(self):
        response = self.client.get('/nonexistent_page')
        self.assertEqual(response.status_code, 404)

    # Тестируем функциональность входа с неправильными данными (неверный логин или пароль)
    def test_login_failure(self):
        # Выполняем POST-запрос с неверными данными для входа
        response = self.client.post('/login', data=dict(
            username='wronguser',
            password='wrongpassword'
        ), follow_redirects=True)

        # Проверка, что страница все еще загружается с ошибкой
        self.assertEqual(response.status_code, 200)

        # Проверка, что сообщение об ошибке присутствует
        self.assertIn('Неверное имя пользователя или пароль', response.data.decode('utf-8'))

    # Тестируем функциональность выхода
    def test_logout_functionality(self):
        # Входим в систему перед тестом
        self.client.post('/login', data=dict(
            username='testuser',
            password='password'
        ), follow_redirects=True)

        # Выполняем запрос на выход
        response = self.client.get('/logout', follow_redirects=True)

        # Проверка, что статус код ответа 200 (страница загрузилась)
        self.assertEqual(response.status_code, 200)

        # Проверка, что в ответе не содержится имя пользователя, т.е. пользователь вышел
        self.assertNotIn('Привет, testuser!', response.data.decode('utf-8'))

        # Проверка, что на странице отображается кнопка для входа
        self.assertIn('Войти', response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
