# encoding: UTF-8

from typing import List, Dict

## Веб сервер
import cherrypy
from connect import connection_factory
from model import *

@cherrypy.expose
class App(object):
    flight_cache = ...  # type: Dict[int, FlightEntity]

    def __init__(self):
        self.flight_cache = dict()

    @cherrypy.expose
    def index(self):
        return """
        <html>
        <body>

        <p>Привет!</p> <p>Тебе интересно сходить на 
        <a href='/flights?flight_date=2084-06-12'>/flights</a>, 
        <a href='/delete_planet?planet_id=1'>/delete_planet</a> или 
        <a href='/delay_flights?flight_date=2084-06-12&interval=1day'>/delay_flights</p>
        </body>
        </html>"""

    def cache_flights(self, flight_date):
        flight_ids = []  # type: List[int]

        # Just get all needed flight identifiers
        with connection_factory.conn() as db:
            flight = FlightEntity.select().join(PlanetEntity)

            if flight_date is not None:
                flight = flight.where(FlightEntity.date == flight_date)

            flight_ids = [row.id for row in flight]
            for row in flight:
                self.flight_cache[row.id] = row

            return flight_ids

    # Отображает таблицу с полетами в указанную дату или со всеми полетами,
    # если дата не указана
    #
    # Пример: /flights?flight_date=2084-06-12
    #         /flights
    @cherrypy.expose
    def flights(self, flight_date=None):
        # Let's cache the flights we need
        flight_ids = self.cache_flights(flight_date)

        # Okeyla, now let's format the result HTML
        result_text = """
        <html>
        <body>
        <style>
    table > * {
        text-align: left;
    }
    td {
        padding: 5px;
    }
    table { 
        border-spacing: 5px; 
        border: solid grey 1px;
        text-align: left;
    }
        </style>
        <table>
            <tr><th>Flight ID</th><th>Date</th><th>Planet</th><th>Planet ID</th></tr>
        """
        for flight_id in flight_ids:
            flight = self.flight_cache[flight_id]
            result_text += f'<tr><td>{flight.id}</td><td>{flight.date}</td><td>{flight.planet.name}</td><td>{flight.planet.id}</td></tr>'
        result_text += """
        </table>
        </body>
        </html>
        """
        cherrypy.response.headers['Content-Type'] = 'text/html; charset=utf-8'
        return result_text

    # Сдвигает полёты, начинающиеся в указанную дату на указанный интервал.
    # Формат даты: yyyy-MM-dd (например 2019-12-19)
    # Формат интервала: 1day, 2weeks, и так далее.
    # https://www.postgresql.org/docs/current/datatype-datetime.html#DATATYPE-INTERVAL-INPUT
    #
    # пример: /delay_flights?flight_date=2084-06-12&interval=1day
    @cherrypy.expose
    def delay_flights(self, flight_date, interval):
        # Make sure flights are cached
        flight_ids = self.cache_flights(flight_date)

        # Update flights, reuse connections 'cause 'tis faster
        with connection_factory.conn() as db:
            cur = db.cursor()
            for id in flight_ids:
                cur.execute("UPDATE Flight SET date=date + interval %s WHERE id=%s", (interval, id))
                db.commit()

    # Удаляет планету с указанным идентификатором.
    # Пример: /delete_planet?planet_id=1
    @cherrypy.expose
    def delete_planet(self, planet_id):
        with connection_factory.conn() as db:
            cur = db.cursor()
            cur.execute("DELETE FROM Planet WHERE id = %s", (planet_id,))
            db.commit()


if __name__ == '__main__':
    cherrypy.quickstart(App())
