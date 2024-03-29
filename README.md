# Clubfeast-Orders-Reminder-Message-Automation

An automation script to automate the orders reminder messages in the following way, 

    1. Scrap the orders data from clubfeast admin portal.
    2. Preprocess the orders data and schedule them.
    3. Send the reminder messages through 8x8 before the specified period of time for each order.

## To run script on a local machine:

  #### 1. Create virtualenv(first time only).
    virtualenv venv

  #### 2. Activate virtualenv(each time).
    source venv/bin/activate

  #### 3. Install libraries(first time only).
    pip install selenium webdriver-manager beautifulsoup4 pandas pytz python-dotenv
    # or
    pip install -r requirements.txt

  #### 4. Run chrome remote webdriver on docker.
    docker run -d -p 4444:4444 --shm-size="2g" selenium/standalone-chrome:latest

  #### 5. Create and set following environment variables in .env file.
    # Set ClubFeast User Creds.
    _CLUBFEAST_USER_EMAIL = your_clubfeast_email
    _CLUBFEAST_USER_PASSWORD = your_clubfeast_password

    # Set 8X8 User Creds.
    _8X8_USER_USERNAME = your_8x8_username
    _8X8_USER_PASSWORD = your_8x8_password

    # Set Orders Region to EAST or WEST.
    ORDERS_REGION = EAST

  #### 6. Uncomment line number 27 in code.py file.
    # load_dotenv() -> load_dotenv()

  #### 7. Run code.
    python code.py

## To run script on docker:
  
  #### 1. Open terminal/cmd in project dir.

  #### 2. Create and set following environment variables in .env file.
    # Set ClubFeast User Creds.
    _CLUBFEAST_USER_EMAIL = your_clubfeast_email
    _CLUBFEAST_USER_PASSWORD = your_clubfeast_password

    # Set 8X8 User Creds.
    _8X8_USER_USERNAME = your_8x8_username
    _8X8_USER_PASSWORD = your_8x8_password

    # Set Orders Region to EAST or WEST.
    ORDERS_REGION = EAST

  #### 3. Run one of the following docker command.
    docker compose up --build
    # or
    docker compose up --build --remove-orphans
    # or
    docker compose up --build --remove-orphans --abort-on-container-exit
    # or
    docker compose up --build --remove-orphans --abort-on-container-exit > script_logs.txt
