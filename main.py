import json
from typing import Dict, List
import requests as rq
from bs4 import BeautifulSoup
import selenium.webdriver
from selenium.webdriver.firefox.options import Options
import pandas as pd
import numpy as np

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
# 'Cookie': 'AMCV_4F173DF05A373EBF0A495E41%40AdobeOrg=MCMID%7C86084811541373255674014950237213292543; nlid=3b46a01|45af2f8; ASP.NET_SessionId=e42x35vnyi0iuihbudfmyeej'
}
SESSION = rq.session()

def get_buildings(excluded_values: List[str] = []) -> List[Dict[str, str]]:
    main_form = rq.get(MAIN_PAGE)
    main_form_bs = BeautifulSoup(main_form.content, "html.parser")
    building_dropdown_bs  = main_form_bs.find(id='PageBody_lstBuildings')
    buildings = []
    for o in building_dropdown_bs.find_all('option'):
        if o['value'] not in excluded_values:
            buildings.append({
                'Value': o['value'], 
                'Display': o.text
            })
    return buildings

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
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    r = SESSION.post('http://info.classroomav.vt.edu/RoomScheduleAjax.aspx', 
    headers=headers,
    data={
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

def parse_full_schedule_table(html: str, id: str) -> pd.DataFrame:
    ...

def parse_full_schedule(html: str) -> pd.DataFrame:
    ...

def parse_daily_schedule_table(html: str, id: str) -> pd.DataFrame:
    schedule_bs = BeautifulSoup(html, "html.parser")

    table_bs = schedule_bs.find('div', {'class': 'DailyTable'}, id=id)
    table_rows_bs = table_bs.find_all('div', {'class':'TableRow'})

    table_headers: List[str] = []
    rows: List[pd.Series] = []
    for table_row_bs in table_rows_bs:
        header_cells = table_row_bs.find_all('div', {'class':'TableCellHeader'})
        if header_cells:
            [table_headers.append(h.text) for h in header_cells]
        else:
            time_cell = table_row_bs.find('div', {'class':'DailyTableCellTime'})
            data_cell = table_row_bs.find('div', {'class':'DailyTableCell'})
            rows.append(pd.Series([time_cell.text, data_cell.text]))

    daily_schedule_df = pd.DataFrame(rows)
    daily_schedule_df.columns = table_headers
    return daily_schedule_df

def parse_daily_schedule(html: str) -> pd.DataFrame:
    class_schedule_df = parse_daily_schedule_table(html, 'DailyClassScheduleTable')
    event_schedule_df = parse_daily_schedule_table(html, 'DailyEventScheduleTable')
    return pd.concat([class_schedule_df, event_schedule_df], axis=0)

def print_all_rooms(buildings: List[Dict[str, str]]):
    for b in buildings:
        rooms = get_rooms(b['Value'])
        print(f"{b['Display']}:\n")
        for r in rooms:
            print(f"{r['Display']}\n")

def main():
    # Grab cookie from the browser for use in requests
    options = Options()
    # options.headless = True
    # web_drv = selenium.webdriver.Firefox(options=options, executable_path='./geckodriver')
    options.binary_location = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
    web_drv = selenium.webdriver.Chrome(options=options)
    web_drv.get(MAIN_PAGE)
    SESSION.headers.update(HEADERS)
        
    buildings = get_buildings(excluded_values=['GYM', 'NVC'])

    empty_count = 0
    for b in buildings:
        rooms = get_rooms(b['Value'])
        print(f"{b['Display']}:")
        for r in rooms:
            room_schedule = get_room_schedule(b['Value'], b['Display'], r['Value'], 'today', True, False)
            room_schedule_df = parse_daily_schedule(room_schedule)
            if room_schedule_df.empty:
                print(f"{b['Value']} {r['Display']}")
                empty_count += 1
        print("")
    print(f"There are {empty_count} empty rooms at VT")
 

    ...

if __name__ == '__main__':
    main()