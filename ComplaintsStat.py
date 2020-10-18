import psycopg2

try:
    connection = psycopg2.connect(user="admin",
                                  password="password",
                                  host="127.0.0.1",
                                  port="5433",
                                  database="complaints")

    cursor = connection.cursor()

except Exception as error:
    print("Connection failed")


def issuecounter(cursor, date_from, date_to):
    query = """
        select product_name,
        count(issue) issue,
        count(timely_response) filter (where timely_response is true),
        count(consumer_disputed) filter (where consumer_disputed is true)
        from complaints.user_complaints
        where date_received >= %s and date_received < %s
        group by product_name
        order by issues desc
    ;"""
    cursor.execute(query, (date_from, date_to))
    header = "product_name, issues, timely_response, consumer_disputed"
    print(header)
    for row in cursor:
        print(row)



 def bad_company(cursor, company):
        query = """
            select * from complaints.user_complaints
            where state_name = (select state_name,
                    count(issue) as isscount
            from complaints.user_complaints
            where company = %s
            group by state_name
            order by isscount desc
            limit 1)
            and company = %s
            limit 3
        ;"""

        cursor.execute(query, (company, company))
        for row in cursor:
            print(row)



if (connection):
    cursor.close()
    connection.close()
