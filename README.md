# Тестовое задание Secunda

Сервис обработки платежей на основе [задания](./task.md).

## Для запуска нужно

- Docker Compose
- `uv`

## Запуск

```sh
cp .env.example .env
docker compose up
```

## Адреса

- API: http://localhost:8000/api/v1
- Swagger UI: http://localhost:8000/docs

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
