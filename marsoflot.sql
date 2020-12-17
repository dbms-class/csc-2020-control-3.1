-- Справочник политических строев
DROP TABLE IF EXISTS Government CASCADE;
CREATE TABLE Government(id SERIAL PRIMARY KEY, value TEXT UNIQUE);

-- Планета, её название, расстояние до Земли, политический строй
DROP TABLE IF EXISTS Planet CASCADE;
CREATE TABLE Planet(
  id SERIAL PRIMARY KEY,
  name TEXT UNIQUE,
  distance NUMERIC(5,2),
  government_id INT REFERENCES Government);

-- Значения рейтинга пилотов
DROP TYPE IF EXISTS Rating CASCADE;
CREATE TYPE Rating AS ENUM('Harmless', 'Poor', 'Average', 'Competent', 'Dangerous', 'Deadly', 'Elite');

-- Пилот корабля
DROP TABLE IF EXISTS Commander CASCADE;
CREATE TABLE Commander(
  id SERIAL PRIMARY KEY,
  name TEXT UNIQUE,
  rating Rating);

-- Космический корабль, вместимость пассажиров и класс корабля
DROP TABLE IF EXISTS Spacecraft CASCADE;
CREATE TABLE Spacecraft(
  id SERIAL PRIMARY KEY,
  capacity INT CHECK(capacity > 0),
  name TEXT UNIQUE,
  class INT CHECK(class BETWEEN 1 AND 3));

-- Полет на планету в означеную дату, выполняемый кораблем, пилотируемый капитаном
DROP TABLE IF EXISTS Flight CASCADE;
CREATE TABLE Flight(id INT PRIMARY KEY,
  spacecraft_id INT REFERENCES Spacecraft,
  commander_id INT REFERENCES Commander,
  planet_id INT REFERENCES Planet ON DELETE CASCADE,
  date DATE
);

-- Стоимость полета до планеты по означенному классу обслуживания
DROP TABLE IF EXISTS Price CASCADE;
CREATE TABLE Price(
  id INT PRIMARY KEY,
  planet_id INT REFERENCES Planet ON DELETE CASCADE,
  fare_code INT CHECK(fare_code BETWEEN 1 AND 10),
  price INT CHECK(price>0),
  UNIQUE(planet_id, fare_code)
);

-- Билет на полёт по указанному тарифу с некоторой скидкой (или наценкой)
-- атрибут discount является множителем для цены.
DROP TABLE IF EXISTS FlightTicket CASCADE;
CREATE TABLE FlightTicket(
  id INT PRIMARY KEY,
  flight_id INT REFERENCES Flight ON DELETE CASCADE ,
  price_id INT REFERENCES Price ON DELETE CASCADE,
  discount NUMERIC(3,2) DEFAULT 1 CHECK(discount >= 0)
);

-- Раса пассажира
DROP TYPE IF EXISTS Race CASCADE;
CREATE TYPE Race AS ENUM('Elves', 'Men', 'Trolls');

-- Пассажир
DROP TABLE IF EXISTS Pax CASCADE;
CREATE TABLE Pax(
  id INT PRIMARY KEY,
  name TEXT,
  race Race);

-- Резервирование места на полет
DROP TABLE IF EXISTS Booking CASCADE;
CREATE TABLE Booking(
  ref_num TEXT PRIMARY KEY,
  pax_id INT REFERENCES Pax,
  ticket_id INT REFERENCES FlightTicket ON DELETE CASCADE);

CREATE OR REPLACE FUNCTION GetBookedSeats(_flight_id INT) RETURNS BIGINT AS $$
SELECT COUNT(*) FROM Booking B JOIN FlightTicket T ON ticket_id = T.id WHERE T.flight_id=_flight_id;
$$ LANGUAGE SQL;

CREATE OR REPLACE VIEW FlightAvailableSeatsView AS
SELECT flight_id, capacity - booked_seats AS available_seats
FROM (
         SELECT F.id AS flight_id, date, capacity, GetBookedSeats(F.id) AS booked_seats
         FROM Flight F JOIN Spacecraft S ON F.spacecraft_id = S.id
     ) T;

