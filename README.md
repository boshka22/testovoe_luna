# 📋 Organization Directory API

Тестовое задание. REST API справочника организаций с поиском по зданию, виду деятельности и геопозиции.

## 🛠 Стек

| Слой        | Технология                      |
|-------------|---------------------------------|
| Язык        | Python 3.11                     |
| Фреймворк   | FastAPI                         |
| База данных | PostgreSQL 15 + SQLAlchemy async |
| Миграции    | Alembic                         |
| Контейнер   | Docker + docker-compose         |

---

## Быстрый старт

git clone https://github.com/boshka22/testovoe_luna

```bash
cp .env.example .env
docker-compose up --build
```

- Swagger: **http://localhost:8000/docs**

---

## Аутентификация

Все запросы требуют заголовок X-API-Key (задаётся в .env).


---

## API

### Здания

| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/buildings` | Список всех зданий |

### Организации

| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/organizations/{id}` | Карточка организации |
| GET | `/organizations?building_id=1` | По зданию |
| GET | `/organizations?activity_id=1` | По деятельности (включая дочерние) |
| GET | `/organizations?search=текст` | Поиск по названию |
| GET | `/organizations?lat=55.75&lon=37.61&radius_km=1` | В радиусе |
| GET | `/organizations?min_lat=&max_lat=&min_lon=&max_lon=` | Прямоугольник |

Пагинация: ?skip=0&limit=20. Фильтры взаимоисключающие — 400 при конфликте.

---

## Дерево деятельностей

Максимальная глубина вложенности — **3 уровня**:

```
Еда (1)
  └── Мясная продукция (2)
  └── Молочная продукция (3)
Автомобили (4)
  └── Грузовые (5)
  └── Легковые (6)
        └── Запчасти (7)
        └── Аксессуары (8)
```

Поиск по `activity_id=1` (Еда) вернёт организации с деятельностями
**Еда**, **Мясная продукция** и **Молочная продукция**.

---

## Тесты

```bash
docker-compose exec db psql -U postgres -c "CREATE DATABASE org_test;"
docker-compose exec web pip install -r requirements/test.txt
docker-compose exec web pytest
```

## Линтеры

```bash
pip install -r requirements/lint.txt
pre-commit install
black .
isort .
flake8 .
mypy app/
```

