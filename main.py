from typing import Dict
import requests as rq
from bs4 import BeautifulSoup
import selenium.webdriver
from selenium.webdriver.firefox.options import Options


CURRENT_TERM: str = '202201'
MAIN_PAGE = 'http://info.classroomav.vt.edu/RoomSchedule.aspx'
HEADERS = {
"User-Agent":
    "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"
}
SESSION = rq.session()

def get_rooms(building_code: str, show_ga_rooms: bool=True, term: str=CURRENT_TERM) -> Dict[str, str]:
    r = SESSION.post('http://info.classroomav.vt.edu/RoomScheduleAjax.aspx/GetRooms', 
    params={
        'buildingCode': building_code,
        'showGARooms': show_ga_rooms,
        'selectedTerm': term
    })
    if r.headers.get('content-type') != 'application/json':
        print(f"Received non-JSON response from server: {r.text}")
        return {}
    else:
        return r.json()

def main():
    # Grab cookie from the browser for use in requests
    options = Options()
    # options.headless = True
    # web_drv = selenium.webdriver.Firefox(options=options, executable_path='./geckodriver')
    options.binary_location = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
    web_drv = selenium.webdriver.Chrome(options=options)
    web_drv.get(MAIN_PAGE)
    SESSION.headers.update(HEADERS)
    # SESSION.headers['referer'] = MAIN_PAGE

    for c in web_drv.get_cookies():
        SESSION.cookies.update(c)
    for c in SESSION.cookies:
        print(c)
        
    main_form = rq.get(MAIN_PAGE)
    main_form_page = BeautifulSoup(main_form.content, "html.parser")
    building_dropdown = main_form_page.find(id='PageBody_lstBuildings')
    # buildings = [(o['value'], o.text) for o in building_dropdown.find_all('option')]

    # print(buildings)
    print(get_rooms('NEW'))
    ...

if __name__ == '__main__':
    main()