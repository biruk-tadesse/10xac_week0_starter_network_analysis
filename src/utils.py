import os
import re
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


# def get_messages_dict(msgs):
#     msg_list = []
#     for msg in msgs:
#         for m in msg:
#             message_type = m.get("subtype", "message")
#             message_content = m.get("text", None)
#             sender_name = m.get("user", None)
#             time_sent = m.get("ts", None)
#             message_distribution = "channel_join" if message_type == "channel_join" else "message"

#             msg_dict = {
#                 "message_type": message_type,
#                 "message_content": message_content,
#                 "sender_name": sender_name,
#                 "time_sent": time_sent,
#                 "message_distribution": message_distribution,
#                 "time_thread_start": m["ts"] if "parent_user_id" in m else None,
#                 "reply_count": len(m["replies"]) if "thread_ts" in m and "reply_users" in m else None,
#                 "reply_user_count": len(m["reply_users"]) if "thread_ts" in m and "reply_users" in m else None,
#                 "time_thread_end": m["ts"] if "thread_ts" in m and "reply_users" in m else None,
#                 "reply_users": m["reply_users"] if "thread_ts" in m and "reply_users" in m else None,
#                 "blocks": [],
#                 "emojis": [],
#                 "mentions": [],
#                 "links": [],
#                 "link_count": 0
#             }

#             if "blocks" in m and m["blocks"] is not None:
#                 emoji_list = []
#                 mention_list = []
#                 links = []

#                 for blk in m["blocks"]:
#                     if "elements" in blk:
#                         for elm in blk["elements"]:
#                             if "elements" in elm:
#                                 for elm_ in elm["elements"]:
#                                     if "type" in elm_:
#                                         if elm_["type"] == "emoji":
#                                             emoji_list.append(elm_["name"])
#                                         elif elm_["type"] == "user":
#                                             mention_list.append(elm_["user_id"])
#                                         elif elm_["type"] == "link":
#                                             links.append(elm_["url"])

#                 msg_dict["emojis"] = emoji_list
#                 msg_dict["mentions"] = mention_list
#                 msg_dict["links"] = links
#                 msg_dict["link_count"] = len(links)

#             msg_list.append(msg_dict)

#     return msg_list


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


def get_messages_df(msgs):
    msg_list = []

    for msg in msgs:
        for m in msg:
            message_type = m.get("subtype", "message")
            message_content = m.get("text", None)
            sender_name = m.get("user", None)
            time_sent = m.get("ts", None)
            message_distribution = "channel_join" if message_type == "channel_join" else "message"

            msg_dict = {
                "message_type": message_type,
                "message_content": message_content,
                "sender_name": sender_name,
                "time_sent": time_sent,
                "message_distribution": message_distribution,
                "time_thread_start": m["ts"] if "parent_user_id" in m else None,
                "reply_count": len(m["replies"]) if "thread_ts" in m and "reply_users" in m else 0,
                "reply_user_count": len(m["reply_users"]) if "thread_ts" in m and "reply_users" in m else 0,
                "time_thread_end": m["ts"] if "thread_ts" in m and "reply_users" in m else None,
                "reply_users": m["reply_users"] if "thread_ts" in m and "reply_users" in m else None,
                "blocks": [],
                "emojis": [],
                "mentions": [],
                "links": [],
                "link_count": 0
            }

            if "blocks" in m and m["blocks"] is not None:
                emoji_list = []
                mention_list = []
                links = []

                for blk in m["blocks"]:
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

    df = pd.DataFrame(msg_list)
    return df


def get_users_df(users):
    df = pd.json_normalize(users)
    columns = ['id', 'team_id', 'name', 'deleted', 'color', 'real_name', 'tz',
               'tz_label', 'tz_offset', 'is_admin', 'is_owner', 'is_primary_owner',
               'is_restricted', 'is_ultra_restricted', 'is_bot', 'is_app_user', 'profile.title', 'profile.phone', 'profile.skype', 'profile.real_name',
               'profile.display_name', 'profile.status_text',
               'profile.image_original', 'profile.email', 'profile.first_name', 'profile.last_name']
    return df[columns]


