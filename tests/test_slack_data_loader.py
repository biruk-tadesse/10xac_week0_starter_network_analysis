
import sys
sys.path.append('../') 
import unittest
import pandas as pd
from src import utils
from src.loader import SlackDataLoader


class TestSlackDataLoader(unittest.TestCase):
    def setUp(self):
        self.data_path = 'C:/Users/biruk.tadesse/Downloads/10 Academy Intensive Training/10xac/10xac_week0_starter_network_analysis/anonymized'
        self.loader = SlackDataLoader(self.data_path)

    def test_get_users_expected_columns(self):
        users = self.loader.get_users()
        users_df = utils.get_users_df(users)
        expected_columns = ['id', 'team_id', 'name', 'deleted', 'color', 'real_name', 'tz',
                            'tz_label', 'tz_offset', 'is_admin', 'is_owner', 'is_primary_owner',
                            'is_restricted', 'is_ultra_restricted', 'is_bot', 'is_app_user', 'profile.title', 'profile.phone', 'profile.skype', 'profile.real_name',
                            'profile.display_name', 'profile.status_text',
                            'profile.image_original', 'profile.email', 'profile.first_name', 'profile.last_name']
        self.assertListEqual(list(users_df.columns), expected_columns)

    def test_get_channels_expected_columns(self):
        channels = self.loader.get_channels()
        channels_df = utils.get_channels_df(channels)
        expected_columns = ['id', 'name', 'created', 'creator', 'is_general',
                            'members']
        self.assertListEqual(list(channels_df.columns), expected_columns)

    def test_get_channel_messages_expected_columns(self):
        channel_name = 'all-broadcast'
        channel_messages = self.loader.get_channel_messages(channel_name)
        channel_messages_df = utils.get_messages_df(channel_messages)
        # print(channel_messages_df.head())
        expected_columns = ["message_type",
                            "message_content",
                            "sender_name",
                            "time_sent",
                            "message_distribution",
                            "time_thread_start",
                            "reply_count",
                            "reply_user_count",
                            "time_thread_end",
                            "reply_users",
                            "blocks",
                            "emojis",
                            "mentions",
                            "links",
                            "link_count",]
        self.assertListEqual(list(channel_messages_df.columns), expected_columns)


if __name__ == '__main__':
    unittest.main()