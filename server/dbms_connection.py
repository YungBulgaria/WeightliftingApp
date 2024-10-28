import mysql.connector

# Connecting to databases

# MySQL
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="test_root",
    database="logbook"
)
query = "SET GLOBAL max_allowed_packet=104857600"
mydb.reconnect()
mycursor = mydb.cursor()
mycursor.execute(query)
mycursor.close()







# Functions

# Send MySQL keywords query
def get_mysql_keywords():
    mydb.reconnect()
    query = "CALL SelectALLKeywords()"
    mycursor = mydb.cursor()
    mycursor.execute(query)
    myresult = mycursor.fetchall()
    mycursor.close()
    data = {"name": [i[0] for i in myresult]}
    return data

# Send MySQL search query
def get_mysql_search(query):
    mydb.reconnect()
    input_value = query["input_val"]
    where_clause = f"WHERE name LIKE '%{input_value}%'"
    query = f"SELECT * FROM All_Keywords {where_clause} ORDER BY CHAR_LENGTH(name) ASC"
    mycursor = mydb.cursor()
    mycursor.execute(query)
    data = mycursor.fetchall()
    mycursor.close()
    return data


# Send MySQL query for faculty
def get_faculty(query):
    mydb.reconnect()
    input_value = query["input_val"]
    where_clause = (
        f"WHERE keyword.name LIKE '%{input_value}%' "
        f"AND publication.id = publication_keyword.publication_id "
        f"AND publication_keyword.keyword_id = keyword.id "
        f"AND faculty_publication.faculty_id = faculty.id "
        f"AND faculty_publication.publication_id = publication.id"
    )
    query = (
        f"SELECT faculty.name, faculty.photo_url, SUM(publication_keyword.score * publication.num_citations) AS KRC "
        f"FROM faculty, publication_keyword, publication, keyword, faculty_publication "
        f"{where_clause} "
        f"GROUP BY faculty.name, faculty.photo_url "
        f"ORDER BY KRC DESC LIMIT 1;"
    )
    mycursor = mydb.cursor()
    mycursor.execute(query)
    data = mycursor.fetchall()
    mycursor.close()
    return data

def get_highest_KRC(query, query2):
    mydb.reconnect()
    input_value = query["input_val"]
    name = query2['input_val']
    where_clause = (
        f"WHERE keyword.name LIKE '%{input_value}%' AND faculty.name LIKE '%{name}%' "
        f"AND publication.id = publication_keyword.publication_id "
        f"AND publication_keyword.keyword_id = keyword.id "
        f"AND faculty_publication.faculty_id = faculty.id "
        f"AND faculty_publication.publication_id = publication.id"
    )
    query = (
        f"SELECT SUM(publication_keyword.score * publication.num_citations) AS KRC "
        f"FROM faculty, publication_keyword, publication, keyword, faculty_publication "
        f"{where_clause} "
        f"GROUP BY faculty.name "
        f"ORDER BY KRC DESC LIMIT 1;"
    )
    mycursor = mydb.cursor()
    mycursor.execute(query)
    data = mycursor.fetchall()
    mycursor.close()
    return data

# Retrieve faculty (Parts 5 and 6)
def list_faculty():
    mydb.reconnect()
    query = "SELECT name FROM faculty"
    mycursor = mydb.cursor()
    mycursor.execute(query)
    data = mycursor.fetchall()
    mycursor.close()
    flattened_data = [item for sublist in data for item in sublist]
    return flattened_data

# Part 5
def list_faculty_details(query):
    mydb.reconnect()
    input_value = query["input_val"]
    where_clause = f"WHERE name LIKE '%{input_value}%'"
    query = f"SELECT position, email, phone, research_interest FROM faculty {where_clause}"
    mycursor = mydb.cursor()
    mycursor.execute(query)
    data = mycursor.fetchall()
    mycursor.close()
    return data

# Part 5
def update_faculty_details(faculty, position, email, phone, research_area):
    mydb.reconnect()
    mycursor = mydb.cursor()

    curr_details = get_faculty_details(faculty)
    position = position if position else curr_details[0]
    email = email if email else curr_details[1]
    phone = phone if phone else curr_details[2]
    research_area = research_area if research_area else curr_details[3]

    # MySQL update
    mycursor.execute(
        f"UPDATE faculty SET position = '{position}', email = '{email}', phone = '{phone}', research_interest = '{research_area}' WHERE name LIKE '%{faculty}%'"
    )
    mydb.commit()
    mycursor.close()


def get_faculty_details(faculty_name):
    mydb.reconnect()
    cursor = mydb.cursor()
    cursor.execute(f"SELECT position, email, phone, research_interest FROM faculty WHERE name LIKE '%{faculty_name}%'")
    result = cursor.fetchone()
    cursor.close()
    return result if result else ['', '', '', '']

def list_faculty_keywords(query):
    input_value = query["input_val"]
    cypher_query = f"MATCH (f:FACULTY)-[:INTERESTED_IN]->(k:KEYWORD) WHERE f.name CONTAINS '{input_value}' RETURN k.name"
    with driver.session(database="academicworld") as session:
        result = session.run(cypher_query, input_value=input_value)
        data = [record["k.name"] for record in result]
    return data

def update_faculty_keywordsA(value, keyword):
    # MySQL Update
    mydb.reconnect()
    mycursor = mydb.cursor()
    try:
        mycursor.execute(f"SELECT id FROM faculty WHERE name LIKE '{value}'")
        faculty_id = mycursor.fetchone()[0]
        mycursor.fetchall()
        mycursor.execute(f"SELECT id FROM keyword WHERE name = '{keyword}'")
        keyword_result = mycursor.fetchone()
        mycursor.fetchall()
        if keyword_result:
            keyword_id = keyword_result[0]
        else:
            mycursor.execute(f"SELECT MAX(id) FROM keyword")
            keyword_id = mycursor.fetchone()[0] + 1
            mycursor.fetchall()
            mycursor.execute(f"INSERT INTO keyword (name, id) VALUES ('{keyword}', '{keyword_id}')")
            mydb.commit()

        mycursor.execute(f"INSERT INTO faculty_keyword (faculty_id, keyword_id) VALUES ('{faculty_id}', '{keyword_id}')")
        mydb.commit()
    except Exception as e:
        print(f"MySQL Error1: {e}")
    finally:
        mycursor.close()