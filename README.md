# Backend сервиса авторизации

https://github.com/Ezereul/Auth_sprint_1

Backend сервиса авторизации с системой ролей на FastAPI.

---

## Установка

```bash
$ git clone git@github.com:Ezereul/Auth_sprint_1.git
```


## Подготовка переменных окружения
Перед первым запуском нужно подготовить переменные окружения.

В директории с проектом последовательно запустить:

```shell
$ mv .env.template .env
$ openssl genrsa -out rsa.key 2048
$ openssl rsa -in rsa.key -pubout > rsa.key.pub
```
Затем открыть файл `.env` в любом текстовом редакторе. 
В качестве значения переменной `AUTHJWT_PRIVATE_KEY` установить значение из файла `rsa.key`.
В качестве значения переменной `AUTHJWT_PUBLIC_KEY` установить значение из файла `rsa.key.pub`.


## Запуск

Проект запускается командой `docker compose up`. Применение миграций и создание стандартных ролей произойдёт автоматически.

После запуска можно сразу регистрировать нового пользователя.

## Запуск тестов

Тесты запускаются на отдельном образе postgres-test:

```shell
docker compose -f docker-compose-test.yml up -d postgres-test
poetry run pytest
```

## Документация API

Документация доступна по url: `http://0.0.0.0/docs`.
