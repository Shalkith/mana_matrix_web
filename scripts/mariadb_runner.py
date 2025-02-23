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
        table = 'hb_decklists'
    if format == 'pedh':
        table = 'pedh_decklists'
    if format == 'cedh':
        table = 'cedh_decklists'
    if format == 'edh':
        table = 'edh_decklists'
    query = f'''
select hd.card_name, COALESCE(s1.image_url,s3.image_url),COALESCE(s2.image_url,s4.image_url),count(distinct deck_id) from {table} hd 
left JOIN mtg_datalake.scryfall_images s1 on SUBSTRING_INDEX(hd.card_name, '[and]', 1) = s1.card_name 
left JOIN mtg_datalake.scryfall_images s2 on SUBSTRING_INDEX(hd.card_name, '[and]', -1) = s2.card_name and s2.card_name not like s1.card_name
left JOIN mtg_datalake.scryfall_images s3 on SUBSTRING_INDEX(hd.card_name, ' // ', 1) = s3.card_name 
left JOIN mtg_datalake.scryfall_images s4 on SUBSTRING_INDEX(hd.card_name, ' // ', -1) = s4.card_name and s4.card_name not like s3.card_name
where hd.card_name not in (
'Plains','Island','Swamp','Mountain','Forest','Snow-Covered Plains','Snow-Covered Island','Snow-Covered Swamp','Snow-Covered Mountain','Snow-Covered Forest')
group by 1,2,3 order by 4 desc 
limit 200
'''
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
        table = 'hb_deck_details'
    if format == 'pedh':
        table = 'pedh_deck_details'
    if format == 'cedh':
        table = 'cedh_deck_details'
    if format == 'edh':
        table = 'edh_deck_details'
    con = connect()    
    query = f"""
    select commander_name,COALESCE(s1.image_url,s3.image_url),COALESCE(s2.image_url,s4.image_url),count(distinct deck_id) from {table}
left JOIN mtg_datalake.scryfall_images s1 on SUBSTRING_INDEX(commander_name, '[and]', 1) = s1.card_name 
left JOIN mtg_datalake.scryfall_images s2 on SUBSTRING_INDEX(commander_name, '[and]', -1) = s2.card_name and s2.card_name not like s1.card_name
left JOIN mtg_datalake.scryfall_images s3 on SUBSTRING_INDEX(commander_name, ' // ', 1) = s3.card_name 
left JOIN mtg_datalake.scryfall_images s4 on SUBSTRING_INDEX(commander_name, ' // ', -1) = s4.card_name and s4.card_name not like s3.card_name
    where commander_name is not null
    group by 1 ,2,3 order by 4 desc """

    query = sqlalchemy.text(query)
    result = con.execute(query)
    
    results = []
    for row in result:
        results.append(row)
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

        