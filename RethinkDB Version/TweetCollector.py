'''Use this module to collect tweets from the live stream.'''
import tweepy
import json
import rethinkdb as r
from rethinkdb.errors import RqlRuntimeError

# This works best outside class StdOutListener as
# it's own function.
def database_connect():
    '''Creates the database and the table if it doesn't already exist'''
    db_name = 'test'# Enter name of your database
    table_name = 'chat_test_1'# Enter name of your table
    conn = r.connect('localhost', 28015)
    try:
        try:
            r.db_create(db_name).run(conn)
            r.db(db_name).table_create(table_name).run(conn)
            print("Database setup completed!")
        except RqlRuntimeError:
            r.db(db_name).table_create(table_name).run(conn)
            print("Database already exists!")
    except:
        print("Database and table exist!")
    finally:
        conn.close()

# This seems to only work outside the class.

class StdOutListener(tweepy.StreamListener):
    '''Used to override the StreamListener so you can do what you want
    with the data streaming in.'''
    def __init__(self, limit):
        self.limit = limit
        self.num_of_tweets = 0
        self.conn = r.connect('localhost', 28015)
    def on_data(self, data):
        '''Prints the data on screen and stores certain parts in a RethinkDB
        database.'''
        print(data)
        try:
            self.num_of_tweets += 1
            if self.num_of_tweets < self.limit:
                tweet_data = json.loads(data)
                r.db('test').table('chat_test_1').insert(tweet_data).run(self.conn)
                return True
            else:
                print("Done Collecting!")
                return False
        except Exception:
            pass

    def on_error(self, status):
        '''prints out any errors that come from the listener.'''
        print (status)

class TweetStream(object):
    '''Used to access the streaming portion of the API
     that actually prints out live tweets.'''
    def __init__(self, limit, tag):
        self.consumer_key = ""
        self.consumer_secret = ""
        self.access_token = ""
        self.access_token_secret = ""
        self.rate_limit = limit
        self.tag = tag

    def key_grabber(self):
        '''Grabs the keys needed for OAuth.'''
        self.consumer_key = ""
        self.consumer_secret = ""
        self.access_token = ""
        self.access_token_secret = ""

    def streamer(self):
        '''Instantiates the listener class we created above and
        also access the stream. stream.filter(track=[]) is where,
        you tell tweepy what keywords to look for.'''
        listen = StdOutListener(self.rate_limit)
        auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
        auth.set_access_token(self.access_token, self.access_token_secret)
        stream = tweepy.Stream(auth, listen)
        stream.filter(track=[self.tag])
        print(stream)
