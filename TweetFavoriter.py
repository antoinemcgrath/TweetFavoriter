#### A script for exporting twitter data of a specific list

#### Specify your processed directory
backups_dir = "processed_tweets"

import os
import json
import tweepy
import re
import time
import errno
from bson.json_util import dumps
from sys import argv

script, subject, query = argv

#python3 TweetFavoriter.py CRSReports "Congressional Research Service Reports"
#python3 TweetFavoriter.py CRSReports "Congressional Research Service Report"
#python3 TweetFavoriter.py CRSReports "CRS Reports"
#python3 TweetFavoriter.py CRSReports "CRS Report"

#python3 TweetFavoriter.py Baratza "Sette 270"
#python3 TweetFavoriter.py Baratza "Sette270"

#python3 TweetFavoriter.py ChrisK "Quantitea"


print("the script is called:", (script))
print("your subject variable is:", (subject))
print("your query words variable is:", (query))


#### Allow for reject lists (auto-lowercase for faster computing)
auto_rejects = ['100 crs', 'TurkeyInsights', 'Crs_tiant', 'pakai', 'CAR014, Neuro', 'toxicities',
                'crosses', 'Judwa2,' 'BoxOffice', 'Common Reporting Standard', 'CAR-T', 'lac crs',
                'ZairaWasim', 'bollywood', 'Qiita', 'Emaar',
                'Speechlys', 'CRS_Healthcare', 'pharmac', 'csr', 'god', '20 crs', 'white nationalist',
                'KKK','nazi','hitler','tea party', 'tea pain', 'tea bagger', 'racist', 'fuck']

lower_auto_rejects = []
for ban in auto_rejects:
    lower_auto_rejects.append(ban.lower())
auto_rejects = lower_auto_rejects


#### Load API keys file
keys_json = json.load(open('/usr/local/keys.json'))


#### Specify key dictionary wanted (generally [Platform][User][API])
#Keys = keys_json["Twitter"]["ClimateCong_Bot"]["ClimatePolitics"]
Keys = keys_json["Twitter"]["AGreenDCBike"]["Mentions_Monitor"]



max_tweets = 200


#### Access API using key dictionary definitions
auth = tweepy.OAuthHandler( Keys['Consumer Key (API Key)'], Keys['Consumer Secret (API Secret)'] )
auth.set_access_token( Keys['Access Token'], Keys['Access Token Secret'] )
api = tweepy.API(auth)
#user = Keys['Owner']




#### Define twitter rate determining loop
#Follow add rate limited to 1000 per 24hrs: https://support.twitter.com/articles/15364
def twitter_rates():
    stats = api.rate_limit_status()  #stats['resources'].keys()
    for akey in stats['resources'].keys():
        if type(stats['resources'][akey]) == dict:
            for anotherkey in stats['resources'][akey].keys():
                if type(stats['resources'][akey][anotherkey]) == dict:
                    #print(akey, anotherkey, stats['resources'][akey][anotherkey])
                    limit = (stats['resources'][akey][anotherkey]['limit'])
                    remaining = (stats['resources'][akey][anotherkey]['remaining'])
                    used = limit - remaining
                    if used != 0:
                        print("Twitter API used:", used, "requests used,", remaining, "remaining, for API queries to", anotherkey)
                    else:
                        pass
                else:
                    pass  #print("Passing")  #stats['resources'][akey]
        else:
            print(akey, stats['resources'][akey])
            print(stats['resources'][akey].keys())
            limit = (stats['resources'][akey]['limit'])
            remaining = (stats['resources'][akey]['remaining'])
            used = limit - remaining
            if used != 0:
                print("Twitter API:", used, "requests used,", remaining, "remaining, for API queries to", akey)
                pass
twitter_rates()


searched_tweets = [status for status in tweepy.Cursor(api.search, q=query).items(max_tweets)]
print(len(searched_tweets))

#### Create directories when they do not exist
def make_path_exist(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise
make_path_exist(backups_dir)


#### Create file for processed tweets
processed_file = backups_dir + "/" + subject + ".json"
if os.path.isfile(processed_file) == False:
    f = open(processed_file, 'a')
    f.write('[""]')
    f.close()
else:
    pass


#### Read file of processed tweets as JSON list
f = open(processed_file, 'r')
processed = json.load(f)
f.close()


#### To favorite (aka like & heart) a tweet
def favoriting_tweet(tweet):
    try:
        api.create_favorite(tweet.id_str)
        print("Favoriting", tweet.id_str, tweet.text)
    except tweepy.TweepError as e:
        if e.api_code == 139:
            print("Your account already liked this tweet")
        else:
            print(e.api_code)
            print(e.response)
        pass
    return()

#### Definition of tweet processing
def process_this_tweet(tweet):
    twtext = tweet.text.lower()
    for reject_word in auto_rejects:
        if twtext.find(reject_word) != -1:
            print("Tweet contains a reject word(s):", reject_word, twtext)
            return()
        else:
            #print("Reject word was not present")
            pass
    #print("Detect Sentiment", "Tweet it now")
    favoriting_tweet(tweet)
    return()



#### Process tweets & add newly processed tweets to JSON list
print(len(processed), processed)
processed_count = 0
for tweet in searched_tweets:
    twURL = str("https://twitter.com/AGreenDCBike/status/"+tweet.id_str)
    if processed.count(tweet.id_str) == 0:
        process_this_tweet(tweet)
        processed.append(tweet.id_str)
        print(twURL, tweet.text)
    else:
        processed_count += 1
        pass
print("Tweets already processed:", processed_count)

#print(len(processed), processed)


#### Write processed tweets to file
f = open(processed_file, 'w')
f.flush()
json.dump(processed, f)
f.close()
