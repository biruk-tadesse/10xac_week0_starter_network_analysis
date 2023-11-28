import os
import sys
import glob
import json
import datetime
from collections import Counter
from collections import Counter

import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
from nltk.corpus import stopwords


def break_combined_weeks(combined_weeks):
    """
    Breaks combined weeks into separate weeks.

    Args:
        combined_weeks: list of tuples of weeks to combine

    Returns:
        tuple of lists of weeks to be treated as plus one and minus one
    """
    plus_one_week = []
    minus_one_week = []

    for week in combined_weeks:
        if week[0] < week[1]:
            plus_one_week.append(week[0])
            minus_one_week.append(week[1])
        else:
            minus_one_week.append(week[0])
            plus_one_week.append(week[1])

    return plus_one_week, minus_one_week


def get_msgs_df_info(df):
    msgs_count_dict = df.user.value_counts().to_dict()
    replies_count_dict = dict(Counter([u for r in df.replies if r != None for u in r]))
    mentions_count_dict = dict(Counter([u for m in df.mentions if m != None for u in m]))
    links_count_dict = df.groupby("user").link_count.sum().to_dict()
    return msgs_count_dict, replies_count_dict, mentions_count_dict, links_count_dict


def get_messages_dict(msgs):
    msg_list = []

    for msg in msgs:
        message_type = msg.get("subtype", "message")
        message_content = msg.get("text", None)
        sender_name = msg.get("user", None)
        time_sent = msg.get("ts", None)
        message_distribution = "channel_join" if message_type == "channel_join" else "message"

        msg_dict = {
            "message_type": message_type,
            "message_content": message_content,
            "sender_name": sender_name,
            "time_sent": time_sent,
            "message_distribution": message_distribution,
            "time_thread_start": msg["ts"] if "parent_user_id" in msg else None,
            "reply_count": len(msg["replies"]) if "thread_ts" in msg and "reply_users" in msg else None,
            "reply_user_count": len(msg["reply_users"]) if "thread_ts" in msg and "reply_users" in msg else None,
            "time_thread_end": msg["ts"] if "thread_ts" in msg and "reply_users" in msg else None,
            "reply_users": msg["reply_users"] if "thread_ts" in msg and "reply_users" in msg else None,
            "blocks": [],
            "emojis": [],
            "mentions": [],
            "links": [],
            "link_count": 0
        }

        if "blocks" in msg and msg["blocks"] is not None:
            emoji_list = []
            mention_list = []
            links = []

            for blk in msg["blocks"]:
                if "elements" in blk:
                    for elm in blk["elements"]:
                        if "elements" in elm:
                            for elm_ in elm["elements"]:
                                if "type" in elm_:
                                    if elm_["type"] == "emoji":
                                        emoji_list.append(elm_["name"])
                                    elif elm_["type"] == "user":
                                        mention_list.append(elm_["user_id"])
                                    elif elm_["type"] == "link":
                                        links.append(elm_["url"])

            msg_dict["emojis"] = emoji_list
            msg_dict["mentions"] = mention_list
            msg_dict["links"] = links
            msg_dict["link_count"] = len(links)

        msg_list.append(msg_dict)

    return msg_list


def from_msg_get_replies(msg):
    replies = []
    if "thread_ts" in msg and "replies" in msg:
        try:
            for reply in msg["replies"]:
                reply["thread_ts"] = msg["thread_ts"]
                reply["message_id"] = msg["client_msg_id"]
                replies.append(reply)
        except:
            pass
    return replies


def msgs_to_df(msgs):
    msg_list = get_messages_dict(msgs)
    df = pd.DataFrame(msg_list)
    return df


def process_msgs(msg):
    '''
    select important columns from the message
    '''

    keys = ["client_msg_id", "type", "text", "user", "ts", "team",
            "thread_ts", "reply_count", "reply_users_count"]
    msg_list = {k: msg[k] for k in keys}
    rply_list = from_msg_get_replies(msg)

    return msg_list, rply_list


def get_messages_from_channel(channel_path):
    '''
    get all the messages from a channel        
    '''
    channel_json_files = os.listdir(channel_path)
    channel_msgs = [json.load(open(channel_path + "/" + f)) for f in channel_json_files]

    df = pd.concat([pd.DataFrame(get_messages_dict(msgs)) for msgs in channel_msgs])
    print(f"Number of messages in channel: {len(df)}")

    return df


def convert_2_timestamp(column, data):
    """convert from unix time to readable timestamp
        args: column: columns that needs to be converted to timestamp
                data: data that has the specified column
    """
    if column in data.columns.values:
        timestamp_ = []
        for time_unix in data[column]:
            if time_unix == 0:
                timestamp_.append(0)
            else:
                a = datetime.datetime.fromtimestamp(float(time_unix))
                timestamp_.append(a.strftime('%Y-%m-%d %H:%M:%S'))
        return timestamp_
    else:
        print(f"{column} not in data")