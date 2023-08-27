import requests
from bs4 import BeautifulSoup
import json
import re
import argparse
import sys

def write_instagram_page_info_to_jsonl(filename, user_profile, posts):
	with open(filename, "w") as outfile:
		user_profile_str=json.dumps(user_profile)
		outfile.write(user_profile_str + "\n")

		for post in posts:
			dictionary=json.dumps(post)
			outfile.write(dictionary +"\n")
	return

def write_instagram_page_info_to_json(filename, dict):
	with open(filename, 'w') as outfile:
		json.dump(dict, outfile)
	return

#helper function for case 1, case 2, case 3
def get_portion_of_html_with_instagram_page_info(soup, timestamp):
	script_tag = soup.find_all('script') 
	for tag in script_tag:
		text = tag.contents
		#find tag with no attributes
		if (timestamp < 20140123000000) and (not bool(tag.attrs)):
			text=tag.contents[0]
			if 'window._jscalls' not in text:
				continue
			#print(text, file=sys.stderr)
			if timestamp<20130225000000:
				pattern=re.compile('^[\s\S]+window._jscalls[\s\S]+init",\[([\s\S]+),"AnonymousUser",\{"anonymous":[a-z]+\},\[([\s\S]+)')
				m=pattern.match(text)
				return m.groups()
			elif 20130302000000<=timestamp<20130412000000:
				pattern=re.compile('^[\s\S]+window._jscalls[\s\S]+("profileUser":[\s\S]+"userMedia":\[[\s\S]*\]),"moreAvailable')
				m=pattern.findall(text)
				return m
			else:
				pattern=re.compile('^[\s\S]+window._jscalls[\s\S]+("userMedia":[\s\S]+"user":\{[\s\S]*\}),"moreAvailable')
				m=pattern.findall(text)
				return m
		elif len(text)!=0 and text[0].startswith('window._sharedData'):
			if timestamp<20150226000000:
				pattern=re.compile('^window._sharedData[\s\S]+("userMedia":[\s\S]+"user":\{[\s\S]*\}),"moreAvailable')
				m=pattern.findall(text[0])
				return m
			elif 20150226000000<=timestamp<20150227000000:
				pattern=re.compile('^window._sharedData[\s\S]+\{("canSeePrerelease":[\s\S]+"user":\{[\s\S]*)\}\]\},"country_code')
				m=pattern.findall(text[0])
				return m
			# elif 20150610000000<=timestamp<20150630000000:
			# 	pattern=re.compile('^window._sharedData[\s\S]+"user":\{([\s\S]+"media":\{[\s\S]*)\},"__path":')
			# 	m=pattern.findall(text[0])
			# 	return m
			# else:
			# 	#print(text[0], file=sys.stderr)
			# 	#pattern=re.compile('^window._sharedData[\s\S]+"user":\{([\s\S]+"media":\{[\s\S]*)\}\}\]\},"hostname":')
			# 	#m=pattern.findall(text[0])
			# 	#return m
			# 	return text[0].strip('window._sharedData = ')[:-1]
			elif 20150610000000<=timestamp:
				return text[0].strip('window._sharedData = ')[:-1]

#helper functions for case 1 
def get_user_profile_dict_1(m, instagram_page_dict_temp, timestamp):
	if timestamp<=20130225000000:
		user_profile_string=m[0]
		user_profile_dict = json.loads(user_profile_string)
		return user_profile_dict
	#2013/03/02 and on
	elif 20130302000000<=timestamp<20130412000000:
		return instagram_page_dict_temp['profileUser']
	elif timestamp>=20130413000000:
		return instagram_page_dict_temp['user']

def clean_user_profile_dict(user_profile_dict):
	pic_link=user_profile_dict['profile_picture']
	profile_pic_status_code=get_resource_status_code(pic_link)
	user_profile_dict['profile_picture']={'uri':pic_link, 'status_code': profile_pic_status_code}
	return user_profile_dict

