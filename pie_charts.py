import cx_Oracle
import plotly.offline as py
import plotly.graph_objs as go

username = 'eugene1'
password = 'qwerty'
databaseName = 'localhost/xe'

connection = cx_Oracle.connect(username, password, databaseName)

cursor = connection.cursor()
cursor.execute("""
SELECT
    human.ident_code,
    TRIM(human.firstname || ' ' || human.surname),
    NVL(count(personal_auto.auto_number),0)
 FROM
    human left join personal_auto
    on (human.ident_code = personal_auto.ident_code_fk and personal_auto.REGISTRATION_END_DATE is null)
GROUP BY human.ident_code, TRIM(human.firstname || ' ' || human.surname)
""")

humans = []
auto_count = []

for row in cursor:
    humans += [row[1] + " " + str(row[0])]
    auto_count += [row[2]]

pie = go.Pie(labels=humans, values=auto_count)
py.plot([pie])

cursor.close()
connection.close()
