# Science Helpy

> Мультиагентный сервис для поиска, скачивания и LLM-анализа научных статей на arXiv

**Авторы:** Степовой Кирилл, Тугов Денис

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black)](https://react.dev/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](https://docs.docker.com/compose/)

## Демонстрация

| Формат | Ссылка |
|--------|--------|
| CLI | [Google Drive](https://drive.google.com/file/d/15UfV33nzn90dD-_NxCi10xk7A5us9KF7/view?usp=drive_link) |
| Frontend | [Google Drive](https://drive.google.com/drive/folders/1T3pY8CQugVzKjKJN6LicxbuxGhLUjd9B?usp=sharing) |
| Материалы в репозитории | [`docs/`](docs/) |


Единый репозиторий сервиса для поиска научных статей на arXiv, скачивания исходных материалов, парсинга содержимого, LLM-оценки статьи и генерации обзорного текста. Проект состоит из React frontend, FastAPI backend и отдельного модуля `agents_system`, в котором живут мультиагентные сценарии анализа.

## Что входит в проект

- `frontend` — пользовательский интерфейс на React, TypeScript, Vite, Tailwind CSS, React Query и Zustand.
- `backend` — HTTP API на FastAPI с разделением по слоям DDD.
- `agents_system` — LangGraph/LangChain-оркестрация, агенты и инструменты для работы со статьями и изображениями.
- `docker-compose.yml` — локальная среда разработки из frontend, backend API и PostgreSQL.
- `Dockerfile` — образ backend, который копирует и `backend`, и `agents_system`, чтобы API мог обращаться к агентам напрямую.

## Быстрый запуск через Docker Compose

### Требования

- Docker Engine
- Docker Compose Plugin

Проверка:

```bash
docker --version
docker compose version
```

### 1. Подготовьте переменные окружения

Для backend нужен файл `backend/.env`. Быстрый старт:

```bash
cp backend/env.example backend/.env
```

Минимально имеет смысл проверить такие переменные:

```env
DEBUG=True
DATABASE_URL=postgresql://postgres:postgres@db:5432/science_helpy
OPENROUTER_API_KEY=
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
TAVILY_API_KEY=
```

Важно:

- `OPENROUTER_API_KEY` обязателен для сценариев, где backend вызывает `CoordinatorAgent` и `GraphMAS`.
- Без `OPENROUTER_API_KEY` API поднимется, но операции поиска, скачивания, оценки и генерации обзора через агентов будут возвращать ошибку доступности сервиса.
- `TAVILY_API_KEY` нужен только там, где агенту требуется веб-поиск для дополнительного контекста.

### 2. Поднимите весь стек

Из корня репозитория:

```bash
docker compose up --build
```

После запуска будут доступны:

- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- PostgreSQL: `localhost:5433`

### 3. Остановите стек

```bash
docker compose down
```

Если нужно удалить volume PostgreSQL:

```bash
docker compose down -v
```

### Что именно делает Compose

`docker-compose.yml` поднимает 3 сервиса:

1. `db`
   PostgreSQL 15 в контейнере `science_helpy_db`, наружу проброшен порт `5433`.

2. `api`
   Backend в контейнере `science_helpy_api`, запускается командой:

   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

   В контейнер монтируется весь репозиторий как `/app`, поэтому изменения в `backend` и `agents_system` видны без пересборки образа.

3. `frontend`
   Vite dev server в контейнере `science_helpy_frontend`, запускается командой:

   ```bash
   npm run dev -- --host 0.0.0.0 --port 5173
   ```

   Для `node_modules` используется отдельный volume `frontend_node_modules`.

### Важное замечание про PostgreSQL

Сервис `db` и SQLAlchemy-конфигурация в проекте есть, но на текущем этапе backend хранит статьи, оценки и обзоры в in-memory репозиториях:

- `backend/app/infrastructure/repositories/article_repository_impl.py`
- `backend/app/infrastructure/repositories/evaluation_repository_impl.py`
- `backend/app/infrastructure/repositories/review_repository_impl.py`

Это означает:

- данные не переживают перезапуск backend-контейнера;
- PostgreSQL пока не используется как основное runtime-хранилище для этих сущностей;
- наличие `db` в compose подготавливает окружение под будущий переход на постоянное хранение.

## Локальный запуск без Docker

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp env.example .env
python main.py
```

Альтернатива:

```bash
cd backend
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm ci
npm run dev
```

По умолчанию frontend отправляет запросы на префикс `/api/v1`, а Vite проксирует `/api` на `http://127.0.0.1:8000`. В Docker это значение переопределяется переменной `VITE_API_PROXY_TARGET=http://api:8000`.

## Пользовательский сценарий

Базовый поток работы такой:

1. Пользователь вводит поисковый запрос во frontend.
2. Frontend вызывает `POST /api/v1/articles/search`.
3. Backend через `OrchestrationService` обращается к `CoordinatorAgent`, который ищет статьи в arXiv.
4. После выбора статьи frontend вызывает `POST /api/v1/articles/download`.
5. Backend скачивает PDF и, если доступно, TeX, затем сохраняет метаданные статьи во внутреннем репозитории.
6. Для текстового содержимого frontend запускает `POST /api/v1/articles/{article_id}/parse`.
7. Для оценки статьи frontend вызывает `POST /api/v1/evaluations/evaluate`.
8. Для генерации обзорного текста frontend вызывает `POST /api/v1/reviews/write`.

## Архитектура

### Общая схема

Проект разделен на три крупных части:

- frontend отвечает только за пользовательский сценарий и визуализацию результатов;
- backend отвечает за HTTP API, прикладные сценарии и адаптацию ответов агентов в доменные сущности;
- `agents_system` инкапсулирует мультиагентную обработку статьи, работу с arXiv, парсинг файлов и генерацию LLM-результатов.

Поток данных выглядит так:

```text
React UI
  -> FastAPI endpoints
  -> use cases application layer
  -> domain repositories / orchestration service
  -> agents_system
  -> внешние сервисы: arXiv, OpenRouter, Tavily
```

### Backend: слои и ответственность

Структура backend:

```text
backend/
├── app/
│   ├── domain/
│   ├── application/
│   ├── infrastructure/
│   ├── presentation/
│   └── shared/
├── main.py
├── requirements.txt
└── env.example
```

#### 1. `domain`

Слой домена содержит бизнес-сущности и контракты.

- `entities/article.py` — сущность статьи.
- `entities/evaluation.py` — сущность оценки статьи.
- `entities/review.py` — сущность обзорного текста.
- `repositories/*.py` — абстракции репозиториев для статей, оценок и обзоров.

Задача этого слоя — не знать ничего о FastAPI, LangGraph, HTTP и конкретных хранилищах.

#### 2. `application`

Слой сценариев использования.

- `use_cases/search_articles.py` — поиск по запросу.
- `use_cases/download_article.py` — загрузка статьи и создание сущности.
- `use_cases/parse_article.py` — получение распарсенного текста.
- `use_cases/evaluate_article.py` — запуск оценки и сохранение результата.
- `use_cases/write_review.py` — запуск генерации обзора и сохранение результата.

Также здесь находятся:

- `dto/` — DTO и мапперы между доменными сущностями и API-ответами;
- `services/orchestration_service.py` — главный адаптер между backend и `agents_system`;
- `services/agent_service.py` — дополнительный адаптер для прямой работы с отдельными агентами.

Ключевая идея: use case знает только о репозиториях и сервисах, а не о деталях HTTP или LangGraph.

#### 3. `infrastructure`

Технические реализации и конфигурация.

- `config/settings.py` — чтение настроек через `pydantic-settings`.
- `repositories/*_impl.py` — текущие in-memory реализации репозиториев.
- `database/base.py` — подготовка SQLAlchemy engine и session factory.
- `external/arxiv_client.py`, `external/file_service.py` — заготовки и интеграционные компоненты для внешних систем.

Сейчас инфраструктурный слой частично готов под постоянное хранилище, но основной runtime-контур работает через память процесса.

#### 4. `presentation`

Внешний API-слой.

- `api/v1/articles.py`
- `api/v1/evaluations.py`
- `api/v1/reviews.py`
- `dependencies.py` — singleton-экземпляры репозиториев и сервисов.
- `schemas/` — Pydantic-схемы запросов и ответов.
- `middleware/error_handler.py` — унификация обработки доменных ошибок.

`backend/app/main.py` создает FastAPI-приложение, настраивает CORS и подключает роутер `/api/v1`.

### Backend: ключевой сервис оркестрации

`backend/app/application/services/orchestration_service.py` — основной мост между API и агентной системой.

Он отвечает за:

- проброс переменных окружения для `agents_system`;
- ленивую инициализацию `CoordinatorAgent` и `GraphMAS`;
- запуск поиска статей;
- скачивание PDF и TeX;
- парсинг содержимого статьи;
- получение структурированной оценки;
- генерацию полного обзора статьи и разбиение его на секции.

Именно здесь backend превращает "сырой" вывод инструментов и агентов в DTO, с которыми уже работают use case и API.

### agents_system: как устроена мультиагентная часть

Структура:

```text
agents_system/
├── agents/
│   ├── coordinator_agent.py
│   ├── describe_agent.py
│   ├── review_agent.py
│   └── writer_agent.py
├── agent_tools/
│   └── tools.py
└── graph_mas.py
```

Роли компонентов:

- `CoordinatorAgent`
  Управляет высокоуровневым сценарием: поиск статьи, скачивание, выбор следующего шага, вызов инструментов.

- `DescribeAgent`
  Описывает извлеченные изображения из статьи.

- `EvalAgent`
  Возвращает структурированную оценку статьи с баллами, сильными и слабыми сторонами.

- `WriterAgent`
  Пишет обзор статьи и может генерировать дополнительные текстовые артефакты.

- `agent_tools/tools.py`
  Инструменты для поиска arXiv, скачивания PDF/TeX, парсинга PDF и TeX, извлечения изображений.

- `graph_mas.py`
  Собирает state graph поверх LangGraph и маршрутизирует поток между агентами в зависимости от команды пользователя и текущего состояния.

### Как backend использует `agents_system`

Есть два режима интеграции.

1. Прямой вызов координатора

Используется для поиска и скачивания. Backend формирует `HumanMessage`, передает его `CoordinatorAgent`, затем разбирает `ToolMessage` и вытаскивает из него артефакты.

2. Полный граф `GraphMAS`

Используется для оценки и обзора. Backend подает в граф путь к статье, распарсенный текст и путь к извлеченным изображениям, а затем получает:

- `review_data` для оценки;
- `written_review` для обзорного текста;
- промежуточное состояние, которое можно сохранить в сущность статьи.

### Frontend: структура и поток данных

Frontend организован в разрезе `app / pages / widgets / features / entities / shared`.

Основные каталоги:

```text
frontend/src/
├── app/
├── pages/
├── widgets/
├── features/
├── entities/
└── shared/
```

#### `app`

- `App.tsx` — корневой компонент.
- `router/AppRouter.tsx` — маршрутизация. Сейчас в проекте один экран `/`.
- `providers/query-client.ts` — инициализация React Query.

#### `pages`

- `pages/home/HomePage.tsx` — собирает главный экран.

#### `widgets`

Крупные UI-блоки страницы:

- `widgets/app-shell/AppShell.tsx` — основная раскладка интерфейса;
- `widgets/article-hub/ArticleHub.tsx` — рабочая область выбранной статьи;
- `widgets/activity-overview/ActivityOverview.tsx` — дополнительный блок активности, сейчас не подключен в `AppShell`.

#### `features`

Функциональные сценарии пользователя:

- `features/article-search/ui/ArticleSearch.tsx` — форма и логика поиска;
- `features/article-picker/model/use-selected-article.ts` — выбор текущей статьи.

#### `entities`

- `entities/article/api/article-api.ts` — React Query hooks для вызова backend API.

Именно этот слой связывает UI с backend:

- `useArticles`
- `useArticleDetail`
- `useArticleParse`
- `useArticleEvaluation`
- `useGenerateArticleEvaluation`
- `useArticleReview`
- `useGenerateArticleReview`

#### `shared`

Переиспользуемые примитивы:

- `shared/api/http.ts` — `axios` instance с базовым префиксом `/api/v1`;
- `shared/types/article.ts` — типы frontend-модели;
- `shared/ui/` — кнопки, карточки, dialog и другие UI-компоненты.

### Контур запросов между frontend и backend

Frontend работает только с HTTP API backend и не общается с агентами напрямую.

Используемые endpoint:

- `POST /api/v1/articles/search`
- `POST /api/v1/articles/download`
- `POST /api/v1/articles/{article_id}/parse`
- `GET /api/v1/articles/{article_id}`
- `POST /api/v1/evaluations/evaluate`
- `GET /api/v1/evaluations/article/{article_id}`
- `POST /api/v1/reviews/write`
- `GET /api/v1/reviews/article/{article_id}`
- `GET /api/v1/health`

### Хранение состояния

В проекте есть несколько уровней состояния:

- клиентское состояние выбора статьи и кэша запросов во frontend;
- runtime-состояние доменных сущностей в in-memory репозиториях backend;
- состояние выполнения графа в `GraphMAS` через `MemorySaver`;
- файловые артефакты на диске: скачанные PDF/TeX и извлеченные изображения.

Практическое следствие:

- после рестарта backend пропадут сохраненные в памяти статьи, оценки и обзоры;
- скачанные файлы на смонтированном диске репозитория сохранятся;
- повторный запрос после рестарта backend может потребовать повторного скачивания и анализа.

## API

### `POST /api/v1/articles/search`

Ищет статьи в arXiv по текстовому запросу.

Пример:

```json
{
  "query": "retrieval augmented generation",
  "max_results": 10
}
```

### `POST /api/v1/articles/download`

Скачивает статью по `arxiv_id`, возвращает внутренний `UUID` и локальные пути к файлам, если они получены.

Пример:

```json
{
  "arxiv_id": "2501.12345"
}
```

### `POST /api/v1/articles/{article_id}/parse`

Парсит текст статьи из TeX или PDF и сохраняет результат в сущность статьи.

### `POST /api/v1/evaluations/evaluate`

Запускает LLM-оценку статьи.

Пример:

```json
{
  "article_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### `POST /api/v1/reviews/write`

Генерирует структурированный обзор статьи на русском языке.

## Технологии

### Frontend

- React 19
- TypeScript
- Vite
- Tailwind CSS
- TanStack Query
- Axios
- Zustand
- React Router

### Backend

- Python 3.11
- FastAPI
- Pydantic
- SQLAlchemy
- Uvicorn

### Agent layer

- LangGraph
- LangChain
- OpenRouter
- Tavily
- arXiv integration
- PDF/TeX parsing utilities

## Структура репозитория

```text
science-helpy/
├── agents_system/
├── backend/
├── frontend/
├── docs/
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## Ограничения текущей реализации

- PostgreSQL поднимается, но еще не является основным хранилищем прикладных сущностей.
- Репозитории backend живут в памяти процесса.
- Для работы агентных сценариев нужны внешние ключи и доступ к LLM-провайдеру.
- Часть поведения завязана на парсинг текстового вывода инструментов, поэтому при изменении формата ответа агентов потребуется синхронно обновлять backend-адаптер.

## Куда смотреть в коде в первую очередь

- `docker-compose.yml` — локальная оркестрация сервисов.
- `Dockerfile` — сборка backend вместе с `agents_system`.
- `backend/app/main.py` — создание FastAPI-приложения.
- `backend/app/application/services/orchestration_service.py` — главный интеграционный слой с агентами.
- `backend/app/presentation/api/v1/` — HTTP endpoints.
- `frontend/src/entities/article/api/article-api.ts` — клиентский слой запросов.
- `agents_system/graph_mas.py` — граф мультиагентной обработки.


