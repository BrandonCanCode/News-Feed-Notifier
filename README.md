# News Feed Notifier

## Overview
News Notifier is a Python application that allows users to parse through their preferred news RSS feeds and send an email containing the latest news articles using the Google SMTP server and the user's login credentials. Additionally, users can specify a list of keywords to filter news articles. This application is particularly useful for individuals who want to stay up-to-date with the latest news but do not have the time to manually browse through multiple news websites.

## Installation
1. Clone the repository or download the zip file and extract it to a desired directory.
2. Open the terminal or command prompt and navigate to the extracted directory.
3. Install the required dependencies by running `pip install -r requirements.txt`.
4. Configure the application by filling in the required fields in `config.json`. This includes the user's Google login credentials, the recipient email address, and the news RSS feed URLs.
    - Note that a secondary google account may need to be setup to allow third-party apps to send emails using the stmp server. For example, I created a new
      email address for my homelab and aquired a 16 digit password for third-party app and I put the credentials into the information within the config file. 
5. Run the application by running `python app.py`.
6. Run automatically with a cron job like so (9AM everyday): `0 9 * * * /usr/bin/python3 /path/to/news-feed-notifier/app.py`.

## Usage
Upon running the application, it will parse through the configured news RSS feeds and send an email to the specified recipient containing the latest news articles. The application can be scheduled to run automatically at a specified time using a Cron job. Debugging and errors are sent to the app.log file.

## Key Words
These filter found RSS feeds to help customize articles for what the user is interested in. Note that the application searches for subwords within the article's summary. Key words should be set in the config with all lower case lettering and without appending 's', (e.g 'house', not 'Houses').

## Contributing
If you find a bug or would like to contribute to this project, please feel free to submit a pull request or open an issue. 

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.