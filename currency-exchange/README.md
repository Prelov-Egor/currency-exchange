Сервис обмена валют (НБ РБ)
Веб-сервис для двухэтапного обмена валют по официальным курсам Национального банка Республики Беларусь.

Основные возможности
Автоматическое обновление: Ежедневное обновление курсов через API НБ РБ (в 00:05).

Двухэтапный обмен: Получение котировки → подтверждение или отклонение сделки.

Отчёты: Выгрузка сделок за любой выбранный период.

Управление сделками: Просмотр незавершённых операций и полная история.

Интерфейс: Современный веб-интерфейс на Bootstrap 5.

Как запустить
Способ 1: Стандартный запуск (рекомендуется для проверки)
Самый надежный способ развернуть проект со всеми зависимостями:

Создайте виртуальное окружение:

Bash
python -m venv .venv
Активируйте его:

Windows: .venv\Scripts\activate

macOS/Linux: source .venv/bin/activate

Установите зависимости:

Bash
pip install -r requirements.txt
Запустите сервер:

Bash
python main.py
Способ 2: Через Docker
Bash
docker-compose up --build
Сервер будет доступен по адресу: http://localhost:8000

Основные возможности API
GET / — Главная страница

POST /api/v1/exchange/quote — Получение котировки

POST /api/v1/exchange/confirm — Подтверждение сделки

GET /api/v1/deals/history — История сделок

GET /api/v1/reports/deals — Отчёт за период

Документация Swagger: http://localhost:8000/docs

Технологии
Backend: FastAPI, SQLAlchemy (Async), SQLite, APScheduler

Frontend: JavaScript (Fetch API), Bootstrap 5

Инструменты: Ruff, Black, Docker