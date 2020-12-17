# encoding: UTF-8

from typing import List, Dict

## Веб сервер
import cherrypy
from connect import getconn, putconn
from model import *
from peewee import prefetch

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
        # 1
        db = getconn()
        try:
            cur = db.cursor()
            if flight_date is None:
                cur.execute("SELECT id FROM Flight")
            else:
                cur.execute("SELECT id FROM Flight WHERE date = %s", (flight_date,))
            flight_ids = [row[0] for row in cur.fetchall()]
        finally:
            putconn(db)

        # Now let's check if we have some cached data, this will speed up performance, kek
        # Voila, now let's make sure all the flights we need are cached to boost performance.
        # Stupid database...
        # 8
        flights = FlightEntity.select().where(FlightEntity.id.in_(flight_ids))
        planets = PlanetEntity.select()
        flights_with_planets = prefetch(flights, planets)
        for flight in flights_with_planets:
            self.flight_cache[flight.id] = flight

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
    def delay_flights(self, flight_date=None, interval=None):
        if flight_date is None or interval is None:
            return "Please specify flight_date and interval arguments, like this: /delay_flights?flight_date=2084-06-12&interval=1week"
        # Make sure flights are cached
        flight_ids = self.cache_flights(flight_date)

        # Update flights, reuse connections 'cause 'tis faster
        # 1
        db = getconn()
        try:
            cur = db.cursor()

            # 2
            if flight_ids is None or len(flight_ids) == 0:
                return "There are no flights at " + flight_date

            # 3
            placeholders = ", ".join(["%s"] * len(flight_ids))
            query = "UPDATE Flight SET date=date + interval %s WHERE id IN ({})".format(placeholders)
            cur.execute(query, (interval,) + tuple(flight_ids))

            # 4
            db.commit()

            # 5
            for flight_id in flight_ids:
                del self.flight_cache[flight_id]
        finally:
            putconn(db)

    # Удаляет планету с указанным идентификатором.
    # Пример: /delete_planet?planet_id=1
    @cherrypy.expose
    def delete_planet(self, planet_id=None):
        if planet_id is None:
            return "Please specify planet_id, like this: /delete_planet?planet_id=1"
        db = getconn()
        cur = db.cursor()
        try:
            cur.execute("DELETE FROM Planet WHERE id = %s RETURNING id;", (planet_id,))
            result = cur.fetchall()
            # 7
            if len(result) <= 0:
                return "Planet with id " + planet_id + " not found"
            # 4
            db.commit()
        finally:
            # 1
            putconn(db)


if __name__ == '__main__':
    cherrypy.quickstart(App())
