import sqlalchemy
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
load_dotenv()

def connect():
    '''
    create a .env file in the root directory of the project and add the following lines:
    DBUSER=your_database_username
    DBPASSWORD=your_database_password
    DBHOST=your_database_host
    DBPORT=your_database_port
    DB=your_db_name
    '''

    user = os.getenv('DBUSER')
    password = os.getenv('DBPASSWORD')
    host = os.getenv('DBHOST')
    port = os.getenv('DBPORT')
    db = os.getenv('DB')

    # connect to the # mariadb
    engine = create_engine('mysql+mysqldb://' + user + ':' + password + '@' + host + ':' + port + '/' + db)
    # run a test query
    #result = engine.execute("select * from health_log")
    connection = engine.connect()
    return connection 

def get_topcards(format):
    format = format.lower()
    if format == 'brawl':
        table = 'hb_top_cards'
    if format == 'pedh':
        table = 'pedh_top_cards'
    if format == 'cedh':
        table = 'cedh_top_cards'
    if format == 'edh':
        table = 'edh_top_cards'
    query = f'''select * from {table}'''
    con = connect()   
    query = sqlalchemy.text(query)
    result = con.execute(query)
    results = []
    for row in result:
        results.append(row)
    close_connection(con)
    return results



def get_commanders(format):
    format = format.lower()
    if format == 'brawl':
        table = 'hb_commanders'
    if format == 'pedh':
        table = 'pedh_commanders'
    if format == 'cedh':
        table = 'cedh_commanders'
    if format == 'edh':
        table = 'edh_commanders'
    con = connect()    
    query = f"""select * from {table}"""

    query = sqlalchemy.text(query)
    result = con.execute(query)
    
    results = []
    for row in result:
        results.append(row)
    close_connection(con)
    return results 

def get_card_names():
    con = connect()
    query = 'select distinct card_name,oracle_id from mtg_datalake.scryfall_images order by 1 asc'
    query = sqlalchemy.text(query)
    result = con.execute(query)
    
    results = []
    for row in result:
        results.append(row[0])
    close_connection(con)
    return results 

def get_card_id(name):
    con = connect()
    name = name.lower()
    query = f"select distinct oracle_id from mtg_datalake.scryfall_images where lower(card_name) = '{name}' order by 1 asc"
    query = sqlalchemy.text(query)
    result = con.execute(query)
    
    results = []
    for row in result:
        results.append(row[0])
    close_connection(con)
    return results 

def close_connection(con):
    # explicitly close the connection
    con.close()

    




if __name__ == '__main__':
    #setup()
    con = connect()
    print(get_commanders('brawl'))
    close_connection(con)
    print('done')

        