CREATE OR REPLACE VIEW FlightEntityView AS
SELECT id, date, available_seats, planet_id
FROM Flight F JOIN FlightAvailableSeatsView S ON F.id = S.flight_id;



-----------------------------------------------------------------------
-- Функция GenerateData генерирует тестовые данные с заданным коэффициентом масштабирования
-- При значении factor=1 в базе будет 500 полётов, 50 пассажиров, около 7000 билетов и 3500 бронирований
-- При увеличении factor количество записей пропорционально увеличивается


CREATE OR REPLACE FUNCTION GenerateData(factor FLOAT) RETURNS VOID AS $$
BEGIN
-- ================================
-- Перечисление государственных устройств
INSERT INTO Government(value)
SELECT unnest(ARRAY['Анархия', 'Коммунизм', 'Конфедерация', 'Олигархия', 'Демократия', 'Диктатура', 'Феодализм']);

-- ================================
-- Капитаны со случайными рейтингами
WITH Names AS (
  SELECT unnest(ARRAY['Громозека', 'Ким', 'Буран', 'Зелёный', 'Горбовский', 'Ийон Тихий', 'Форд Префект', 'Комов', 'Каммерер', 'Гагарин', 'Титов', 'Леонов', 'Крикалев', 'Армстронг', 'Олдрин']) AS name
), Ratings AS (
  select enumsortorder AS rating_num, enumlabel::Rating AS rating_value
  from pg_catalog.pg_enum
  WHERE enumtypid = 'rating'::regtype ORDER BY enumsortorder
),
NameRating AS (
  SELECT name, (0.5 + random() * (SELECT MAX(rating_num) FROM Ratings))::int
  AS rating_num FROM Names
)
INSERT INTO Commander(name, rating)
SELECT name, rating_value FROM NameRating JOIN Ratings USING(rating_num);

-- ================================
-- Перечисление планет со случайными расстояниями и правительствами
WITH PlanetNames AS (
  SELECT unnest(ARRAY[
    'Tibedied', 'Qube', 'Leleer', 'Biarge', 'Xequerin', 'Tiraor', 'Rabedira', 'Lave',
    'Zaatxe', 'Diusreza', 'Teaatis', 'Riinus', 'Esbiza', 'Ontimaxe', 'Cebetela', 'Ceedra',
    'Rizala', 'Atriso', 'Teanrebi', 'Azaqu', 'Retila', 'Sotiqu', 'Inleus', 'Onrira', 'Ceinzala',
    'Biisza', 'Legees', 'Quator', 'Arexe', 'Atrabiin', 'Usanat', 'Xeesle', 'Oreseren', 'Inera',
    'Inus', 'Isence', 'Reesdice', 'Terea', 'Orgetibe', 'Reorte', 'Ququor', 'Geinona',
    'Anarlaqu', 'Oresri', 'Esesla', 'Socelage', 'Riedquat', 'Gerege', 'Usle', 'Malama',
    'Aesbion', 'Alaza', 'Xeaqu', 'Raoror', 'Ororqu', 'Leesti', 'Geisgeza', 'Zainlabi',
    'Uscela', 'Isveve', 'Tioranin', 'Learorce', 'Esusti', 'Ususor', 'Maregeis', 'Aate',
    'Sori', 'Cemave', 'Arusqudi', 'Eredve', 'Regeatge', 'Edinso', 'Ra', 'Aronar',
    'Arraesso', 'Cevege', 'Orteve', 'Geerra', 'Soinuste', 'Erlage', 'Xeaan', 'Veis',
    'Ensoreus', 'Riveis', 'Bivea', 'Ermaso', 'Velete', 'Engema', 'Atrienxe', 'Beusrior',
    'Ontiat', 'Atarza', 'Arazaes', 'Xeeranre', 'Quzadi', 'Isti', 'Digebiti', 'Leoned',
    'Enzaer', 'Teraed'
  ]) AS name
)
INSERT INTO Planet(name, distance, government_id)
SELECT name, (random() * 1000)::numeric(5,2), (0.5 + random() * (SELECT COUNT(*) FROM Government))::int
FROM PlanetNames;

