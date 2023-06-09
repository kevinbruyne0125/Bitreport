import json
import os
from collections import namedtuple

import pytest
import sqlalchemy
from influxdb import InfluxDBClient
from sqlalchemy.exc import OperationalError, ProgrammingError

import config
from app import models
from app.api.app_factory import create_app
from app.models.influx import insert_candles
from app.ta.indicators import INDICATORS

engine = sqlalchemy.create_engine(f"postgresql://postgres@{config.Test.POSTGRES_HOST}")
App = namedtuple("App", ["ctx", "client"])


def create_test_db():
    conn = engine.connect()
    conn.execute("commit")
    try:
        conn.execute("create database test")
    except ProgrammingError:
        pass
    conn.close()


def drop_test_db():
    conn = engine.connect()
    conn.execute("commit")
    try:
        conn.execute("drop database if exists test")
    except OperationalError:
        pass
    conn.close()


@pytest.fixture(scope="session")
def app(request):
    """Session-wide test application."""
    # influx_conn = database.connect_influx(config.Test.INFLUX)
    create_test_db()

    # Create app and add 500 error endpoint
    _app = create_app(config.Test)

    @_app.route("/test/bad/error")
    def error():
        raise KeyError

    client = _app.test_client()
    ctx = _app.app_context()

    # When testing API use client
    # When testing TA use ctx
    yield App(ctx, client)

    # Cleanup
    with ctx:
        models.db.engine.dispose()
    drop_test_db()


@pytest.fixture(scope="session")
def drop_influx():
    client = InfluxDBClient(**config.Test.INFLUX)
    client.drop_database(config.Test.INFLUX.get("database", "test"))


@pytest.fixture
def influx():
    client = InfluxDBClient(**config.Test.INFLUX)
    dbname = config.Test.INFLUX.get("database", "test")
    client.create_database(dbname)

    yield client

    client.drop_database(dbname)


def fill_database():
    rel_dir = os.path.dirname(__file__)
    pair = "BTCUSD"

    for tf in ["1h", "12h"]:
        measurement = pair + tf
        path = os.path.join(rel_dir, f"test_data/{measurement}.json")
        with open(path) as data_file:
            points = json.load(data_file)
            insert_candles(points, time_precision="ms")

        # Add fake pair
        points = points[:120]
        measurement = f"TEST{tf}"
        for x in points:
            x["measurement"] = measurement

        insert_candles(points, time_precision="ms")


@pytest.fixture()
def filled_influx(app):
    client = InfluxDBClient(**config.Test.INFLUX)
    dbname = config.Test.INFLUX.get("database", "test")
    client.create_database(dbname)

    # Add some test points
    with app.ctx:
        fill_database()

    yield client

    client.drop_database(dbname)


@pytest.fixture
def indicators_names():
    return list(INDICATORS.keys())


@pytest.fixture
def charting_names():
    # return ['wedge', 'levels', 'double_top', 'double_bottom']
    return []


@pytest.fixture
def required_indicators(
    indicators_names, charting_names
):  # pylint:disable=redefined-outer-name
    return indicators_names + charting_names
