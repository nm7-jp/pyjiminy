pyjiminy
========

- pyjiminy is a scraping tool, which completes the following tasks:
- searching hotel availability in Tokyo Disney resort
- notifying the status of hotel availability via g-mail


Requirements
------------

- `Less secure app access`_ should be turned off in source gmail account
- Generate `G-Mail application password`_ beforehand
- Docker engine should be installed on your host

.. _Less secure app access: https://support.google.com/accounts/answer/6010255?hl=en#zippy=%2Cuse-an-app-password%2Cuse-more-secure-apps%2Cif-less-secure-app-access-is-off-for-your-account
.. _G-Mail application password: https://support.google.com/accounts/answer/185833

Getting Started
------------

1. Clone the repository from github

.. code-block:: text

    $ git clone https://github.com/nm7-jp/pyjiminy.git

2. Change directory to repostiroy root

.. code-block:: text

    $ cd pyjiminy

3. Create `.env` to repository root and define environment variables

.. code-block:: text

    # Define PYJIMINY_ENV as "development" for debug mode
    PYJIMINY_ENV=development

    # Your GMAIL application password
    PYJIMINY_GMAIL_APP_PASSWORD=xxxxx

    # source e-mail address
    PYJIMINY_GMAIL_FROM_ADDRESS=yyyyy@gmail.com

    # destination e-mail address
    PYJIMINY_GMAIL_TO_ADDRESS=aaaaa@bbbbb

    # Abbreviation of target disney hotel
    ## DAH: Disney Ambassador Hotel
    ## DHM: tokyo Disney sea Hotel MIRACOSTA
    ## TDH: Tokyo Disney land Hotel
    ## DCH: tokyo disney Celebration Hotel
    PYJIMINY_HOTEL_NAME=DHM
    
    # Arrival year, month and day for hotel booking
    PYJIMINY_HOTEL_ARRIVAL_YEAR=2022
    PYJIMINY_HOTEL_ARRIVAL_MONTH=2
    PYJIMINY_HOTEL_ARRIVAL_DAY=25

    # Number of stay nights, rooms and adults for hotel
    PYJIMINY_HOTEL_STAY_NIGHTS=1
    PYJIMINY_HOTEL_ROOM_NUMBERS=1
    PYJIMINY_HOTEL_ADULT_NUMBERS=2

4. Build docker container image

.. code-block:: text

    $ make build

5. Run docker container

.. code-block:: text

    $ make start