def get_channels_df(channels):
    df = pd.json_normalize(channels)
    columns = ['id', 'name', 'created', 'creator', 'is_general',
               'members']
    return df[columns]


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

    df = pd.concat([get_messages_df(msgs) for msgs in channel_msgs])
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
# combine all json file in all-weeks8-9
def slack_parser(path_channel):
    """ parse slack data to extract useful informations from the json file
        step of execution
        1. Import the required modules
        2. read all json file from the provided path
        3. combine all json files in the provided path
        4. extract all required informations from the slack data
        5. convert to dataframe and merge all
        6. reset the index and return dataframe
    """

    # specify path to get json files
    combined = []
    for json_file in glob.glob(f"{path_channel}*.json"):
        with open(json_file, 'r', encoding="utf8") as slack_data:
            combined.append(slack_data)

    # loop through all json files and extract required informations
    dflist = []
    for slack_data in combined:

        msg_type, msg_content, sender_id, time_msg, msg_dist, time_thread_st, reply_users, \
        reply_count, reply_users_count, tm_thread_end = [],[],[],[],[],[],[],[],[],[]

        for row in slack_data:
            if 'bot_id' in row.keys():
                continue
            else:
                msg_type.append(row['type'])
                msg_content.append(row['text'])
                if 'user_profile' in row.keys(): sender_id.append(row['user_profile']['real_name'])
                else: sender_id.append('Not provided')
                time_msg.append(row['ts'])
                if 'blocks' in row.keys() and len(row['blocks'][0]['elements'][0]['elements']) != 0 :
                     msg_dist.append(row['blocks'][0]['elements'][0]['elements'][0]['type'])
                else: msg_dist.append('reshared')
                if 'thread_ts' in row.keys():
                    time_thread_st.append(row['thread_ts'])
                else:
                    time_thread_st.append(0)
                if 'reply_users' in row.keys(): reply_users.append(",".join(row['reply_users'])) 
                else:    reply_users.append(0)
                if 'reply_count' in row.keys():
                    reply_count.append(row['reply_count'])
                    reply_users_count.append(row['reply_users_count'])
                    tm_thread_end.append(row['latest_reply'])
                else:
                    reply_count.append(0)
                    reply_users_count.append(0)
                    tm_thread_end.append(0)
        data = zip(msg_type, msg_content, sender_id, time_msg, msg_dist, time_thread_st,
         reply_count, reply_users_count, reply_users, tm_thread_end)
        columns = ['msg_type', 'msg_content', 'sender_name', 'msg_sent_time', 'msg_dist_type',
         'time_thread_start', 'reply_count', 'reply_users_count', 'reply_users', 'tm_thread_end']

        df = pd.DataFrame(data=data, columns=columns)
        df = df[df['sender_name'] != 'Not provided']
        dflist.append(df)

    dfall = pd.concat(dflist, ignore_index=True)
    dfall['channel'] = path_channel.split('/')[-1].split('.')[0]        
    dfall = dfall.reset_index(drop=True)
    
    return dfall



def parse_slack_reaction(path, channel):
    """get reactions"""
    dfall_reaction = pd.DataFrame()
    combined = []
    for json_file in glob.glob(f"{path}*.json"):
        with open(json_file, 'r') as slack_data:
            combined.append(slack_data)

    reaction_name, reaction_count, reaction_users, msg, user_id = [], [], [], [], []

    for k in combined:
        slack_data = json.load(open(k.name, 'r', encoding="utf-8"))
        
        for i_count, i in enumerate(slack_data):
            if 'reactions' in i.keys():
                for j in range(len(i['reactions'])):
                    msg.append(i['text'])
                    user_id.append(i['user'])
                    reaction_name.append(i['reactions'][j]['name'])
                    reaction_count.append(i['reactions'][j]['count'])
                    reaction_users.append(",".join(i['reactions'][j]['users']))
                
    data_reaction = zip(reaction_name, reaction_count, reaction_users, msg, user_id)
    columns_reaction = ['reaction_name', 'reaction_count', 'reaction_users_count', 'message', 'user_id']
    df_reaction = pd.DataFrame(data=data_reaction, columns=columns_reaction)
    df_reaction['channel'] = channel
    return df_reaction

def get_community_participation(path):
    """ specify path to get json files"""
    combined = []
    comm_dict = {}
    for json_file in glob.glob(f"{path}*.json"):
        with open(json_file, 'r') as slack_data:
            combined.append(slack_data)
    # print(f"Total json files is {len(combined)}")
    for i in combined:
        a = json.load(open(i.name, 'r', encoding='utf-8'))

        for msg in a:
            if 'replies' in msg.keys():
                for i in msg['replies']:
                    comm_dict[i['user']] = comm_dict.get(i['user'], 0)+1
    return comm_dict


def get_tagged_users(df):
    """get all @ in the messages"""

    return df['msg_content'].map(lambda x: re.findall(r'@U\w+', x))


    
