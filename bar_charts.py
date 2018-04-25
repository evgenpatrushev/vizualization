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
    count(registration_address.apartment_number)
 FROM
    human left join registration_address
    on (human.ident_code = registration_address.ident_code_fk and registration_address.REGISTRATION_END_DATE is null)
GROUP BY human.ident_code, TRIM(human.firstname || ' ' || human.surname) """)

humans = []
reg_address_count = []

for row in cursor:
    humans += [str(row[0]) + "\n"+ row[1]]
    reg_address_count += [row[2]]
data = [go.Bar(
    x=humans,
    y=reg_address_count
)]


layout = go.Layout(
    title='Humans and count of their houses',
    xaxis=dict(
        title='Humans',
        titlefont=dict(
            family='Courier New, monospace',
            size=18,
            color='#7f7f7f'
        )
    ),
    yaxis=dict(
        title='Count houses',
        rangemode='nonnegative',
        autorange=True,
        titlefont=dict(
            family='Courier New, monospace',
            size=18,
            color='#7f7f7f'
        )
    )
)
fig = go.Figure(data=data, layout=layout)
py.plot(fig)

cursor.close()
connection.close()
