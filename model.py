# encoding: UTF-8
# В этом файле реализованы Data Access Objects в виде классов Peewee ORM
from peewee import *
from connect import getconn
from connect import LoggingDatabase
from args import *

#db = PostgresqlDatabase(args().pg_database, user=args().pg_user, host=args().pg_host, password=args().pg_password)
#наверное не надо создавать новый пулл сессий
db = getconn()
#db = LoggingDatabase(args())


# Классы ORM модели.
class PlanetEntity(Model):
    id = IntegerField() #AutoField() не будет ругаться на то что нет primary key?
    distance = DecimalField()
    name = TextField()

    class Meta:
        database = db
        db_table = "planet"


class FlightEntity(Model):
    id = IntegerField() #AutoField()
    date = DateField()
    available_seats = IntegerField()
    planet = ForeignKeyField(PlanetEntity, related_name='flights')

    class Meta:
        database = db
        db_table = "flightentityview"


class PriceEntity(Model):
    id = IntegerField() #AutoField()
    planet = ForeignKeyField(PlanetEntity, related_name='price')
    #добавить ограничение, точно не знаю как правильно
    fare_code = IntegerField(constraints=[Check('fare_code BETWEEN 1 AND 10')])
    price = IntegerField()
    #UNIQUE(planet_id, fare_code) нет проверки

    class Meta:
        database = db
        db_table = "price"


class TicketEntity(Model):
    id = IntegerField() #AutoField()
    price = ForeignKeyField(PriceEntity)
    flight = ForeignKeyField(FlightEntity)
    discount = DecimalField()

    class Meta:
        database = db
        db_table = "flightticket"

    # Тут целочисленное значение атрибута Price.fare_code из интервала [1..10] конвертируется в
    # символ от A до J
    def fare(self):
        return chr(ord('A') + self.price.fare_code - 1)

    # Устанавливает размер скидки на билет
    def set_discount(self, discount):
        db = getconn()
        cur = db.cursor()
        #используем пулл сессий
        try:
            cur = db.cursor()
            cur.execute("UPDATE FlightTicket SET discount=%s WHERE id=%s", (discount, self.id))
            db.commit()
        finally:
            db.close()


class BookingEntity(Model):
    ref_num = TextField()
    ticket = ForeignKeyField(TicketEntity)

    class Meta:
        database = db
        db_table = "booking"

