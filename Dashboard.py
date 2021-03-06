import cx_Oracle
import plotly.plotly as py
import plotly.graph_objs as go
import re
import plotly.dashboard_objs as dashboard


username = 'eugene1'
password = 'qwerty'
databaseName = 'localhost/xe'


def fileId_from_url(url):
    """Return fileId from a url."""
    raw_fileId = re.findall(r'~[\w]+/[0-9]+$', url)[0][1:]
    return raw_fileId.replace('/', ':')


connection = cx_Oracle.connect(username, password, databaseName)

cursor = connection.cursor()

""" create plot 1   """

cursor.execute("""
SELECT
    human.ident_code,
    TRIM(human.firstname || ' ' || human.surname),
    count(registration_address.apartment_number)
 FROM
    human left join registration_address
    on (human.ident_code = registration_address.ident_code_fk and registration_address.REGISTRATION_END_DATE is null)
GROUP BY human.ident_code, TRIM(human.firstname || ' ' || human.surname)
order by 1
""")

humans = []
reg_address_count = []

for row in cursor:
    humans += [str(row[0]) + "<br>"+ row[1]]
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
registration_address_count = py.plot(fig, filename = "registration address count")


""" create plot 2   """
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
auto_count = py.plot([pie], filename="auto count")


""" create plot 3   Вивести динаміку покупок по датах"""
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

count_dates = go.Scatter(
    x=dates,
    y=address_count[1:],
    mode='lines+markers'
)
data = [count_dates]
count_reg_by_time = py.plot(data, filename = "count reg by time")

"""--------CREATE DASHBOARD------------------ """

my_dboard = dashboard.Dashboard()

registration_address_count_id = fileId_from_url(registration_address_count)
auto_count_id = fileId_from_url(auto_count)
count_reg_by_time_id = fileId_from_url(count_reg_by_time)


box_1 = {
    'type': 'box',
    'boxType': 'plot',
    'fileId': registration_address_count_id,
    'title': 'Humans and count houses'
}

box_2 = {
    'type': 'box',
    'boxType': 'plot',
    'fileId': auto_count_id,
    'title': 'Humans and count cars'
}

box_3 = {
    'type': 'box',
    'boxType': 'plot',
    'fileId': count_reg_by_time_id,
    'title': 'Human and count houses by date (name:Den Semenov; ident_code:2)'
}

my_dboard.insert(box_1)
my_dboard.insert(box_2, 'below', 1)
my_dboard.insert(box_3, 'left', 2)

py.dashboard_ops.upload(my_dboard, 'My First Dashboard with Python')
