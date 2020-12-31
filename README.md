114 не указано в WHERE, что полет должен начаться в дату `flight_date`, но указан лишний `id`
предыдущая строка после этого не нужна
49-55 КЭШ не обновится, если удалить планету или сдвинуть полеты, еще и тормозит программу :()

# Третья контрольная курса Базы Данных в CSC
Контрольная работа модуля №3. Вариант 1




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

