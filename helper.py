from urlextract import URLExtract
extractor = URLExtract()
from wordcloud import WordCloud
from collections import Counter
import pandas as pd
import emoji

def fetch_stats(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    #fetch number of messages
    num_message = df.shape[0]

    #finding number of words and links
    words = []
    links = []
    for message in df['message']:
        links.extend(extractor.find_urls(message))
        words.extend(message.split())

    #finding number of media messages
    media_count = df['message'].str.contains('omitted').sum()

    return num_message,len(words),media_count,len(links)

def most_busy_users(df):
    x = df['user'].value_counts().head()
    df = round((df['user'].value_counts()/df.shape[0])*100,2).reset_index().rename(columns={'index':'name','user':'percent'})
    return x,df

def create_wordcloud(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # remove group notification
    # remove media ommited
    # remove stop words
    temp = df[df['user'] != 'group_notification']
    temp = temp[temp['message'].str.contains('omitted') == False]
    temp = temp[temp['message'].str.contains('image') == False]

    f = open('stop_hinglish.txt', 'r')
    stop_words = f.read()

    def remove_stop_words(message):
        y=[]
        for word in message.lower().split():
            if word not in stop_words:
                y.append(word)

        return " ".join(y)

    wc = WordCloud(width=500,height=500,min_font_size=10,background_color='white')
    temp['message'] = temp['message'].apply(remove_stop_words)
    df_wc = wc.generate(temp['message'].str.cat(sep=''))
    return df_wc

def most_common_words(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # remove group notification
    # remove media ommited
    # remove stop words
    temp = df[df['user'] != 'group_notification']
    temp = temp[temp['message'].str.contains('omitted') == False]
    temp = temp[temp['message'].str.contains('image') == False]

    f = open('stop_hinglish.txt', 'r')
    stop_words = f.read()

    words = []

    for message in temp['message']:
        for word in message.lower().split():
            if word not in stop_words and word != '\u200e':
                words.append(word)

    return pd.DataFrame(Counter(words).most_common(20))

def emoji_helper(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    emojis = []
    for message in df['message']:
        emojis.extend([c for c in message if c in emoji.UNICODE_EMOJI['en']])

    emoji_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))
    return emoji_df

def monthly_timeline(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()
    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i] + "-" + str(timeline['year'][i]))
    timeline['time'] = time

    return timeline

def daily_timeline(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    daily_timeline = df.groupby('only_date').count()['message'].reset_index()
    return daily_timeline

def week_activity_map(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['day_name'].value_counts()

def month_activity_map(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['month'].value_counts()

def activity_heat_map(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    activity_heatmap = df.pivot_table(index='day_name',columns='period',values='message',aggfunc='count').fillna(0)
    return activity_heatmap