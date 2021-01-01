# Третья контрольная курса Базы Данных в CSC
Контрольная работа модуля №3. Вариант 1


## Ошибки. 
#### файл connect.py

нет функции для возвращения сессии обратно в пулл.
Я бы добавила:
    def putconn(db):
        return pg_pool.putconn(db)

#### файл model.py
стр.28
Нет указания столбца
по моему должно быть
planet = ForeignKeyField(PlanetEntity, related_name='flights', column_name="id")
аналогичная ошибка в 47,48

стр.61
Для метода set_discount класса TicketEntity нет подтверждения операции: db.commit()

#### файл app.py

стр. 48
соединение указано не верно, должно быть
flight = FlightEntity.select().join(PlanetEntity).where(FlightEntity.planet == PlanetEntity.id).get()

стр.111
интервал указывается как "1week", но в запрос должно подставляться "1 week", то есть параметр interval нужно обработать.
в этой же строке нет db.commit() подтверждения операции

стр. 122
нет подтверждения операции db.commit()

с стр 34, 108 вместо конструкции "with" лучше использовать "try, finally", чтобы в блоке finally возвратить сессию в пул

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

