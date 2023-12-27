# ODU_REU_2023
## Using the Instagram Memento Scraper
The Python script takes the URI-M as a command line argument. For example, if you want to scrape information from https://web.archive.org/web/20170214033011/https://www.instagram.com/beyonce/, then you would navigate to the folder that contains the Python script and run the script with the following piece of code:

```ps
python instagram_memento_scraper.py --urim https://web.archive.org/web/20170214033011/https://www.instagram.com/beyonce/
```
## Code Output
The Instagram memento scraper outputs a JSON object, which can be interpreted as a Python dictionary. The output JSON object contains two main keys, "profileUser" and "userMedia." The value of the key "profileUser" is a dictionary that contains basic user profile information, including the username, biography, and follower count, on the Instagram handle associated with the URI-M. The value of the key "userMedia" is a list of dictionaries in which each dictionary represents a single Instagram post on the webpage associated with the URI-M. Each dictionary might include data such as the caption, comment count, or like count of an Instagram post. The amount and kind of information that can be scraped from an Instagram memento depends on the timestamp of the memento. For a detailed description of the information that can be scraped by my Python script, see https://github.com/rachelzheng03/ODU_REU_2023/blob/main/instagram_memento_scraper/Table%20of%20Information%20Extractable%20from%20Mementos.pdf. You can also direct the output to a JSON file from the command line. For instance, if you want to redirect the output from the example above to a JSON file named example14.json, you can put the following code in the command line:

```ps
python instagram_memento_scraper.py --urim https://web.archive.org/web/20170214033011/https://www.instagram.com/beyonce/ > example14.json
```
The full output for this example can be found at https://github.com/rachelzheng03/ODU_REU_2023/blob/main/instagram_memento_scraper/example_outputs/example14.json.