def split_posts(post_html, timestamp):
	if timestamp<20121109000000:
		return re.split(',\{"location|,\[\{"location', post_html)
	else:
		return re.split(',\{"can_delete_comments|,\[\{"can_delete_comments', post_html)
	
def post_to_dict(post_info, timestamp):
	if timestamp<20121109000000:
		if not post_info.startswith('{"location'):
			post_info='{"location'+post_info
		pattern=re.compile('^\{"location[\s\S]+\}\}')
	else:
		if not post_info.startswith('{"can_delete_comments'):
			post_info='{"can_delete_comments'+post_info
		pattern=re.compile('^\{"can_delete_comments[\s\S]+\}\}')

	m=pattern.match(post_info)
	post_info=m.group()
	try:
		post_dict=json.loads(post_info)
	except Exception as e:
		print(post_info, file=sys.stderr)
		raise(e)
	return post_dict

def clean_post_dict(post_dict):
	#print(post_dict.keys(), file=sys.stderr)
	try:
		comments_list=post_dict['comments']['data']
		for comment in comments_list:
			del comment['from']['profile_picture']

		if (post_dict['location']!=None) and ('id' in post_dict['location'].keys()):
			del post_dict['location']['id']

		if post_dict['caption']!=None:
			del post_dict['caption']['from']

		if post_dict['link']!=None:
			is_on_live_instagram(post_dict['link'])
		
		if 'can_view_comments' in post_dict.keys():
			del post_dict['can_view_comments']

		likes_list=post_dict['likes']['data']
		for like in likes_list:
			del like['profile_picture']

		#delete information about who created the post	
		del post_dict['user']

		#get status codes of images 
		images_dict=post_dict['images']
		status_code=get_resource_status_code(images_dict['low_resolution']['url'])
		images_dict['low_resolution']['status_code']=status_code
		status_code=get_resource_status_code(images_dict['thumbnail']['url'])
		images_dict['thumbnail']['status_code']=status_code
		status_code=get_resource_status_code(images_dict['standard_resolution']['url'])
		images_dict['standard_resolution']['status_code']=status_code
	except Exception as e:
		print(post_dict, file=sys.stderr)
		raise e

def case1(soup, instagram_page_dict_final, timestamp):
	m=get_portion_of_html_with_instagram_page_info(soup, timestamp)

	instagram_page_dict_temp={}
	if timestamp>=20130302000000:
		instagram_page_dict_temp=json.loads('{'+m[0]+'}')

	#get and clean user profile information
	user_profile_dict_temp=get_user_profile_dict_1(m, instagram_page_dict_temp, timestamp)
	user_profile_dict_final=clean_user_profile_dict(user_profile_dict_temp)
	instagram_page_dict_final['profileUser']=user_profile_dict_final

	#get and clean post information
	if timestamp<=20130225000000:
		posts=split_posts(m[1], timestamp)
	else:
		posts=instagram_page_dict_temp['userMedia']

	count=1
	for post_info in posts:
		print('post count:', count, file=sys.stderr)
		if timestamp<=20130225000000:
			post_dict=post_to_dict(post_info, timestamp)
		else:
			post_dict=post_info
		clean_post_dict(post_dict)
		instagram_page_dict_final['userMedia'].append(post_dict)	
		count+=1
	#return instagram_page_dict_final

#helper functions for case 2
def get_bio_and_profile_pic_uri(soup):
	meta_tags=soup.findAll('meta')
	for tag in meta_tags:
		if 'property' in tag.attrs.keys():
			if tag.attrs['property']=='og:description':
				bio=tag.attrs['content']
			if tag.attrs['property']=='og:image':
				profile_picture_uri=tag.attrs['content']
				profile_picture_status_code=get_resource_status_code(profile_picture_uri)
	return {'bio': bio, 'profile_picture':{'uri':profile_picture_uri, 'status_code': profile_picture_status_code}}

def get_website(soup):
	if soup.find('p', class_="user-bio has-bio")!=None:
		website=soup.find('p', class_="user-bio has-bio").find('a').get('href')
	else:
		website=soup.find('p', class_="user-bio").find('a').get('href')
	return website

