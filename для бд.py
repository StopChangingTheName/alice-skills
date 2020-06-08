import psycopg2

with open('рекордики.txt', 'r', encoding='utf-8') as f:
    data = f.readlines()
for line in data:
    line = line.split('\t')
    con = psycopg2.connect(user="kndwjclu",
                           password="WQZM309s2Rd4dUUbl1l3v_zicW2ghkYv",
                           host="dumbo.db.elephantsql.com",
                           port="5432",
                           database="kndwjclu")
    cur = con.cursor()
    cur.execute(f"INSERT INTO u VALUES (DEFAULT,'{line[1]}',{int(line[2])},{int(line[3])},{int(line[4])},"
                f"{int(line[5])},{int(line[6].strip('\n'))});")
    con.commit()
    con.close()