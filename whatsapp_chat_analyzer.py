
import streamlit as st
import preprocessor
import helper
import matplotlib.pyplot as plt
import seaborn as sns
from pymongo import MongoClient
from dotenv import load_dotenv   #for python-dotenv method
load_dotenv()                    #for python-dotenv method
import os
username = os.environ.get('user_name')
password = os.environ.get('password')

connection_url = "mongodb+srv://"+username+":"+password+"@cluster0.ubfo2jm.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(connection_url)
db = client['Whatsapp_Chat']
collection = db['chat_collection']

st.sidebar.title("Whatsapp Chat Analyzer")

uploaded_file = st.sidebar.file_uploader("Choose a file")
if uploaded_file is not None:
    # To read file as bytes:
    bytes_data = uploaded_file.getvalue()
    file_name = uploaded_file.name
    data = bytes_data.decode('utf-8')
    chat = {
        'Name': file_name,
        'Chat': data
    }
    if collection.find_one({'Chat':data}):
        pass
    else:
        collection.insert_one(chat).inserted_id

    df = preprocessor.preprocess(data)
    #st.dataframe(df)

    #fetch unique users
    user_list = df['user'].unique().tolist()
    try:
        user_list.remove('group_notification')
    except:
        pass
    user_list.sort()
    user_list.insert(0,"Overall")
    selected_user = st.sidebar.selectbox("Show analysis wrt",user_list)

    if st.sidebar.button("Show Analysis"):
        #stats area
        st.title("Top Statistics")
        num_messages,words,media_count,links = helper.fetch_stats(selected_user,df)
        col1,col2,col3,col4 = st.columns(4)

        with col1:
            st.header("Total Messages")
            st.title(num_messages)
        with col2:
            st.header("Total Words")
            st.title(words)
        with col3:
            st.header("Media Shared")
            st.title(media_count)
        with col4:
            st.header("Links Shared")
            st.title(links)

        # monthly timeline
        st.title("Monthly Timeline")
        monthly_timeline = helper.monthly_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(monthly_timeline['time'], monthly_timeline['message'], color='green')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        #daily timeline
        st.title("Daily Timeline")
        daily_timeline = helper.daily_timeline(selected_user,df)
        fig,ax = plt.subplots()
        ax.plot(daily_timeline['only_date'],daily_timeline['message'],color='black')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        #activity map
        st.title("Activity Map")
        col1,col2 = st.columns(2)

        with col1:
            busy_day = helper.week_activity_map(selected_user, df)
            st.header("Most Busy Day")
            fig,ax = plt.subplots()
            ax.bar(busy_day.index,busy_day.values)
            plt.xticks(rotation='vertical')
            st.pyplot(fig)
        with col2:
            busy_month = helper.month_activity_map(selected_user, df)
            st.header("Most Busy Month")
            fig, ax = plt.subplots()
            ax.bar(busy_month.index, busy_month.values,color='orange')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        #activity heat map
        st.title("Activity Heatmap")
        user_heatmap = helper.activity_heat_map(selected_user,df)
        fig,ax = plt.subplots()
        ax = sns.heatmap(user_heatmap)
        st.pyplot(fig)

        #finding the busiest users in the group(Group level)
        if selected_user=='Overall':
            x,new_df= helper.most_busy_users(df)
            fig,ax = plt.subplots()

            st.title('Most Busy Users')
            col1,col2 = st.columns(2)

            with col1:
                ax.bar(x.index,x.values,color='red')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)
            with col2:
                st.dataframe(new_df)

        #word cloud
        st.title("Wordcloud")
        df_wc = helper.create_wordcloud(selected_user,df)
        fig,ax = plt.subplots()
        ax.imshow(df_wc)
        st.pyplot(fig)

        #most common words
        st.title("Most Common Words")
        most_common_df = helper.most_common_words(selected_user,df)
        fig,ax = plt.subplots()
        ax.barh(most_common_df[0],most_common_df[1])
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        #emoji analysis
        emoji_df = helper.emoji_helper(selected_user,df)
        st.title("Emoji Analysis")

        col1,col2 = st.columns(2)
        with col1:
            st.dataframe(emoji_df)
        with col2:
            fig,ax = plt.subplots()
            ax.pie(emoji_df[1].head(),labels=emoji_df[0].head(),autopct = '%0.2f')
            st.pyplot(fig)

