#!/usr/bin/env python
from time import strftime
from pandas.core.frame import DataFrame

__author__ = 'vimukthi'
import pandas.io.sql as psql
import numpy as np
import MySQLdb as db
import matplotlib.pyplot as plt
from datetime import datetime, timedelta, date
import optparse
import config

mysql_cn = db.connect(host=config.DATABASE_SERVER, user=config.DATABASE_USER,
                      passwd=config.DATABASE_PASSWORD,db=config.DATABASE_NAME)

def main():
    global snp
    global nasdaq
    global usa_events
    global usa_processed
    with mysql_cn:
        snp = psql.frame_query(config.SQL.get('SNP'), con=mysql_cn)
        nasdaq = psql.frame_query(config.SQL.get('NASDAQ'), con=mysql_cn)
        usa_events = psql.frame_query(config.SQL.get('USA_EVT'), con=mysql_cn)
        usa_processed = psql.frame_query(config.SQL.get('USA_PROCESSED'), con=mysql_cn)
        #fill_trading_stats_in_db()
        #fill_event_severity()
        show_stocks_correlation()
        calc_correlation()
        #cleanup()

def show_stocks_correlation():
    plt.gca().set_color_cycle([ 'red', 'yellow', 'green', 'blue'])
    plt.plot(usa_processed.date, usa_processed.nasdaq_adj_close_rate)
    plt.plot(usa_processed.date, usa_processed.snp_adj_close_rate)
    plt.legend(['NASDAQ adjusted closing price', 'S&P500 adjusted closing price'], loc='upper left')
    plt.show()
    print usa_processed['snp_adj_close_rate'].corr(usa_processed['nasdaq_adj_close_rate'], method='spearman')

def calc_correlation():
    fig, plot1 = plt.subplots()
    plot1.plot(usa_processed.date, usa_processed.event_severity)
    plot1.set_ylabel('Event severity')
    plot2 = plot1.twinx()
    plot2.plot(usa_processed.date, usa_processed.nasdaq_adj_close_rate)
    plot2.plot(usa_processed.date, usa_processed.snp_adj_close_rate)
    plot2.set_ylabel('Indexes')
    plt.show()
    print usa_processed.corr()

def fill_trading_stats_in_db():
    cur = mysql_cn.cursor()
    snp_prev_value = 0
    nasdaq_prev_value = 0
    snp_no_value = 0
    nasdaq_no_value = 0
    for single_date in daterange(date(1971, 2, 5), date(2005, 12, 20)):
        snp_value = snp_prev_value
        nasdaq_value = nasdaq_prev_value

        try:
            snp_value = snp[snp['date'] == single_date]['adj_close'][:1].values[0]
            snp_no_value = 0
        except IndexError:
            snp_no_value = 1

        try:
            nasdaq_value = nasdaq[nasdaq['date'] == single_date]['adj_close'][:1].values[0]
            nasdaq_no_value = 0
        except IndexError:
            nasdaq_no_value = 1
        #print "snp - " , snp_value, "nasdaq - ", nasdaq_value
        cur.execute("INSERT INTO usa_processed(year, month, day, snp_adj_close_rate, nasdaq_adj_close_rate, date) VALUES(%s, %s, %s, %s, %s, %s)",
                    (single_date.year, single_date.month, single_date.day,
                     (snp_value - snp_prev_value), (nasdaq_value - nasdaq_prev_value), single_date))

        if snp_no_value == 0:
            snp_prev_value = snp_value
        if nasdaq_no_value == 0:
            nasdaq_prev_value = nasdaq_value
        #print "date",  single_date.year, single_date.month, single_date.day
    cur.close()

# Assume : event_severity = number killed * 2 + number injured
def fill_event_severity():
    severities = dict()
    usa_events['severity'] = usa_events['n_injurd'].astype(int) + 2 * usa_events['n_killed_a'].astype(int)
    for index, event in usa_events.iterrows():
        try:
            evt_date = date(int(event['year']), int(event['month']), int(event['day']))
            for i in range(0, int(event['day_span'])):
                nw_date = evt_date + timedelta(i)
                n_severity = int(event['severity'])
                if(severities.has_key(nw_date)):
                    n_severity = severities.get(nw_date) + int(event['severity'])
                severities[nw_date] = n_severity
                #print nw_date, severities[nw_date]
        except ValueError:
            pass
    cur = mysql_cn.cursor()
    for day in severities:
        cur.execute("UPDATE usa_processed SET event_severity = %s where date=%s",
                    (severities[day], day))
    cur.close()

def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)

def cleanup():
    mysql_cn.close()


if __name__ == '__main__':
    main()