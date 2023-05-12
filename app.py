# Python program to illustrate
# desktop news notifier
import feedparser
import logging
import smtplib, ssl
import os
import json
from datetime import datetime, timedelta
from dateutil.parser import parse
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart


class newsItem:
    def __init__(self, title, summary, date, link, image):
        self.title = title
        self.summary = summary
        self.date = date
        self.link = link
        self.image = image
	
    def __str__(self):
        return f"{self.title}: {self.summary} \n{self.date}\n{self.link}"
    
    def html(self):
        return f"<b>{self.title}</b><br>{self.summary}<br>{self.date}<br>{self.link}"
	

def parseFeed(URL: str):
    news = feedparser.parse(URL)
    items = []
    for x in news["items"]:
        #Parse News Data
        try: 
            new = newsItem(x["title"], None, x["published"], x["link"], None)

            #Attempt to grab summary
            try:
                new.summary = x["summary"]
            except:
                None

            #Attempt to grab thumbnail
            try: 
                new.image = x["media_thumbnail"][0]["url"]
            except: 
                try:
                    new.image = x["media_content"][0]["url"]
                except:
                    None
            items.append(new)
            
        except Exception as e: 
            if (e.args[0] != "published"):
                logging.error("Could not parse data...\n" + "Error: " + str(e))

    if (len(items) == 0):
        logging.error(f"No stories were found for URL: {URL}")
    return items


# Script Entrance!
if __name__ == "__main__":
    
    # Attempt to run application
    try:
        script_path = os.path.abspath(__file__)
        script_path = script_path.replace("/app.py", "")

        # Open and clear log file
        log_file = os.path.join(script_path, "app.log")
        with open(log_file, "w"): pass

        # Configure logging
        logging.basicConfig(format="%(asctime)s %(levelname)s:%(message)s", filename=log_file, level=logging.DEBUG)

        # Configure application
        logging.debug("Parsing config file...")
        with open(os.path.join(script_path, "config.json"), "r") as f:
            config = json.load(f)
            
        email_recipients = config["recipients"]
        key_words        = config["key_words"]
        email_sender     = config["sender"]
        email_password   = config["sender_pass"]
        rss_urls         = config["rss_urls"]

        # Read RSS Feeds
        logging.debug("Parsing News Stories...")
        feed = []
        for rss_url in rss_urls:
            try:
                feed.extend(parseFeed(rss_url))
            except Exception as e:
                logging.error(f"Error parsing feed for url ({rss_url}): " + str(e))

    
        # Get the current date and time
        now = datetime.now() 
        lastPubDate = (now - timedelta(hours=24)).timestamp()
        
        # Filter RSS feeds based on the keywords and the last 24 hours 
        filtered_feed = [item for item in feed if any(keyword in (item.title.lower().rstrip("s") or item.summary.lower().rstrip("s")) for keyword in key_words)]
        filtered_feed = [item for item in filtered_feed if parse(item.date).timestamp() >= lastPubDate]


        # EMAIL
        logging.debug("Creating Email Message...")
        # Create email message
        message = MIMEMultipart("related")
        
        # Read the HTML file
        with open(os.path.join(script_path, "email.html"), "r") as f:
            html = f.read()
            
        # Modify HTML for parsed news stories
        media1 = open(os.path.join(script_path, "media1.html"), "r").read()
        media2 = open(os.path.join(script_path, "media2.html"), "r").read()
        media3 = open(os.path.join(script_path, "media3.html"), "r").read()

        # Dynamically add media content
        logging.debug("Filtering Feed...")
        count = 1
        media = ""
        for item in filtered_feed:
            # Thumbnail found
            if (item.image != None):
                if ((count % 2) == 0):
                    media += media1
                else:
                    media += media2
                    
                # Insert thumbnail
                media = media.replace(f"[image]", item.image)
                
            # No thumbnail  
            else: 
                media += media3
            
            # Insert rest of html feed elements
            media = media.replace(f"[title]", item.title)
            media = media.replace(f"[summary]", item.summary)
            media = media.replace(f"[published]", item.date)
            media = media.replace(f"[link]", item.link)
            count += 1

        html = html.replace("[media]", media)
        
        # Configure date
        date = now.strftime("%Y-%m-%d") # Format the date as a string in YYYY-MM-DD format
        html = html.replace("[date]", date)

        # Add email body
        message.attach(MIMEText(html, "html"))
        
        # Find all image files in the images folder
        image_dir = os.path.join(script_path, "images")
        image_filenames = [f for f in os.listdir(image_dir) if os.path.isfile(os.path.join(image_dir, f))]
        
        # Add constant embedded images
        logging.debug("Adding embedded images...")
        for file in image_filenames:
            with open(os.path.join(image_dir, file), "rb") as f:
                image_data = f.read()
            image = MIMEImage(image_data, str.split(file, ".")[1])
            image.add_header("Content-ID", f"<{file}>")
            image.add_header("Content-Disposition", "inline", filename=file)
            message.attach(image)

        # Set message headers
        message["Subject"] = "Today's News"
        message["From"] = email_sender
        message["Content-Type"] = "text/html"

        # Create a secure SSL context
        port = 465  # For SSL
        context = ssl.create_default_context()

        logging.debug("Sending Email Message...")
        with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
            server.login(email_sender, email_password)
            server.sendmail(email_sender, email_recipients, message.as_string())
        
        logging.debug("Success!")
    
    # Log any exceptions that break application
    except Exception as e:
        logging.error(f"Error ({str(now)}) running news feed notifier: " + str(e))