import kevin_info
import requests
import json
import datetime
import calendar
import sqlite3
import facebook
from pprint import pprint

import plotly.plotly as py #visualization import using plotly
import plotly.graph_objs as go

#name: Kevin Rothstein

#creating cache system
CACHE_FNAME = "kevin_FB_cached_data.json" #name of cache file for my facebook data
try:
	cache_file = open(CACHE_FNAME,'r') #opens files and reads it
	cache_contents = cache_file.read() #converts the contents to string type
	CACHE_DICTION = json.loads(cache_contents) #loads contents into a dictionary
	cache_file.close() #closes the cache file
except:
	CACHE_DICTION = {}

#creating another cache file for different data
CACHE_FNAME1 = "kevin_INSTA_cached_data.json" #name of cache file for my instagram data 
try:
	cache_file1 = open(CACHE_FNAME1,'r')
	cache_contents1 = cache_file1.read()
	CACHE_DICTION1 = json.loads(cache_contents1)
	cache_file1.close()
except:
	CACHE_DICTION1= {}

def get_my_facebook_information(facebook_access_token): #function for facebook data
	if facebook_access_token in CACHE_DICTION: #check cache for data
		print("...using cache...")
		returned_facebook_data = CACHE_DICTION[facebook_access_token]
	else:

		print("...fetching FACEBOOK data...")
		the_graph = facebook.GraphAPI(access_token=facebook_access_token, version="2.1")
		my_data = the_graph.request('me?fields=feed.limit(100){created_time,likes}') #requests data, limits to 100
		my_user_id = my_data['id']
		my_posts = my_data['feed']['data'] #iterates through data to retieve needed info
		returned_facebook_data = [] #empty list to add data and info later
	
		amount_of_posts = 0
		for kevin in my_posts: #iterates through all posts to find specified data
			amount_of_posts += 1
			my_created_time = kevin['created_time'] #time of post
			
			year = int(my_created_time[:4]) #gets year,month,day post was posted 
			month = int(my_created_time[5:7]) 
			day = int(my_created_time[8:10]) 
			date = datetime.datetime(year, month, day) 
			days = date.weekday()
			
			#checks value and assign to specific day
			if days == 0:
				day_of_the_week = "Monday"
			
			elif days == 1:
				day_of_the_week = "Tuesday"
			
			elif days == 2:
				day_of_the_week = "Wednesday"
			
			elif days == 3:
				day_of_the_week = "Thursday"
			
			elif days == 4:
				day_of_the_week = "Friday"
			
			elif days == 5:
				day_of_the_week = "Saturday"
			
			else:
				day_of_the_week = "Sunday"
			
			likes = 0
			if 'likes' in kevin.keys(): #checks keys of dict
				for like in kevin['likes']['data']:
					likes += 1 #accumilator for amount of likes on a post
			returned_facebook_data.append((my_user_id, day_of_the_week, likes)) #creates a tuple (user id, day fo the week, and value of likes)
			CACHE_DICTION[facebook_access_token] = returned_facebook_data #puts data in cache
			my_file = open(CACHE_FNAME, 'w')  #writers data to file
			my_file.write(json.dumps(CACHE_DICTION))
			my_file.close() #closes cache file
	return returned_facebook_data

def get_my_instagram_information(instagram_access_token): #creat function using instagram access token 
	if instagram_access_token in CACHE_DICTION1: #checking if data is in cache 
		print("...using cache...")
		returned_instagram_data = CACHE_DICTION1[instagram_access_token]
	else:
		print("...fetching INSTA data...")
		url = 'https://api.instagram.com/v1/users/self/media/recent/?access_token=' + instagram_access_token #instagram access token added to instagram url
		my_data = requests.get(url).text #request data
		my_posts = json.loads(my_data)['data'] #returns data into dictioanry and iterates to 'data' key -->string
		my_user_id = my_posts[0]['user']['id'] #retrieves ID
		# print(my_user_id)
		returned_instagram_data = []
		
		for kevin in my_posts: #looping through posts to fetch results
			my_time = kevin['created_time'] #time stamp
			my_timestamp = datetime.datetime.fromtimestamp(int(my_time))
			# print(my_timestamp)
			my_weekday = calendar.day_name[my_timestamp.weekday()]
			my_likes = kevin['likes']['count'] #retrieves like count
			# print(my_likes)
			returned_instagram_data.append((my_user_id, my_weekday, my_likes)) #appends data in a tuple (id, time stamp, and like count)
			CACHE_DICTION1[instagram_access_token] = returned_instagram_data #adds to cache
			my_file1 = open(CACHE_FNAME1, 'w')
			my_file1.write(json.dumps(CACHE_DICTION1))
			my_file1.close()
	return returned_instagram_data

my_facebook_data = get_my_facebook_information(kevin_info.facebook_access_token) #calls the function with facebook access token 
my_instagram_data = get_my_instagram_information(kevin_info.instagram_access_token) #calls the function with instagram access token
# pprint(my_facebook_data)

#creating a total number of likes per day so i can make a visualization comparing likes and day posted
like_num = 0
total_FB_data = {'Sunday': 0, "Monday": 0, "Tuesday": 0,
"Wednesday": 0, "Thursday": 0, "Friday": 0, "Saturday": 0}
for x in my_facebook_data:
	day_of_week = x[1]
	# print(day_of_week)
	like_cnt = x[2]
	total_FB_data[day_of_week] += like_cnt #accumilating the total number of likes per day
# pprint(total_FB_data)

#creates visualization
py.sign_in('kevrothstein', '4SXrrz7CRGQqRyhhrGEA') #signing into plotly using my username and requested password
traces = []
for data in total_FB_data.items(): #iterate through facebook data to get likes and day
	day = data[0]
	cnt = data[1]

	#creating my x and y axis
	traces.append(go.Bar(
		x = day,
		y = cnt,
		name= cnt
		))
	layout = go.Layout(
		title = "Number of Facebook Likes per Each Day of the Week",
		yaxis = dict(
			title = "Number of Likes"),
		xaxis = dict(
			title = "Day of the Week")
		)

data = go.Data(traces)
fig = go.Figure(data=data, layout = layout)
py.plot(fig, filename = 'Facebook Bar Graph') #name of file

#creating database
conn = sqlite3.connect("kevin_facebook_database.sqlite")
curs = conn.cursor()
curs.execute("DROP TABLE IF EXISTS Kevin_Facebook_Table") #facebook table
curs.execute("CREATE TABLE Kevin_Facebook_Table (User_ID NUMBER, Weekday TEXT, Likes NUMBER)") #columns
#looping through all facebook posts user_id, weekday, and likes
for kevin in my_facebook_data:
	curs.execute('INSERT INTO Kevin_Facebook_Table (User_ID, Weekday, Likes) VALUES (?,?,?)', (kevin[0], kevin[2], kevin[1])) #fills out table
	conn.commit()
#creates connection to sql for facebook data
curs.execute("DROP TABLE IF EXISTS Kevin_Instagram_Table") #insta table
curs.execute("CREATE TABLE Kevin_Instagram_Table (User_ID NUMBER, Weekday, Likes NUMBER)") #columns
#looping through all instagram posts User_id, weekeday, and likes 
for kevin in my_instagram_data:
	curs.execute('INSERT INTO Kevin_Instagram_Table (User_ID, Weekday, Likes) VALUES (?,?,?)', (kevin[0], kevin[1], kevin[2])) #fills out table 
	conn.commit()
#creates connection to sql for instagramdata
curs.close()
