import praw 
import pandas as pd 
from credentials import MyCreds
from itertools import islice

def scraper(subreddit = 'AmItheAsshole', time_filter = 'month', num_posts = 1):
    
    mycreds = MyCreds()

    reddit_read_only = praw.Reddit(client_id=mycreds.client_id,
                                client_secret=mycreds.client_secret,
                                user_agent=mycreds.user_agent,)

    subreddit = reddit_read_only.subreddit(subreddit)

    posts = subreddit.top(time_filter=time_filter)
    first_num_posts = list(islice(posts, num_posts))
    # Scraping the top posts of the current month
    
    posts_dict = {"Title": [], "Post Text": [],
                "ID": [], "Author": []
                }

    for post in first_num_posts:
        # Title of each post
        posts_dict["Title"].append(post.title)
        
        # Text inside a post
        posts_dict["Post Text"].append(post.selftext)
        
        # Unique ID of each post
        posts_dict["ID"].append(post.id)
        
        # Unique ID of each post
        posts_dict["Author"].append(post.author)
        
    # Saving the data in a pandas dataframe
    top_posts = pd.DataFrame(posts_dict)
    file_name =  f'Top {num_posts} posts of {subreddit} during past {time_filter}.csv'
    top_posts.to_csv(file_name, index=False)
    return file_name

if __name__ == '__main__':
    scraper()