import urllib2
import cookielib
import urllib
import re
import pprint
import os
import sys

sys.path.append('c:\\Users\\fabriciols\\Desktop\\fabriciols')
os.environ['DJANGO_SETTINGS_MODULE'] ='ps3t.settings'


from django.core.management import setup_environ
from ps3t import settings
#settings.DATABASE_NAME = os.path.join( project_dir, settings.DATABASE_NAME )
setup_environ(settings)
import ps3t.myps3t.models as db

project_dir = os.path.abspath('../') # or path to the dir. that the db should be in.

hh = urllib2.HTTPHandler()
hsh = urllib2.HTTPSHandler()
hh.set_http_debuglevel(0)
hsh.set_http_debuglevel(0)


#cj = cookielib.LWPCookieJar()
opener = urllib2.build_opener(hh, hsh)

def get_user_info(user):

	URL = "http://profiles.us.playstation.com/playstation/psn/profiles/%s" %user

	request = urllib2.Request(URL)

	request.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 6.1; pt-BR; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5 (.NET CLR 3.5.30729)')
	request.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')
	request.add_header('Accept-Language', 'pt-br,pt;q=0.8,en-us;q=0.5,en;q=0.3')
	request.add_header('Accept-Charset', 'ISO-8859-1,utf-8;q=0.7,*;q=0.7')
	request.add_header('Keep-Alive', '300')
	request.add_header('Connection', 'keep-alive')

	br = opener.open(request)

	ER_USER_AVATAR = re.compile('.*<img width="57" height="57" border="0" alt="" src="(?P<user_avatar>.*.png)"/>.*')
	ER_USER_LEVEL  = re.compile('.*<div id="leveltext"> (?P<user_level>[0-9]{1,})</div>.*')
	ER_USER_PERC   = re.compile('    (?P<perc_level>[0-9]{1,})%')
	ER_USER_TOTAL  = re.compile('.*<center>(?P<total>[0-9]{1,})</center>')
	ER_USER_PLAT   = re.compile('.*<div class="text platinum">(?P<plat>[0-9]{1,}) Platinum</div>.*')
	ER_USER_GOLD   = re.compile('.*<div class="text gold">(?P<gold>[0-9]{1,}) Gold</div>.*')
	ER_USER_SILVER = re.compile('.*<div class="text silver">(?P<silver>[0-9]{1,}) Silver</div>.*')
	ER_USER_BRONZE = re.compile('.*<div class="text bronze">(?P<bronze>[0-9]{1,}) Bronze</div>.*')

	USER_DICT = {}
	
	for i in br.readlines():

		if ER_USER_AVATAR.match(i):
			USER_DICT["avatar_url"] = ER_USER_AVATAR.search(i).group('user_avatar')
			continue

		if ER_USER_LEVEL.match(i):
			USER_DICT["level"] = int(ER_USER_LEVEL.search(i).group('user_level'))
			continue

		if ER_USER_PERC.match(i):
			USER_DICT["perc"] = int(ER_USER_PERC.search(i).group('perc_level'))
			continue

		if ER_USER_TOTAL.match(i):
			USER_DICT["total"] = int(ER_USER_TOTAL.search(i).group('total'))
			continue

		if ER_USER_PLAT.match(i):
			USER_DICT["plat"] = int(ER_USER_PLAT.search(i).group('plat'))
			continue

		if ER_USER_GOLD.match(i):
			USER_DICT["gold"] = int(ER_USER_GOLD.search(i).group('gold'))
			continue

		if ER_USER_SILVER.match(i):
			USER_DICT["silver"] = int(ER_USER_SILVER.search(i).group('silver'))
			continue

		if ER_USER_BRONZE.match(i):
			USER_DICT["bronze"] = int(ER_USER_BRONZE.search(i).group('bronze'))
			break

	return USER_DICT