def get_full_name(soup):
	if soup.find('p', class_="user-bio has-bio")!=None:
		full_name=soup.find('p', class_="user-bio has-bio").find('strong').contents[0]
	else:
		full_name=soup.find('p', class_="user-bio").find('strong').contents[0]
	return full_name

def get_media_followed_by_and_follows_count(soup):
	soup.find('div', class_="user-stats").find_all('li')
	for i in soup.find('div', class_="user-stats").find_all('li'):
		if 'posts' in i.contents[2]:
			media=int(i.find('span', class_='number-stat').contents[0].replace(',', ''))
		elif 'followers' in i.contents[2]:
			followed_by=int(i.find('span', class_='number-stat').get('title').replace(',', ''))
		elif 'following' in i.contents[2]:
			follows=int(i.find('span', class_='number-stat').contents[0].replace(',', ''))
	return {'media': media, 'followed_by': followed_by, 'follows': follows}

def is_verified(soup):
	if soup.find('p', class_="user-bio has-bio")!=None:
		return soup.find('p', class_="user-bio has-bio").find('span', class_="VerifiedBadge user-bio-VerifiedBadge").contents[0].strip()=='(Verified)'
	else:
		return soup.find('p', class_="user-bio").find('span', class_="VerifiedBadge user-bio-VerifiedBadge").contents[0].strip()=='(Verified)'
	
def get_links_to_posts(soup):
	post_link_dict={}
	for i in soup.find('ul', id="photo_feed").find_all('li'):
		post_id=i.find('span').get('id')
		link=i.find('a').get('href')
		post_link_dict[post_id]=link
	return post_link_dict

def get_list_of_posts(soup):
	post_list=[]
	x=get_links_to_posts(soup)
	#print(x, file=sys.stderr)
	for i in soup.findAll('script', type="text/javascript"):
		if len(i.contents)!=0 and i.contents[0].startswith('window._sharedData'):
			text=i.contents[0].rstrip(';')
			pattern=re.compile('^window._sharedData = (\{"static_root":.+)')
			m=pattern.match(text)
			count=1
			for post in json.loads(m.groups()[0])['entry_data']['ReactComponent']:
				print('post count:', count, file=sys.stderr)
				post_dict={}
				containerID=post['containerID']

				#images
				media_link=post['props']['url']
				status_code=get_resource_status_code(media_link)

				post_dict['link']=x[containerID]
				post_dict['images']={'url':media_link, 'status_code': status_code}
				if post['props']['isVideo']:
					post_dict['type']='video'
				else:
					post_dict['type']='image'
				post_list.append(post_dict)
				count+=1
			return post_list
		
def case2(soup, instagram_page_dict_final, username):
	#user profile
	profileUser={}
	profileUser['username']=username #username
	bio_and_profile_pic_dict=get_bio_and_profile_pic_uri(soup)
	profileUser['bio']=bio_and_profile_pic_dict['bio'] #bio
	profileUser['website']=get_website(soup) #website
	profileUser['profile_picture']=bio_and_profile_pic_dict['profile_picture'] #profile pic
	profileUser['full_name']=get_full_name(soup) #full_name
	profileUser['counts']=get_media_followed_by_and_follows_count(soup) #counts of posts, followers, following
	profileUser['isVerified']=is_verified(soup)
	instagram_page_dict_final['profileUser']=profileUser

	#user media
	instagram_page_dict_final['userMedia']=get_list_of_posts(soup)
	
def get_media_type(post, timestamp):
	if timestamp<20170214000000:
		if post['is_video']:
			return 'video'
		else:
			return 'image'
	else:
		if post['__typename']=='GraphVideo':
			assert post['is_video']
			return 'video'
		elif post['__typename']=='GraphImage':
			return 'image'
		elif post['__typename']=='GraphSidecar':
			return 'carousel'

