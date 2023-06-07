import os
import time
import requests
import datetime

from dotenv import load_dotenv
load_dotenv()

class BanTracker:
    
    def __init__(self):
        """
        Initializes the BanTracker class by setting up the webhook URL and calling the necessary functions
        to set the initial state and start the main loop.
        """
        self.webhook = os.getenv('WEBHOOK_URL')
        self.get_latest_ban_id() # Initial Setup
        
        self.main_loop()
        

    def get_latest_bans(self):
        """
        Retrieves the latest bans by sending a GET request to a banlist API endpoint.
        
        Returns:
        - A JSON object containing the latest ban information obtained from the API.
        """
        res = requests.get(url='https://api.pvpgym.net/banlist?beginIndex=0&length=25')

        try:
            res.raise_for_status()
            return res.json()
        except requests.exceptions.HTTPError as e:
            print(e)
            
    
    def get_latest_ban_id(self):
        """
        Retrieves the ID of the latest ban from the list of bans obtained from the API.
        """
        bans = self.get_latest_bans()
        self.latest_ban_id = bans[0]['punished']
        
    
    def format_duration(self, seconds):
        """
        Formats a duration given in seconds into a human-readable string representation.
        
        Arguments:
        - seconds: The duration in seconds to be formatted.
        
        Returns:
        - A string representing the duration in years, months, weeks, and days.
        """
        duration = datetime.timedelta(seconds=seconds)

        years = duration.days // 365
        months = (duration.days % 365) // 30
        weeks = ((duration.days % 365) % 30) // 7
        days = ((duration.days % 365) % 30) % 7

        duration_str = ""
        if years > 0:
            duration_str += f"{years} year{'s' if years > 1 else ''}"
        if months > 0:
            duration_str += f", {months} month{'s' if months > 1 else ''}"
        if weeks > 0:
            duration_str += f", {weeks} week{'s' if weeks > 1 else ''}"
        if days > 0:
            duration_str += f", {days} day{'s' if days > 1 else ''}"

        if duration_str.startswith(", "):
            duration_str = duration_str[2:]

        return duration_str
        
    
    def get_embed(self, ban):
        """
        Generates an embed object containing ban information to be included in a Discord message.
        
        Arguments:
        - ban: A dictionary containing information about a ban.
        
        Returns:
        - A dictionary representing an embed object for a Discord message.
        """
        return {
            "title": ban['punishedName'],
            "color": 16711680,  # Red color
            "thumbnail": {
                "url": f"https://mc-heads.net/avatar/{ban['punished']}/64"
            },
            "fields": [
                {
                    "name": "Punishment",
                    "value": '`' + ban["type"] + '`',
                    "inline": True
                },
                {
                    "name": "Reason",
                    "value": '`' + ban["reason"] + '`',
                    "inline": True
                },
                {
                    "name": "Duration",
                    "value": f'`{self.format_duration(ban["duration"])}`',
                    "inline": False
                },
                {
                    "name": "Banned",
                    "value": f"<t:{round(ban['timestamp'])}:R>",
                    "inline": True
                },
                {
                    "name": "Unbanned",
                    "value": f"<t:{round(ban['timestamp'] + ban['duration'])}:R>",
                    "inline": True
                },
            ],
            "footer": {
                "text": ban['punished']
            }
        }
        
    
    def post_ban(self, ban):
        """
        Posts ban information to a Discord webhook by sending a POST request with a JSON payload
        containing an embed object.
        
        Arguments:
        - ban: A dictionary containing information about a user who has been banned from PvPGym.
        """
        res = requests.post(
            url=self.webhook,
            json = { 'embeds' : [self.get_embed(ban)] },
        )
        
        try:
            res.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print(e)
            
        
    def main_loop(self):
        """
        Continuously checks for new bans and posts them if they have not been processed yet.
        """
        while True:
            time.sleep(5)
            latest_bans = self.get_latest_bans()
            
            if not latest_bans:
                continue
        
            for ban in latest_bans:
                
                if ban['punished'] == self.latest_ban_id:
                    break
                
                self.post_ban(ban)
                
            self.latest_ban_id = latest_bans[0]['punished']
        
 
if __name__ == '__main__':
    BanTracker()
