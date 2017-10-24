import qbapi.qbapi as qb
import pypg.pg_pandas as pg
import pandas as pd

from Sql import Sql
if __name__ == '__main__':
    print "hello world"
    e = pg.get_engine_from_csv('db.csv')
    df = pg.get_sql("select * from billy.gmuf")
    print df