def case3(soup, instagram_page_dict_final, timestamp):
	
	m=get_portion_of_html_with_instagram_page_info(soup, timestamp)
	#print(x, file=sys.stderr)
	x=json.loads(m)
	instagram_page_dict_temp=x['entry_data']['ProfilePage'][0]['user']
	
	#user profile
	profileUser={}
	profileUser['username']=instagram_page_dict_temp['username']
	profileUser['bio']=instagram_page_dict_temp['biography']
	profileUser['website']=instagram_page_dict_temp['external_url']
	profile_pic_url=instagram_page_dict_temp['profile_pic_url']
	profileUser['profile_picture']={'uri':profile_pic_url, 'status_code':get_resource_status_code(profile_pic_url)}
	profileUser['full_name']=instagram_page_dict_temp['full_name']
	media_count=instagram_page_dict_temp['media']['count']
	followed_by=instagram_page_dict_temp['followed_by']['count']
	follows=instagram_page_dict_temp['follows']['count']
	profileUser['count']={'media': media_count, 'followed_by': followed_by, 'follows': follows}
	profileUser['id']=instagram_page_dict_temp['id']
	profileUser['isVerified']=instagram_page_dict_temp['is_verified']
	instagram_page_dict_final['profileUser']=profileUser

	#user media
	count=1
	for post in instagram_page_dict_temp['media']['nodes']:
		print('post count:', count, file=sys.stderr)
		post_dict={}
		if 'comments_disabled' in post.keys():
			post_dict['comments_disabled']=post['comments_disabled']

		post_dict['comments']=post['comments']
		if 'caption' in post.keys():
			post_dict['caption']={'text': post['caption']}
		post_dict['short_code']=post['code']
		post_dict['likes']=post['likes']
		post_dict['created_time']=post['date']
		
		display_src=post['display_src']
		display_src_status_code=get_resource_status_code(post['display_src'])
		post_dict['images']={'display':{'url': display_src, 'status_code': display_src_status_code}}
		if 'thumbnail_src' in post.keys():
			if post['display_src']!=post['thumbnail_src']:
				post_dict['images']={'display':{'url': display_src, 'status_code': display_src_status_code}, 
						'thumbnail': {'url': post['thumbnail_src'], 'status_code': get_resource_status_code(post['thumbnail_src'])}}

		if 'thumbnail_resources' in post.keys():
			post_dict['thumbnail_resources']=post['thumbnail_resources']

		post_dict['type']=get_media_type(post, timestamp)

		if 'video_views' in post.keys():
			post_dict['video_views']=post['video_views']

		post_dict['id']=post['id']
		instagram_page_dict_final['userMedia'].append(post_dict)
		count+=1