DROP SEQUENCE IF EXISTS price_id;
CREATE SEQUENCE price_id;
-- ================================
-- Стоимость билета увеличивается с увеличением расстояния и повышением класса обслуживания
WITH Planets AS (
  SELECT id, distance, random() + 0.5 AS coeff FROM Planet
), Fares AS (
  SELECT generate_series(1,10) AS fare, random() AS coeff
)
INSERT INTO Price(id, planet_id, fare_code, price)
SELECT nextval('price_id'), Planets.id, fare, ((distance * Planets.coeff) + 10 * (Fares.coeff + Fares.fare))::INT
FROM Planets CROSS JOIN Fares;


-- ================================
-- Перечисление кораблей со случайными классами и вместимостью
WITH Names AS (
  SELECT unnest(ARRAY[
      'Кедр', 'Орел', 'Сокол', 'Беркут', 'Ястреб', 'Чайка', 'Рубин', 'Алмаз', 'Аргон', 'Амур', 'Байкал', 'Антей', 'Буран'
  ]) AS name
)
INSERT INTO Spacecraft(name, capacity, class)
SELECT name, (3+random()*20)::INT, (0.5+random()*3)::INT
FROM Names;

-- ================================
-- Случайные полеты
WITH MaxValues AS (
  SELECT (SELECT MAX(id) FROM Spacecraft) AS spacecraft,
  (SELECT MAX(id) - 1 FROM Commander) AS commander,
  (SELECT MAX(id) FROM Planet) AS planet
),
Flights AS (
  SELECT generate_series(1, (500*factor)::INT) AS id
)
INSERT INTO Flight(id, spacecraft_id, commander_id, planet_id, date)
SELECT id, (0.5 + random()*spacecraft)::INT,
    (0.5 + random()*commander)::INT,
    (0.5 + random()*planet)::INT,
    ('2084-01-01'::DATE + random()*365*5 * INTERVAL '1 day')::DATE
FROM MaxValues CROSS JOIN Flights;

DROP SEQUENCE IF EXISTS ticket_id;
CREATE SEQUENCE ticket_id;

WITH T AS (
    SELECT F.id, S.capacity, F.planet_id
    FROM Flight F JOIN Spacecraft S ON F.spacecraft_id = S.id
)
INSERT INTO FlightTicket(id, flight_id, price_id)
SELECT nextval('ticket_id') AS ticket_id, T.id AS flight_id, P.id AS price_id FROM T JOIN LATERAL (
    SELECT generate_series(1, capacity) AS num, (random()*10 + 0.5)::INT AS fare_code
) S ON true
JOIN Price P USING(planet_id, fare_code);
-- ================================
-- Случайные пассажиры
WITH Paxes AS(
  SELECT generate_series(1, (50*factor)::INT) AS id
), Races AS (
  select enumsortorder AS race_num, enumlabel::Race AS race_value
  from pg_catalog.pg_enum
  WHERE enumtypid = 'race'::regtype ORDER BY enumsortorder
), PaxRace AS (
  SELECT id, 'Pax' || id::TEXT AS name, (0.5 + random() * (SELECT MAX(race_num) FROM Races))::int
  AS race_num FROM Paxes
)
INSERT INTO Pax(id, name, race)
SELECT id, name, race_value FROM PaxRace JOIN Races USING(race_num);

-- ================================
-- Случайные бронирования
WITH Bookings AS (
  SELECT generate_series(1, (SELECT COUNT(*) FROM FlightTicket)/2) AS id
),
MaxValues AS (
  SELECT (SELECT MAX(id) FROM Pax) AS pax,
  (SELECT MAX(id) FROM FlightTicket) AS max_ticket_id,
  (SELECT MIN(id) FROM FlightTicket) AS min_ticket_id
)
INSERT INTO Booking(ref_num, pax_id, ticket_id)
SELECT substring(md5(id::TEXT)::TEXT for greatest(sqrt(factor)::INT, 10)), (0.5 + random() * pax)::INT, min_ticket_id+(random() * (max_ticket_id - min_ticket_id))::INT
FROM Bookings CROSS JOIN MaxValues;

END;
$$ LANGUAGE plpgsql;

SELECT GenerateData(0.01);
