from datetime import datetime
from posixpath import dirname
from . import settings
from .scraper import HotelSearcher
from .mail import GmailSender
import pandas
from .helper import convert_pandas_to_str
from logging import getLogger, config
import yaml

with open(dirname(__file__) + "/yaml/config.yml") as f:
    config.dictConfig(yaml.safe_load(f))
logger = getLogger(__name__)

def main():

    hotel = settings.HOTEL
    year = settings.YEAR
    month = settings.MONTH
    day = settings.DAY
    nights = settings.NIGHTS
    rooms = settings.ROOMS
    adults = settings.ADULTS
    
    password = settings.PASSWORD
    from_addr = settings.FROM_ADDRESS
    to_addr = settings.TO_ADDRESS
        
    searcher = HotelSearcher(hotel=hotel,year=year,month=month,day=day,
                             nights=nights,rooms=rooms,adults=adults)
    status = searcher.get_room_status()
    
    df = pandas.read_json(status)
    
    body = convert_pandas_to_str(df)
    subject = "[" + hotel + "]" \
                + "Room Availability Information" \
                + "[" + datetime.now().strftime('%Y-%m-%d %H:%M') + "]"

    
    mail = GmailSender(password=password,
                       to_addr=to_addr,
                       from_addr=from_addr,
                       body=body,
                       subject=subject)
    mail.send()