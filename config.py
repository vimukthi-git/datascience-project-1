__author__ = 'vimukthi'

DATABASE_SERVER = 'localhost'
DATABASE_NAME = 'datascience_project'
DATABASE_USER = 'root'
DATABASE_PASSWORD = 'mit@12345'

SQL = {
    'SNP': 'select * from snp_usa',
    'NASDAQ': 'select * from nasdaq_usa',
    'USA_EVT': 'select * from political_events where country = "United States" and year >= 1971',
    'USA_PROCESSED': 'select * from usa_processed',
}