def case4(soup, instagram_page_dict_final):
	m=get_portion_of_html_with_instagram_page_info(soup, timestamp)
	#print(x, file=sys.stderr)
	x=json.loads(m)
	instagram_page_dict_temp=x['entry_data']['ProfilePage'][0]['graphql']['user']
	
	#user profile
	profileUser={}
	profileUser['username']=instagram_page_dict_temp['username']
	profileUser['bio']=instagram_page_dict_temp['biography']
	profileUser['website']=instagram_page_dict_temp['external_url']
	profile_pic_url=instagram_page_dict_temp['profile_pic_url']
	profileUser['profile_picture']={'uri':profile_pic_url, 'status_code':get_resource_status_code(profile_pic_url)}
	profileUser['full_name']=instagram_page_dict_temp['full_name']
	media_count=instagram_page_dict_temp['edge_owner_to_timeline_media']['count']
	followed_by=instagram_page_dict_temp['edge_followed_by']['count']
	follows=instagram_page_dict_temp['edge_follow']['count']
	profileUser['count']={'media': media_count, 'followed_by': followed_by, 'follows': follows}
	profileUser['id']=instagram_page_dict_temp['id']
	profileUser['isVerified']=instagram_page_dict_temp['is_verified']
	#print(instagram_page_dict_temp.keys(), file=sys.stderr)
	if 'has_highlight_reel' in instagram_page_dict_temp.keys():
		#print('yay', file=sys.stderr)
		profileUser['has_highlight_reel']=instagram_page_dict_temp['has_highlight_reel']
		
	if 'highlight_reel_count' in instagram_page_dict_temp.keys():
		profileUser['highlight_reel_count']=instagram_page_dict_temp['highlight_reel_count']
	instagram_page_dict_final['profileUser']=profileUser

	#user media
	count=1
	for post in instagram_page_dict_temp['edge_owner_to_timeline_media']['edges']:
		print('post count:', count, file=sys.stderr)
		post=post['node']
		post_dict={}
		#if 'comments_disabled' in post.keys():
		post_dict['comments_disabled']=post['comments_disabled']

		post_dict['comments']=post['edge_media_to_comment']
		if len(post['edge_media_to_caption']['edges'])!=0:
			post_dict['caption']=post['edge_media_to_caption']['edges'][0]['node']
		post_dict['short_code']=post['shortcode']
		post_dict['likes']=post['edge_liked_by']
		post_dict['created_time']=post['taken_at_timestamp']
		
		display_src=post['display_url']
		display_src_status_code=get_resource_status_code(display_src)
		post_dict['images']={'display':{'url': display_src, 'status_code': display_src_status_code}}
		if 'thumbnail_src' in post.keys():
			if display_src!=post['thumbnail_src']:
				post_dict['images']={'display':{'url': display_src, 'status_code': display_src_status_code}, 
						'thumbnail': {'url': post['thumbnail_src'], 'status_code': get_resource_status_code(post['thumbnail_src'])}}

		if 'thumbnail_resources' in post.keys():
			post_dict['thumbnail_resources']=post['thumbnail_resources']

		post_dict['type']=get_media_type(post, timestamp)

		if 'video_view_count' in post.keys():
			post_dict['video_views']=post['video_view_count']

		post_dict['id']=post['id']
		instagram_page_dict_final['userMedia'].append(post_dict)
		count+=1

def get_resource_status_code(uri):
	return requests.get(uri).status_code

#not written yet
def is_on_live_instagram(uri):
	pass

def get_instagram_page_dict(soup, instagram_page_dict_final, username, timestamp):
	#before Jan 11, 2015
	if timestamp<20150111000000:
		case1(soup, instagram_page_dict_final, timestamp)
	elif 20150111000000<=timestamp<20150610000000:
		try:
			case2(soup, instagram_page_dict_final, username)
		except:
			if 20150226000000<=timestamp<20150227000000:
				case1(soup, instagram_page_dict_final, timestamp)
			else: 
				raise Exception
	elif 20150610000000<=timestamp<20180312000000:
		case3(soup, instagram_page_dict_final, timestamp)
	else:
		case4(soup, instagram_page_dict_final)


if __name__ == "__main__":
	parser=argparse.ArgumentParser()
	parser.add_argument("--urim", type=str)
	args=parser.parse_args()
	URIM=args.urim
	print(URIM, file=sys.stderr)
	pattern=re.compile('instagram.com[:80]*\/([A-Za-z0-9._]+)')
	instagram_username=pattern.findall(URIM)[0]


	pattern=re.compile('^https:\/\/web.archive.org\/web\/([0-9]+)/')
	m=pattern.match(URIM)
	timestamp=int(m.groups()[0])
	instagram_page_dict_final={'profileUser':{}, 'userMedia':[]}
	if (20130225000000 <= timestamp < 20130302000000) or (20130412000000<=timestamp<20130413000000) or (20180312000000<=timestamp<20180314000000):
		print('This timestamp has not been tested. The script may not work for this timestamp.', file=sys.stderr)
		exit()

	response = requests.get(URIM)
	html = response.text
	soup = BeautifulSoup(html, "lxml")
	#print(soup)
	get_instagram_page_dict(soup, instagram_page_dict_final, instagram_username, timestamp)
	#print(instagram_page_dict_final, file=sys.stderr)		
	#print('\u2601\uFE0F')
	#write_instagram_page_info_to_json(filename+'.json', instagram_page_dict_final)
	json.dump(instagram_page_dict_final, sys.stdout, indent=4)			
