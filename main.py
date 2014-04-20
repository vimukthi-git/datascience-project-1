#!/usr/bin/env python
import pandas as pd
import pandas.io.sql as psql
import MySQLdb as db
import optparse

def main():
  #p = optparse.OptionParser()
  #p.add_option('--person', '-p', default="world")
  #options, arguments = p.parse_args()
  #print 'Hello %s' % options.person 
  mysql_cn = db.connect(host='localhost', port=3306,user='root', passwd='mit@12345',db='datascience_project')
  df_mysql = psql.frame_query('select * from snp_usa;', con=mysql_cn)
  print df_mysql
 

if __name__ == '__main__':
  main()
