# -*- coding: utf-8 -*-
from posixpath import dirname
import smtplib
from email.mime.text import MIMEText
from pyfields import field, make_init

from logging import getLogger, config
import yaml
from . import const as C

C.SMTP_SERVER = "smtp.gmail.com"
C.SMTP_PORT = 587

with open(dirname(__file__) + "/yaml/config.yml") as f:
    config.dictConfig(yaml.safe_load(f))
logger = getLogger(__name__)


class GmailSender():
    
    password:str = field(check_type=True, doc='g-mail login password must be str')
    from_addr:str = field(validators={f'source e-mail address should be gmail account' : lambda from_addr: "gmail" in from_addr})
    to_addr:str = field(check_type=True, doc='destination e-mail address must be str')
    subject:str = field(check_type=True, doc='e-mail subject must be str')
    body:str = field(check_type=True, doc='e-mail body must be str')
    __init__ = make_init()

    def __create_message(self):
        """create e-mail message to be sent

        Returns:
            MIMEText: Costructed MIMEText-type e-mail message
        """
        msg = MIMEText(self.body)
        msg['Subject'] = self.subject
        msg['From'] = self.from_addr
        msg['To'] = self.to_addr
        return msg

    def send(self):
        """Establish TLS connection to G-mail SMTP server and Send e-mail via 
           G-mail account
        """
        msg = self.__create_message()

        try:
            smtpobj = smtplib.SMTP(C.SMTP_SERVER, C.SMTP_PORT)
            smtpobj.starttls()
            smtpobj.login(self.from_addr, self.password)
            smtpobj.sendmail(self.from_addr, self.to_addr, msg.as_string())
        except Exception as e:
            logger.exception('ERROR: %s', e)
        finally:
            smtpobj.close()