def get_user_games_list(user):

	URL = "http://profiles.us.playstation.com/playstation/psn/profile/%s/get_ordered_trophies_data" %user

	request = urllib2.Request(URL)

	request.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 6.1; pt-BR; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5 (.NET CLR 3.5.30729)')
	request.add_header('Accept', 'text/javascript, text/html, application/xml, text/xml, */*')
	request.add_header('Accept-Language', 'pt-br,pt;q=0.8,en-us;q=0.5,en;q=0.3')
	request.add_header('Accept-Charset', 'ISO-8859-1,utf-8;q=0.7,*;q=0.7')
	request.add_header('Keep-Alive', '300')
	request.add_header('Connection', 'keep-alive')
	request.add_header('X-Requested-With', 'XMLHttpRequest')
	request.add_header('X-Prototype-Version', '1.6.1_rc3')
	request.add_header('Referer', 'http://profiles.us.playstation.com/playstation/psn/profiles/%s' %user) 

	br = opener.open(request)

	ER_GAME_ID   = re.compile(' {10}<a href="/playstation/psn/profiles/%s/trophies/(?P<game_id>.*)">.*' %user)
	ER_GAME_NAME = re.compile('.*<span class="gameTitleSortField">(?P<game_name>.*)</span>.*')
	ER_GAME_PIC  = re.compile('.*<img border="0" alt="" src="(?P<game_pic>http://.*.np.community.playstation.net/trophy/np/.*.PNG)"/>')
	ER_GAME_PERC = re.compile('.*<span class="gameProgressSortField">(?P<game_perc>[0-9]*)</span>%.*')
	ER_GAME_TOTAL= re.compile('.*<span class="gameTrophyCountSortField">(?P<game_total>[0-9]*).*')
	ER_GAME_TROPH= re.compile(' *(?P<game_trophy>[0-9]{1,})$')

	total = 0

	GAME_LIST = []
	GAME_DICT = {}
			 
	for i in br.readlines():
		if ER_GAME_NAME.match(i):
			GAME_DICT["name"] = ER_GAME_NAME.search(i).group('game_name')

		if ER_GAME_ID.match(i):

			if len(GAME_DICT) > 0:
				GAME_LIST.append(GAME_DICT)
				GAME_DICT = {}

			GAME_DICT["id"] = ER_GAME_ID.search(i).group('game_id')
			continue

		if ER_GAME_PIC.match(i):
			GAME_DICT["pic_url"] = ER_GAME_PIC.search(i).group('game_pic')
			continue

		if ER_GAME_PERC.match(i):
			GAME_DICT["perc_done"] = ER_GAME_PERC.search(i).group('game_perc')
			continue

		if ER_GAME_TOTAL.match(i):
			GAME_DICT["trophy_total"] = ER_GAME_TOTAL.search(i).group('game_total')
			total = 1
			continue

		if total > 0:

			if ER_GAME_TROPH.match(i):

				game_trophy = ER_GAME_TROPH.search(i).group('game_trophy')

				if total is 1:
					GAME_DICT["trophy_bronze"] = game_trophy
				elif total is 2:
					GAME_DICT["trophy_silver"] = game_trophy
				elif total is 3:
					GAME_DICT["trophy_gold"] = game_trophy
				elif total is 4:
					GAME_DICT["trophy_platinum"] = game_trophy
					total = 0

				if total is not 0:
					total += 1

	if len(GAME_DICT) > 0:
		GAME_LIST.append(GAME_DICT)

	return GAME_LIST

def get_user_game_info(user, game):

	values = { 'sortBy' : 'id_asc' ,
	'titleId': game}

	data = urllib.urlencode(values)

	URL="http://profiles.us.playstation.com/playstation/psn/profile/%s/get_ordered_title_details_data" %user

	request = urllib2.Request(URL, data)

	request.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 6.1; pt-BR; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5 (.NET CLR 3.5.30729)')
	request.add_header('Accept', 'text/javascript, text/html, application/xml, text/xml, */*')
	request.add_header('Accept-Language', 'pt-br,pt;q=0.8,en-us;q=0.5,en;q=0.3')
	request.add_header('Accept-Charset', 'ISO-8859-1,utf-8;q=0.7,*;q=0.7')
	request.add_header('Keep-Alive', '300')
	request.add_header('Connection', 'keep-alive')
	request.add_header('X-Requested-With', 'XMLHttpRequest')
	request.add_header('X-Prototype-Version', '1.6.1_rc3')
	request.add_header('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8')
	request.add_header('Referer', 'http://profiles.us.playstation.com/playstation/psn/profiles/%s/trophies/%s' %(user, game))
	request.add_header('Content-Length', '40')

	page = opener.open(request)

	ER_TROPHY_NAME =   re.compile('.*<span class="trophyTitleSortField">(?P<trophy_name>.*)</span>.*')
	ER_TROPHY_DETAIL = re.compile('.*<span class="subtext">(?P<trophy_detail>.*)</span>.*')
	ER_TROPHY_DATE   = re.compile('.*<span class="dateEarnedSortField" style="display:none">(?P<trophy_date>.*)</span>.*')
	ER_TROPHY_TYPE   = re.compile('.*<span class="trophyTypeSortField" style="display:none">.*')
	ER_TROPHY_TYPE_2 = re.compile(' *[BSGH].*')

	j=0

	type = 0

	TROPHY_LIST = []
	TROPHY_DICT = {}
	
	for i in page.readlines():
		if ER_TROPHY_NAME.match(i):

			if len(TROPHY_DICT) > 0:
				TROPHY_LIST.append(TROPHY_DICT)
				TROPHY_DICT = {}
				
			TROPHY_DICT["id"]   = j
			TROPHY_DICT["name"] = ER_TROPHY_NAME.search(i).group('trophy_name')
			j += 1
			continue

		if ER_TROPHY_DETAIL.match(i):
			TROPHY_DICT["detail"] = ER_TROPHY_DETAIL.search(i).group('trophy_detail')
			continue

		if ER_TROPHY_DATE.match(i):
			TROPHY_DICT["date"] = ER_TROPHY_DATE.search(i).group('trophy_date')
			continue

		if ER_TROPHY_TYPE.match(i):
			type = 1
			continue

		if type == 1:
			if ER_TROPHY_TYPE_2.match(i):
				TROPHY_DICT["type"] = i.replace(' ','')[:-1]
				type = 0

				if TROPHY_DICT["type"] == "HIDDEN":
					TROPHY_DICT["id"]   = j
					TROPHY_LIST.append(TROPHY_DICT)
					TROPHY_DICT = {}
					j += 1

	#pprint.pprint(TROPHY_LIST)

	return TROPHY_LIST
				
USER='fabriciols'

USER_INFO      = get_user_info(USER)
GAME_USER_LIST = get_user_games_list(USER)

db.gamesInfo.objects.all()

for game in GAME_USER_LIST:
	pprint.pprint(game)
	game = db.gamesInfo(psn_id = game["id"],
						       name = game["name"],
						    pic_url = game["pic_url"])

	game.save()

pprint.pprint(USER_INFO)
#pprint.pprint(GAME_USER_LIST)