# encoding: UTF-8
# В этом файле реализованы Data Access Objects в виде классов Peewee ORM
from peewee import *

from connect import getconn, putconn
from connect import LoggingDatabase
from args import *

db = PostgresqlDatabase(args().pg_database, user=args().pg_user, host=args().pg_host, password=args().pg_password)
#db = LoggingDatabase(args())


# Классы ORM модели.
class PlanetEntity(Model):
    id = IntegerField()
    distance = DecimalField()
    name = TextField()

    class Meta:
        database = db
        db_table = "planet"


class FlightEntity(Model):
    id = IntegerField()
    date = DateField()
    available_seats = IntegerField()
    planet = ForeignKeyField(PlanetEntity, related_name='flights')

    class Meta:
        database = db
        db_table = "flightentityview"


class PriceEntity(Model):
    id = IntegerField()
    fare_code = IntegerField()
    price = IntegerField()

    class Meta:
        database = db
        db_table = "price"


class TicketEntity(Model):
    id = IntegerField()
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
        #with getconn() as db:
        try:
            cur = db.cursor()
            cur.execute("UPDATE FlightTicket SET discount=%s WHERE id=%s", (discount, self.id))
        finally:
            db.commit()
            putconn(db)


class BookingEntity(Model):
    ref_num = TextField()
    ticket = ForeignKeyField(TicketEntity)

    class Meta:
        database = db
        db_table = "booking"

