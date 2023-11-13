from pyspark.sql import SparkSession
import pytest


@pytest.fixture(scope="session")
def spark(request):
    """Spark session as a fixture.

    See https://engblog.nextdoor.com/unit-testing-apache-spark-with-py-test-3b8970dc013b.
    """
    sess = (
        SparkSession.builder.master("local")
        .appName("pytest-pyspark-local-testing")
        .getOrCreate()
    )
    request.addfinalizer(sess.stop)
    return sess
