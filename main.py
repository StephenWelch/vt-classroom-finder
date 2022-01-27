import json
from typing import Dict, List
import requests as rq
from bs4 import BeautifulSoup
import selenium.webdriver
from selenium.webdriver.firefox.options import Options

CURRENT_TERM_NAME = 'Spring 2022'
CURRENT_TERM_ID = '202201'
MAIN_PAGE = 'http://info.classroomav.vt.edu/RoomSchedule.aspx'
HEADERS = {
'Connection': 'keep-alive',
# 'Accept': 'application/json, text/javascript, */*; q=0.01',
# 'DNT': '1',
'X-Requested-With': 'XMLHttpRequest',
'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36',
'Content-Type': 'application/json; charset=UTF-8',
'Origin': 'http://info.classroomav.vt.edu',
'Referer': 'http://info.classroomav.vt.edu/RoomSchedule.aspx',
'Accept-Language': 'en-US,en;q=0.9',
'Cookie': 'AMCV_4F173DF05A373EBF0A495E41%40AdobeOrg=MCMID%7C86084811541373255674014950237213292543; nlid=3b46a01|45af2f8; ASP.NET_SessionId=e42x35vnyi0iuihbudfmyeej'
}
SESSION = rq.session()

def get_rooms(building_code: str, show_ga_rooms: bool=True, term_id: str=CURRENT_TERM_ID) -> Dict[str, str]:
    r = SESSION.post('http://info.classroomav.vt.edu/RoomScheduleAjax.aspx/GetRooms', 
    json={
        'buildingCode': building_code,
        'showGARooms': show_ga_rooms,
        'selectedTerm': term_id
    })
    if 'application/json' not in r.headers.get('Content-Type'):
        print(f"Received non-JSON response from server:\n{r.text}")
        return {}
    else:
        return [ d for d in r.json()['d'] if d['Value'] ]

def get_room_schedule(building_code: str, building_name: str, room_num: str, schedule: str, show_events: bool, show_past_events: bool, term_id: str=CURRENT_TERM_ID, term_name: str=CURRENT_TERM_NAME) -> Dict[str, str]:
    # headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    r = SESSION.post('http://info.classroomav.vt.edu/RoomScheduleAjax.aspx', 
    # headers=headers,
    json={
        'buildingCode': building_code,
        'buildingName': building_name,
        'roomNumber': room_num,
        'termID': term_id,
        'termName': term_name,
        'schedule': schedule,
        'showEvents': str(show_events).lower(),
        'showPastEvents': str(show_past_events).lower()
    })
    if 'text/html' not in r.headers.get('Content-Type'):
        print(f"Received non-HTML response from server:\n{r.text}")
        return {}
    else:
        return r.text

def print_all_rooms(buildings: List[Dict[str, str]]):
    for b in buildings:
        rooms = get_rooms(b['Value'])
        print(f"{b['Display']}:\n")
        for r in rooms:
            print(f"{r['Display']}\n")

def main():
    # Grab cookie from the browser for use in requests
    options = Options()
    options.headless = True
    web_drv = selenium.webdriver.Firefox(options=options, executable_path='./geckodriver')
    web_drv.get(MAIN_PAGE)
    SESSION.headers.update(HEADERS)

    headers = web_drv.execute_script("var req = new XMLHttpRequest();req.open('GET', document.location, false);req.send(null);return req.getAllResponseHeaders()")
    print(headers)

    # for cookie in web_drv.get_cookies():
    #     # if 'sameSite' in cookie:
    #     #     cookie['samesite'] = cookie.pop('sameSite')
    #     cookie.pop('sameSite')
    #     if 'httpOnly' in cookie:
    #         httpO = cookie.pop('httpOnly')
    #         cookie['rest'] = {'httpOnly': httpO}
    #     if 'expiry' in cookie:
    #         cookie['expires'] = cookie.pop('expiry')
    #     SESSION.cookies.set(**cookie)
    # for c in SESSION.cookies:
    #    print(c)
        
    main_form = rq.get(MAIN_PAGE)
    main_form_page = BeautifulSoup(main_form.content, "html.parser")
    building_dropdown = main_form_page.find(id='PageBody_lstBuildings')
    buildings = [{'Value': o['value'], 'Display': o.text } for o in building_dropdown.find_all('option')]

    print(get_rooms('NCB'))
    print(get_room_schedule('NCB', 'New Classroom Building', '160', 'today', True, False))

    ...

if __name__ == '__main__':
    main()