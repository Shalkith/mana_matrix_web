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

def get_card_details(card_id,format):
    format = format.lower()
    if format == 'brawl':
        table = 'hb'
    if format == 'pedh':
        table = 'pedh'
    if format == 'cedh':
        table = 'cedh'
    if format == 'edh':
        table = 'edh'

    con = connect()
    query = f"select distinct card_name from mtg_datalake.scryfall_images where oracle_id = '{card_id}' order by 1 asc"
    query = sqlalchemy.text(query)
    result = con.execute(query)
    results = []
    for row in result:
        results.append(row[0])
    card_name = results[0]
    card_name = card_name.replace("'","''")
    print(card_name)
    query = f"""
    #decks card is used in
    SELECT DISTINCT 
        d.commander_name,
        d.deck_name,
        d.deck_id,
        d.colors,
        d.publicurl,
        d.viewcount
    FROM mtg_datalake_processed.{table}_deck_details d
    JOIN mtg_datalake_processed.{table}_decklists l 
        ON d.deck_id = l.deck_id
    WHERE LOWER(l.card_name) LIKE LOWER('{card_name}') and LOWER(d.commander_name) not LIKE LOWER('{card_name}') order by d.viewcount+0 desc limit 10"""
    query = sqlalchemy.text(query)
    print(query)
    result = con.execute(query)
    results = []
    for row in result:
        results.append(row)
    used_in_decks = results

    query = f"""
    #decks where card is commander
    SELECT DISTINCT 
        d.commander_name,
        d.deck_name,
        d.deck_id,
        d.colors,
        d.publicurl,
        d.viewcount 
    FROM mtg_datalake_processed.{table}_deck_details d
    WHERE LOWER(d.commander_name) LIKE LOWER('{card_name}') order by d.viewcount+0 desc limit 10 """
    query = sqlalchemy.text(query)
    result = con.execute(query)
    results = []
    for row in result:
        results.append(row)
    this_card_decks = results


    query = f"""
    # commanders that use this card
    SELECT  
        d.commander_name,
        count(distinct d.deck_id) decks ,
        si.image_url ,
        si.oracle_id 
    FROM mtg_datalake_processed.{table}_deck_details d
    JOIN mtg_datalake_processed.{table}_decklists l 
        ON d.deck_id = l.deck_id
    left join mtg_datalake.scryfall_images si on si.card_name = d.commander_name 
    WHERE LOWER(l.card_name) LIKE LOWER('{card_name}')   and LOWER(d.commander_name) not LIKE LOWER('{card_name}')
    group by 1,3,4 order by 2 desc limit 10"""
    query = sqlalchemy.text(query)
    result = con.execute(query)
    results = []
    for row in result:
        results.append(row)
    top_commanders_for_this = results


    query = f"""
    # avg deck for this commander
    select * from {table}_average_decks had
    left join mtg_datalake.scryfall_images sp on sp.card_name  = had.card_name 
    where commander = '{card_name}'"""
    query = sqlalchemy.text(query)
    result = con.execute(query)
    results = []
    for row in result:
        results.append(row)
    avg_deck = results


    query = f"""
    #top cards for this commander 
    select hbm.card_name , 
    si.image_url ,si.type_line ,
    sum(quantity) quantity from {table}_board_mainboard hbm 
    left join mtg_datalake.scryfall_images si on si.card_name = hbm.card_name 
    where hbm.deck_id in (
    select deck_id from {table}_board_commanders hbc where card_name = '{card_name}' )
    and type_line not like '%Basic%Land%'
    group by 1,2,3 order by 4 desc
    limit 10"""
    query = sqlalchemy.text(query)
    result = con.execute(query)
    results = []
    for row in result:
        results.append(row)
    top_cards = results
    close_connection(con)
    card_name = card_name.replace("''","'")

    return used_in_decks,this_card_decks,top_commanders_for_this,avg_deck,top_cards,card_name


def close_connection(con):
    # explicitly close the connection
    con.close()

    




if __name__ == '__main__':
    #setup()
    con = connect()
    print(get_commanders('brawl'))
    close_connection(con)
    print('done')

        