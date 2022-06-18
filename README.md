# clubfeast


# To run script on a local machine:

  ## 1. Create virtualenv(first time only).
    virtualenv venv

  ## 2. Activate virtualenv(each time).
    source venv/bin/activate

  ## 3. Install libraries(first time only).
    pip install selenium webdriver-manager beautifulsoup4 pandas pytz

  ## 4. Run chrome remote webdriver on docker.
    docker run -d -p 4444:4444 --shm-size="2g" selenium/standalone-chrome:latest

  ## 5. Run code.
    python code.py



# To run script on docker:
  
  ## 1. Open terminal/cmd in project dir.

  ## 2. Create and set following environment variables in .env file.
    # _CLUBFEAST_USER_EMAIL
    # _CLUBFEAST_USER_PASSWORD
    # _8X8_USER_USERNAME
    # _8X8_USER_PASSWORD
    # ORDERS_REGION

  ## 3. Run one of the following docker command.
    docker compose up --build
    # or
    docker compose up --build --remove-orphans
    # or
    docker compose up --build --remove-orphans --abort-on-container-exit
    # or
    docker compose up --build --remove-orphans --abort-on-container-exit > script_logs.txt
