# Третья контрольная курса Базы Данных в CSC
Контрольная работа модуля №3. Вариант 1

### Найденные ошибки
[file]:[line]: description: solution (optional)

- connect.py:19: фукнция get_conn берет сессию из пула, которую надо вернуть самостоятельно:
Сделал peewee pool и фабрику, которая автоматически возвращает сессию в пул - это позволит не думать нигде об этом в коде.
- app.py:45: тут какое-то безумие с кэшом - на каждый отсутствующий ключ делается отдельный запрос к БД:
вместо этого можно сразу вытащить все нужные данные и сложить в кэш (хотя дальше мы им всё равно не пользуемся,
но допустим хотим пользоваться в будущем)
- marsoflot.sql: сделал factor типов FLOAT, чтобы тестироваться на маленьких таблицах
- marsoflot.sql:80: внутри VIEW на каждый полёт вызывается GetBookedSeats, что (предположительно) приводит к огромногому числу запросов:
на самом деле не понял, почему делается так много подзапросов. Попробовал убрать GetBookedSeats и сделать join таблиц, но лучше не стало(( 
- webapp.py: flight_date и interval обязательные аргументы, но почему-то обхявлены опциональными:
переделал на обязательные
- webapp.py: ^ то же с plande_id 
- webapp.py: расставил db.commit(), где его не хватало

### Инициализация БД
по умолчанию пользователь postgres с пустым паролем на localhost:5432/postgres

```
psql -h localhost -U postgres -f marsoflot.sql
```

### Запуск приложения
```
python3 app.py
```

Если нужно поменять хост, порт, пользователя, базу данных или пароль, воспользуйтесь аргументами командной строки. `python3 app.py -h`  вам про них расскажут.

### Как сдавать
Пул-реквест в репозиторий `github.com/dbms-class/csc-2020-control-3.1` или письмо с заархивированным кодом на `dmitry+csc@barashev.net`. Пожалуйста, не присылайте в архиве каталоги `build`, `.gradle` и `.idea` 

