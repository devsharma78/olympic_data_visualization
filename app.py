import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.figure_factory as ff
import preprocessor, helper
import mysql.connector
import matplotlib.pyplot as plt

helper.add_bg_from_local('olympic.jpg')

# Connect to the MySQL server
mydb = mysql.connector.connect(host='localhost', database='olympic_data_visualization', user='root', password='mysql')
# Create a cursor object to interact with the database
mycursor = mydb.cursor()
# Run a SELECT query on the table
mycursor.execute("SELECT * FROM noc_regions")

# Fetch all the rows of the result set
result_region_df = mycursor.fetchall()
region_df = pd.DataFrame(result_region_df)
region_df = region_df.rename(columns={0: 'NOC', 1: 'region', 2: 'notes'})

# Create a cursor object to interact with the database
cursor = mydb.cursor()
# Run a SELECT query on the table
cursor.execute("SELECT * FROM athlete_events")

# Fetch all the rows of the result set
result_df = cursor.fetchall()
df = pd.DataFrame(result_df)
df = df.rename(columns={0 : 'ID', 1 : 'Name', 2 : 'Sex', 3 : 'Age', 4 : 'Height', 5 : 'Weight', 6 : 'Team', 7 : 'NOC', 8 : 'Games', 9 : 'Year', 10 : 'Season', 11 : 'City', 12 : 'Sport', 13 : 'Event', 14 : 'Medal'})
df = preprocessor.preprocess(df, region_df)
st.sidebar.title("Olympics Analysis")

user_menu = st.sidebar.radio(
    'Select an option', 
    ('Medal Leaderboard', 'Overall Analaysis', 'Country-wise analysis', 'Athlete-wise analysis')
)


if user_menu == 'Medal Leaderboard' :
    st.sidebar.header("Medal Leaderboard")
    years, countries = helper.country_year_list(df)
    selected_year = st.sidebar.selectbox("Select year", years)
    selected_country = st.sidebar.selectbox("Select Country", countries)

    if (selected_country == 'Overall' and selected_year == 'Overall') :
        st.title("Overall Leaderboard")

    if (selected_country == 'Overall' and selected_year != 'Overall') :
        st.title("Medal Leaderboard in "+ str(selected_year) + " Olympics" )

    if (selected_country != 'Overall' and selected_year == 'Overall') :
        st.title(selected_country + " Overall Performance")

    if (selected_country != 'Overall' and selected_year != 'Overall') :
        st.title(selected_country + " performance in " + str(selected_year) + " Olympics")
    
    medal_Leaderboard =  helper.fetch_medal_Leaderboard(df, selected_year,selected_country)
    helper.main()
    st.table(medal_Leaderboard)

if user_menu == 'Overall Analaysis' :
    editions = df['Year'].unique().shape[0] - 1
    cities = df['City'].unique().shape[0]
    events = df['Event'].unique().shape[0]
    sports = df['Sport'].unique().shape[0]
    athletes = df['Name'].unique().shape[0]
    nations = df['region'].unique().shape[0]

    st.title("Top Statistics")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.header("Editions")
        st.title(editions)
    with col2:
        st.header("Hosts")
        st.title(cities)
    with col3:
        st.header("Sports")
        st.title(sports)

    col1,col2,col3 = st.columns(3)
    with col1:
        st.header("Events")
        st.title(events)
    with col2:
        st.header("Nations")
        st.title(nations)
    with col3:
        st.header("Athletes")
        st.title(athletes)

    nations_over_time = helper.data_over_time(df,'region')
    st.title("Participating nations over the years")
    # print("nations",nations_over_time)
    fig = px.line(nations_over_time, x = "Edition", y = "No of region")
    st.plotly_chart(fig)

    events_over_time = helper.data_over_time(df,'Event')
    st.title("Events over the years")
    fig = px.line(events_over_time, x = "Edition", y = "No of Event")
    st.plotly_chart(fig)

    athletes_over_time = helper.no_of_athletes_over_time(df,'Name')
    st.title("Athletes over the years")
    fig = px.line(athletes_over_time, x = "Edition", y = "No of athletes")
    st.plotly_chart(fig)

    st.title("No. of events over time in every sport")
    fig, ax = plt.subplots(figsize = (20,20))
    x = df.drop_duplicates(['Year', 'Sport', 'Event'])
    ax = sns.heatmap(x.pivot_table(index = 'Sport', columns='Year', values = 'Event', aggfunc='count').fillna(0).astype(int),
    annot=True)
    st.pyplot(fig)

    st.title("Most sucessful athletes")
    sport_list = df['Sport'].unique().tolist()
    sport_list.sort()
    sport_list.insert(0,'Overall')
    selected_sport = st.selectbox('Select a sport', sport_list)
    x = helper.most_successful(df,selected_sport)
    helper.main()
    st.table(x)


if user_menu == 'Country-wise analysis' :
    st.sidebar.title('Country wise Analysis')
    years, countries = helper.country_year_list(df)
    selected_country = st.sidebar.selectbox("Select Country", countries)
    final_df = helper.yearwise_medal_Leaderboard(df,selected_country)

    st.title(selected_country + " medal Leaderboard over the years")
    fig = px.line(final_df, x = "Year", y = "No of medals")
    st.plotly_chart(fig)

    st.title(selected_country + " excels in the following sports")
    pt = helper.country_event_heatmap(df, selected_country)
    sns.set(font_scale = 1.6)
    fig,ax = plt.subplots(figsize = (25,20))
    ax = sns.heatmap(pt, annot=True)
    st.pyplot(fig)

    st.title("Top 10 athletes of " + selected_country)
    x = helper.most_successful_countrywise(df, selected_country)
    helper.main()
    st.table(x)


if user_menu == 'Athlete-wise analysis' :
    athlete_df = df.drop_duplicates(subset = ['Name', 'region'])
    x1 = athlete_df['Age'].dropna()
    x2 = athlete_df[athlete_df['Medal'] == 'Gold']['Age'].dropna()
    x3 = athlete_df[athlete_df['Medal'] == 'Silver']['Age'].dropna()
    x4 = athlete_df[athlete_df['Medal'] == 'Bronze']['Age'].dropna()

    fig = ff.create_distplot([x1,x2,x3,x4], ['Overall Age', 'Gold medalist', 'Silver medalist', 'Bronze medalist'],
                         show_hist = False, show_rug=False)

    st.title("Distribution of Age")
    fig.update_layout(autosize = False, width = 800, height = 500)
    st.plotly_chart(fig)

    st.title('Number of male and female participants over time')
    gender_participation = helper.male_v_female_overtime(df)
    fig = px.line(gender_participation, x = 'Year', y = 'No of participants', color = 'Sex', markers=True)
    st.plotly_chart(fig)
            

    st.title("Height and weight distribution of athletes")
    sport_list = df['Sport'].unique().tolist()
    sport_list.sort()
    sport_list.insert(0,'Overall')
    selected_sport = st.selectbox('Select a sport', sport_list)
    temp_df = helper.weight_and_height(df,selected_sport)
    fig,ax = plt.subplots(figsize=(10,10))
    ax = sns.scatterplot(x = 'Weight', y= 'Height',data=temp_df, hue='Sex')
    st.pyplot(fig)
