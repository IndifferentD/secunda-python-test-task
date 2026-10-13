# Тестовое задание Secunda: асинхронный сервис процессинга платежей

Решение [тестового задания](./task.md) на позицию Python-разработчика.

## Требования

- Docker Compose
- `uv` для локальной работы

## Запуск

```sh
cp .env.example .env
docker compose up
```

## Сервисы

- `api` создаёт платежи и отдаёт информацию о них.
  - API: http://localhost:8000/api/v1
  - Swagger UI: http://localhost:8000/docs
- `outbox` публикует в очередь задачи на обработку платежей.
- `worker` обрабатывает платежи и отправляет webhook.

## Примеры запросов

### Создать платёж

```sh
curl -X POST http://localhost:8000/api/v1/payments \
  -H 'X-API-Key: api-key' \
  -H 'Idempotency-Key: payment-1' \
  -H 'Content-Type: application/json' \
  -d '{"amount":"100.00","currency":"RUB","description":"Тестовый платёж","metadata":{},"webhook_url":"https://your-service.example/webhook"}'
```

### Получить платёж

```sh
curl -H 'X-API-Key: api-key' http://localhost:8000/api/v1/payments/PAYMENT_ID
```
