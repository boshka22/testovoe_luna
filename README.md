# Organization Directory API

REST API справочника организаций с поиском по зданию, деятельности и геопозиции.

## Стек

| Слой        | Технология                      |
|-------------|---------------------------------|
| Язык        | Python 3.11                     |
| Фреймворк   | FastAPI                         |
| База данных | PostgreSQL 15 + SQLAlchemy async |
| Миграции    | Alembic                         |
| Контейнер   | Docker + docker-compose         |

---

## Быстрый старт

```bash
cp .env.example .env
docker-compose up --build
```

- API: **http://localhost:8000**
- Swagger: **http://localhost:8000/docs**

---

## Аутентификация

Все запросы требуют заголовок `X-API-Key`:

```bash
curl -H "X-API-Key: secret-api-key-change-me" http://localhost:8000/buildings
```

Ключ задаётся в `.env` → `API_KEY`.

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
| GET | `/organizations?activity_id=1` | По деятельности (с дочерними) |
| GET | `/organizations?search=текст` | Поиск по названию |
| GET | `/organizations?lat=55.75&lon=37.61&radius_km=1` | В радиусе |
| GET | `/organizations?min_lat=&max_lat=&min_lon=&max_lon=` | В прямоугольнике |

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
