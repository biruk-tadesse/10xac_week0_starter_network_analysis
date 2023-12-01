import streamlit as st
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from gensim import models


# Load data and models
combined_df = pd.read_csv('./combined_df.csv') 
mlflow_model_path = './model/lda_model' 

# Set page configuration
st.set_page_config(layout="wide")

# Functions
def get_top_users(data, top_n=10):
    return data['sender_name'].value_counts()[:top_n]

# Sidebar
st.sidebar.title("Dashboard Menu")
selected_chart = st.sidebar.selectbox("Select Chart", ["Top Users", "Message Distribution", "Word Cloud",
                                                       "User Reply Counts", "Top Message Senders",
                                                       "Average Reply Count per User", "Average Reply Users Count per User",
                                                       "Average Word Count per Message", "WordCloud for Each Channel",
                                                       "User Reactions",  "Message Classification Distribution",
                                                       "Topic Modeling Results","Sentiment Analysis"])

# Main content
st.title("Slack Analytics Dashboard")

# Display selected chart
if selected_chart == "Top Users":
    st.header("Top Users")
    top_users = get_top_users(combined_df)
    st.bar_chart(top_users)

elif selected_chart == "Message Distribution":
    st.header("Message Distribution Across Hours")
    plt.figure(figsize=(15, 7))
    sns.countplot(x='time_sent', data=combined_df)
    st.pyplot()

elif selected_chart == "Word Cloud":
    st.header("Word Cloud")
    def generate_wordcloud(text):
        wordcloud = WordCloud(width=500, height=300, background_color='white').generate(text)
        return wordcloud.to_image()
    all_messages = ' '.join(combined_df['message_content'].dropna())
    st.image(generate_wordcloud(all_messages), use_column_width=True)

elif selected_chart == "User Reply Counts":
    st.header("User Reply Counts")
    user_reply_counts = combined_df.groupby('sender_name')['reply_count'].sum()
    st.bar_chart(user_reply_counts)

elif selected_chart == "Top Message Senders":
    st.header("Top Message Senders")
    top_message = get_top_users(combined_df)
    st.bar_chart(top_message)

elif selected_chart == "Average Reply Count per User":
    reply_count=combined_df.groupby('sender_name')['reply_count'].mean().sort_values(ascending=False)[:20]
    st.header(f'Average Number of reply count per Sender in all channels combined')
    st.bar_chart(reply_count)
    # plt.show()

elif selected_chart == "Average Reply Users Count per User":
    st.header("Average Reply Users Count per User")
    average_reply_peruser = combined_df.groupby('sender_name')['reply_user_count'].mean().sort_values(ascending=False)[:20]
    st.bar_chart(average_reply_peruser)

elif selected_chart == "Average Word Count per Message":
    st.header("Average Word Count per Message")
    combined_df['word_count'] = combined_df['message_content'].apply(lambda x: len(str(x).split()))
    bin_size = int((combined_df['word_count'].max() - combined_df['word_count'].min()) / 10)  # Adjust 10 to your preference
    fig, ax = plt.subplots()
    sns.histplot(data=combined_df, x='word_count', bins=bin_size, kde=True, ax=ax)
    st.pyplot(fig)

elif selected_chart == "WordCloud for Each Channel":
    st.header("WordCloud for Each Channel")
    for channel_name, channel_messages in combined_df.groupby('channel_name')['message_content']:
        st.subheader(f"WordCloud for Channel: {channel_name}")
        channel_wordcloud = WordCloud(width=500, height=300, background_color='white').generate(
            ' '.join(channel_messages.dropna()))
        st.image(channel_wordcloud.to_image(), use_column_width=True)

elif selected_chart == "User Reactions":
    st.header("User Reactions")
    reactions = combined_df.groupby('sender_name')[['reply_count', 'reply_user_count']].sum()\
        .sort_values(by='reply_count', ascending=False)[:10]
    st.bar_chart()

# elif selected_chart == "Time Distribution of Messages":
#     st.header("Time Distribution of Messages")
#     combined_df['time_sent'] = pd.to_datetime(combined_df['time_sent'], unit='s')
#     combined_df['hour_sent'] = combined_df['time_sent'].dt.hour
#     sns.countplot(x='hour_sent', data=combined_df)
#     st.pyplot()

# elif selected_chart == "Time Difference Analysis":
#     st.header("Time Difference Analysis")
#     plt.figure(figsize=(15, 10))
#     plt.subplot(2, 2, 1)
#     plt.hist(combined_df['time_diff_message'].dt.total_seconds(), bins=50, color='blue', alpha=0.7)
#     plt.title('Time Difference Between Consecutive Messages')
#     plt.xlabel('Time Difference (seconds)')
#     plt.ylabel('Frequency')
#     st.pyplot()


elif selected_chart == "Message Classification Distribution":
    st.header("Message Classification Distribution")
    sns.countplot(x='message_category', data=combined_df)
    st.pyplot()

elif selected_chart == "Topic Modeling Results":
    st.header("Topic Modeling Results")
    lda_model = models.LdaModel.load(mlflow_model_path)
    for idx, topic in lda_model.print_topics():
        st.subheader(f'Topic {idx + 1}: {topic}')

elif selected_chart == "Sentiment Analysis":
    sentiment_plot_path = "./sentiment_analysis_plot.png"
    sentiment_plot = plt.imread(sentiment_plot_path)
    st.image(sentiment_plot, use_column_width=True, caption="Sentiment Over Time")


# MLflow integration
st.header("MLflow Model Info")
with st.spinner("Loading model info..."):
    lda_model = models.LdaModel.load(mlflow_model_path)
    st.text("Number of Topics: {}".format(lda_model.num_topics))

# Download data link
st.header("Download Data")
st.markdown("[Download Data Here](combined_df.csv)", unsafe_allow_html=True)

# Streamlit app command
if __name__ == '__main__':
    st.write("Navigate on the left please!")