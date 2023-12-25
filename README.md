# ODU_REU_2023
## Using the Instagram Memento Scraper
The Python script takes the URI-M as a command line argument. For example, if you want to scrape information from https://web.archive.org/web/20170214033011/https://www.instagram.com/beyonce/, then you would navigate to the folder that contains the Python script and run the script with the following piece of code:

```ps
python instagram_memento_scraper.py --urim https://web.archive.org/web/20170214033011/https://www.instagram.com/beyonce/
```
## Code Output
The Instagram memento scraper outputs a JSON object, which can be interpreted as a Python dictionary. The output JSON object contains two main keys, "profileUser" and "userMedia." The value of the key "profileUser" is a dictionary that contains basic user profile information, including the username, biography, and follower count, on the Instagram handle associated with the URI-M. The value of the key "userMedia" is a list of dictionaries in which each dictionary represents a single Instagram post on the webpage associated with the URI-M.
