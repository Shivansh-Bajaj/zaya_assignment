import redis
from cabbookingapp.settings import GEO_RADIUS


class FindDriver:
    r = None

    def __init__(self):
        try:
            self.r = redis.StrictRedis(host='redis-14057.c14.us-east-1-3.ec2.cloud.redislabs.com', port=14057, password="MULpeyURGoskdhHbIE7EqJAAtyYqss9E", db=0)

        except Exception as e:
            raise e

    def add_geo(self, city, long, lat, driverid):
        try:
            value = (long, lat, driverid)
            return self.r.geoadd(city, *value)
        except Exception as e:
            raise e

    def del_geo(self, city, driver):
        self.r.zrem(city, driver)

    def find_nearest(self, city, long, lat):
        try:
            return self.r.georadius(city, long, lat, GEO_RADIUS, unit='km',
                                    withdist=True, withcoord=True, withhash=True, sort='ASC')
        except Exception as e:
            raise e

    def get_driver_seats(self, driver):
        return self.r.hget('pool', driver)

    def del_driver_from_pool(self, driver):
        return self.r.hdel('pool', driver)

    def set_driver_seats(self, driver, seats):
        return self.r.hset('pool', driver, seats)

    def match(self, city, driver):
        return self.r.zscan(city, match=driver)

    def find_distance(self, city, place1, place2):
        return self.r.geodist(city, place1, place2, unit='km')