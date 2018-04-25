import cx_Oracle
import plotly.offline as py
import plotly.graph_objs as go

username = 'smithj'
password = 'qwerty'
databaseName = 'localhost/xe'

connection = cx_Oracle.connect(username, password, databaseName)

cursor = connection.cursor()

cursor.execute("""
SELECT
    registration_start_date,
    registration_end_date
 FROM
    registration_address
where ident_code_fk = 2
""")
dict_count = {}


for row in cursor:
    if row[0] not in dict_count:
        dict_count[row[0]] = 1
    else:
        dict_count[row[0]] += 1

    if (row[1] not in dict_count) and (row[1] is not None):
        dict_count[row[1]] = -1
    elif (row[1] is not None):
        dict_count[row[1]] -= 1
address_count=[0]
i=0
for keys in sorted(dict_count.keys()):
    address_count.append(address_count[i]+dict_count[keys])
    i+=1

dates = [str(key)[:10] for key in sorted(dict_count.keys())]

dates_count = go.Scatter(
    x=dates,
    y=address_count[1:],
    mode='lines+markers'
)
data = [dates_count]
py.plot(data)
