from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import requests
from flask_migrate import Migrate
from datetime import datetime
app = Flask(__name__)

# Настройка базы данных и секретного ключа для сессий
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key_here'

# Инициализация базы данных
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Модель User для базы данных
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(50), default='user')


class Route(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    date = db.Column(db.Date, nullable=False)
    length = db.Column(db.Float, nullable=False)
    difficulty = db.Column(db.String(50), nullable=False)
    start_point = db.Column(db.String(100), nullable=False)
    end_point = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<Route {self.name}>'

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    route_id = db.Column(db.Integer, db.ForeignKey('route.id'), nullable=False)
    booking_date = db.Column(db.Date, nullable=False)
    user = db.relationship('User', backref=db.backref('bookings', lazy=True))
    route = db.relationship('Route', backref=db.backref('bookings', lazy=True))

    def __repr__(self):
        return f'<Booking {self.id} for {self.user.username} on {self.booking_date}>'

#  API ключ
API_KEY = '9fa38af01478a699fe825619f36cad31'
BASE_URL = 'https://api.openweathermap.org/data/2.5/weather'


# Функция для получения данных о погоде
def get_weather():
    city = 'Sevastopol'
    url = f'{BASE_URL}?q={city}&appid={API_KEY}&units=metric&lang=ru'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        weather = data['weather'][0]['description']
        temperature = data['main']['temp']
        humidity = data['main']['humidity']
        wind_speed = data['wind']['speed']
        return weather, temperature, humidity, wind_speed
    else:
        return None, None, None, "Ошибка запроса"



def create_admin():
    try:
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            new_admin = User(username='admin', password='admin_password', role='admin')
            db.session.add(new_admin)
            db.session.commit()
            print("Администратор был создан.")
    except Exception as e:
        print(f"Ошибка при создании администратора: {e}")


@app.route('/')
def index():
    weather, temperature, humidity, wind_speed = get_weather()
    return render_template('index.html', weather=weather, temperature=temperature,
                           humidity=humidity, wind_speed=wind_speed)


# Главная страница
@app.route('/home')
def home():
    username = session.get('username')
    return render_template('index.html', username=username)


# Страница о маршруте
@app.route('/trail_info')
def trail_info():
    weather, temperature, humidity, wind_speed = get_weather()
    return render_template('trail_info.html', weather=weather, temperature=temperature,
                           humidity=humidity, wind_speed=wind_speed)


# Страница контактов
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    weather, temperature, humidity, wind_speed = get_weather()
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        return redirect(url_for('home'))
    return render_template('contacts.html', weather=weather, temperature=temperature,
                           humidity=humidity, wind_speed=wind_speed)


# Страница регистрации
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user:
            return "Пользователь с таким именем уже существует."
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')


# Страница входа
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = user.username
            session['role'] = user.role  # Сохраняем роль пользователя в сессии

            if user.role == 'admin':
                return redirect(url_for('admin_panel'))  # Панель администратора
            else:
                return redirect(url_for('home'))
        else:
            error = "Неверное имя пользователя или пароль."

    return render_template('login.html', error=error)


# Панель администратора
@app.route('/admin')
def admin_panel():
    if session.get('role') != 'admin':
        return redirect(url_for('home'))

    users = User.query.all()  # Получаем всех пользователей
    routes = Route.query.all()  # Получаем все маршруты
    return render_template('admin_panel.html', users=users, routes=routes)

@app.route('/admin/add_route', methods=['GET', 'POST'])
def add_route():
    if session.get('role') != 'admin':
        return redirect(url_for('home'))

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        length = request.form.get('length')
        difficulty = request.form.get('difficulty')
        start_point = request.form.get('start_point')
        end_point = request.form.get('end_point')

        new_route = Route(
            name=name,
            description=description,
            date=date,
            length=length if length else None,
            difficulty=difficulty,
            start_point=start_point,
            end_point=end_point
        )

        db.session.add(new_route)
        db.session.commit()

        return redirect(url_for('admin_panel'))

    return render_template('add_route.html')  # Шаблон для создания маршрута

# Редактирование маршрута
@app.route('/admin/edit_route/<int:id>', methods=['GET', 'POST'])
def edit_route(id):
    if session.get('role') != 'admin':
        return redirect(url_for('home'))

    route = Route.query.get(id)  # Получаем маршрут по ID

    if request.method == 'POST':
        # Обновляем данные маршрута
        route.name = request.form['name']
        route.description = request.form['description']
        route.date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        route.length = request.form.get('length')
        route.difficulty = request.form.get('difficulty')
        route.start_point = request.form.get('start_point')
        route.end_point = request.form.get('end_point')

        db.session.commit()  # Сохраняем изменения

        return redirect(url_for('admin_panel'))

    return render_template('edit_route.html', route=route)


# Удаление маршрута
@app.route('/admin/delete_route/<int:id>', methods=['GET', 'POST'])
def delete_route(id):
    if session.get('role') != 'admin':
        return redirect(url_for('home'))

    route = Route.query.get(id)  # Получаем маршрут по ID

    if route:
        db.session.delete(route)  # Удаляем маршрут из базы данных
        db.session.commit()

    return redirect(url_for('admin_panel'))

@app.route('/booking', methods=['GET', 'POST'])
def booking():
    if not session.get('username'):
        return redirect(url_for('login'))  # Требуется авторизация

    routes = Route.query.all()  # Получаем все маршруты для выбора

    # Получаем пользователя по имени из сессии
    user = User.query.filter_by(username=session['username']).first()

    # Получаем все бронирования для текущего пользоваAaтеля
    bookings = Booking.query.filter_by(user_id=user.id).all()

    error_message = None  # Переменная для ошибки, если дата выбрана некорректно

    if request.method == 'POST':
        route_id = request.form['route_id']
        booking_date = datetime.strptime(request.form['booking_date'], '%Y-%m-%d').date()

        # Проверяем, что дата бронирования не раньше сегодняшнего дня
        if booking_date < datetime.today().date():
            error_message = "Дата бронирования должна быть не раньше сегодняшнего числа."
        else:
            # Создаем новое бронирование
            new_booking = Booking(
                user_id=user.id,
                route_id=route_id,
                booking_date=booking_date
            )

            db.session.add(new_booking)
            db.session.commit()

            return redirect(url_for('booking'))  # После бронирования оставляем пользователя на странице бронирования

    return render_template('booking.html', routes=routes, bookings=bookings, error_message=error_message)
@app.route('/cancel_booking/<int:booking_id>', methods=['POST'])
def cancel_booking(booking_id):
    if not session.get('username'):
        return redirect(url_for('login'))  # Требуется авторизация

    # Получаем бронирование по ID
    booking = Booking.query.get(booking_id)

    # Проверяем, что это бронирование принадлежит текущему пользователю
    if booking and booking.user_id == User.query.filter_by(username=session['username']).first().id:
        db.session.delete(booking)  # Удаляем бронирование
        db.session.commit()  # Применяем изменения в базе данных

    return redirect(url_for('booking'))  # Редирект на страницу бронирования

# Страница выхода
@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('role', None)  # Удаляем роль пользователя из сессии
    return redirect(url_for('home'))

@app.route('/trail_1')
def trail_1():
    weather, temperature, humidity, wind_speed = get_weather()
    return render_template('trail_1.html', weather=weather, temperature=temperature,
                           humidity=humidity, wind_speed=wind_speed)

@app.route('/trail_2')
def trail_2():
    weather, temperature, humidity, wind_speed = get_weather()
    return render_template('trail_2.html', weather=weather, temperature=temperature,
                           humidity=humidity, wind_speed=wind_speed)

@app.route('/trail_3')
def trail_3():
    weather, temperature, humidity, wind_speed = get_weather()
    return render_template('trail_3.html', weather=weather, temperature=temperature,
                           humidity=humidity, wind_speed=wind_speed)
# Запуск приложения
if __name__ == '__main__':
    app.run(debug=True)
