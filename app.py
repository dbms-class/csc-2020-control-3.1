# encoding: UTF-8

from typing import List, Dict

## Веб сервер
import cherrypy
from connect import getconn
from model import *

@cherrypy.expose
class App(object):
    #flight_cache = ...  # type: Dict[int, FlightEntity]

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
        #with getconn() as db: #плохо использовать конструкцию with, так как сессия не возвращается в пулл сессий
        db = getconn()
        cur = db.cursor()
        try:
            if flight_date is None:
                cur.execute("SELECT id FROM Flight")
            else:
                cur.execute("SELECT id FROM Flight WHERE date = %s", (flight_date,))
            flight_ids = [row[0] for row in cur.fetchall()]
        finally:
            db.close()

        # Now let's check if we have some cached data, this will speed up performance, kek
        # Voila, now let's make sure all the flights we need are cached to boost performance.
        # Stupid database...
        flight = FlightEntity.select().join(PlanetEntity)
        for flight_id in flight_ids:
            if not flight_id in self.flight_cache:
                # OMG, cache miss! Let's fetch data
                #получается для каждого полета который еще не лежит в кеше будем все время делать join, а затем фильтрацию
                cur_flight = flight.where(FlightEntity.id == flight_id).execute() #get возвращает скаляр
                if cur_flight is not None:
                    self.flight_cache[flight_id] = cur_flight
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
        #with getconn() as db: такая же проблема
        db = getconn()
        cur = db.cursor()
        try:
            for id in flight_ids:
                #плохо что тут делает много запросов к одной таблице
                cur.execute("UPDATE Flight SET date=date + interval %s WHERE id=%s", (interval, id))
            # нужно сохранить изменение
            db.commit()
        finally:
            db.close()

    # Удаляет планету с указанным идентификатором.
    # Пример: /delete_planet?planet_id=1
    @cherrypy.expose
    def delete_planet(self, planet_id=None):
        if planet_id is None:
            return "Please specify planet_id, like this: /delete_planet?planet_id=1"
        db = getconn()
        cur = db.cursor()
        try:
            #проверить есть планета с данным id
            cur.execute("SELECT * FROM Planet WHERE id = %s", (planet_id,))
            #но сначала надо удалить все записи из таблиц Price и Flight,которые ссылаются на эту планету
            if cur.fetchone() is not None:
                cur.execute("DELETE FROM Price WHERE planet_id = %s", (planet_id,))
                cur.execute("DELETE FROM Flight WHERE planet_id = %s", (planet_id,))
                cur.execute("DELETE FROM Planet WHERE id = %s", (planet_id,))
            #нужно сохранить изменение
            db.commit()
        finally:
            db.close()


if __name__ == '__main__':
    cherrypy.quickstart(App())
