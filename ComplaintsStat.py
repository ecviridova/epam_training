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
        select  product_name, issue,
        count(timely_response) filter (where timely_response_bool is true) trc,
        count(consumer_disputed) filter (where consumer_disputed_bool is true) cdc
        from user_complaints
        where date_received >= %s and date_received <= %s
        group by product_name, issue
        order by product_name, issue, count(issue) desc
    ;"""
    cursor.execute(query, (date_from, date_to))
    header = "product_name, issues, timely_response, consumer_disputed"
    print(header)
    for row in cursor:
        print(row)



 def bad_company(cursor, company):
        query = """
            select * from user_complaints
            where state_name = (select state_name
            from user_complaints
            where company = %s
            group by state_name
            order by count(issue) desc
            limit 1)
            and company = %s
            limit 3
        ;"""

        cursor.execute(query, (company, company))
        for row in cursor:
            print(row)
            
            
            
def bad_company2(cursor, company):
    query = """
    with t1 as (
	select
		company,
		state_name,
		count(issue) ci
	from 
        user_complaints
	where 
        company = %s
	group by
        company, state_name
	order by
        ci desc
	limit 1)
    select 
	    t1.company,
	    t1.state_name,
	    uc.product_name,
	    uc.sub_product,
	    uc.issue
    from 
        user_complaints uc, t1
    where 
        uc.company = t1.company
	    and uc.state_name = t1.state_name
    group by
        t1.company, t1.state_name, uc.product_name, uc.sub_product, uc.issue
    ;"""
    cursor.execute(query, company)
        for row in cursor:
            print(row)



if (connection):
    cursor.close()
    connection.close()
