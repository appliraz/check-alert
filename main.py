from time import sleep
from typing import TypedDict, NotRequired
import json

import requests
from datetime import datetime
from plyer import notification


def show_notification(title: str, message: str, frequencies=None, duration = 500):
    if frequencies is None:
        frequencies = [440, 440, 440, 494, 524]

    notification.notify(title=title, message=message, timeout=120)

    try:
        import winsound
        for freq in frequencies:
            winsound.Beep(freq, duration)
    except Exception as e:
        print(e)
        import os
        sound = ''
        for freq in frequencies:
            sound = sound + f" -f {freq} -l {duration}"

        os.system(f'beep {sound}')



alert_date_string_format = "%Y-%m-%d %H:%M:%S"
ALERTS_HISTORY_URL = 'https://www.oref.org.il/warningMessages/alert/History/AlertsHistory.json'
ALERTS_URL = 'https://www.oref.org.il/warningMessages/alert/Alerts.json'

class AlertResult(TypedDict):
    city: str
    date: NotRequired[datetime]
    message: str


def fetch_last_alert(city: str) -> AlertResult | None:
    response = requests.get(ALERTS_URL)
    if response.status_code != 200 and response.status_code != 304:
        print('Nothing found', response.status_code)
        return None

    try:
        print('Got response', response.status_code)
        city_alert: AlertResult = {'city': city, 'message': ''}

        content = response.content.decode("utf-8-sig")
        content = content.strip()

        if not content:
            print('No alert found')
            return None
        else:
            print('Content length', len(content))

        alert = json.loads(content)
        print(alert)
        alert_data_message: str = alert['title']
        alert_data_cities: list[str] = alert['data']

        for data_city in alert_data_cities:
            if data_city.find(city) != -1:
                print(f'Previous message {city_alert['message']} new message {alert_data_message}')
                city_alert['message'] = alert_data_message

        if not city_alert['message']:
            print('No alert found')
            return None

        return city_alert
    except Exception as e:
        print('Failed to parse response', e)
        return None


def fetch_last_alert_history(city) -> AlertResult | None:
    # Use a breakpoint in the code line below to debug your script.
    print(f'Searching for {city}')  # Press Ctrl+F8 to toggle the breakpoint.
    print('Fetching alerts')
    response = requests.get(ALERTS_HISTORY_URL)

    if response.status_code != 200 and response.status_code != 304:
        print('Nothing found', response.status_code)
        return None

    try:
        yesterday = datetime(2026, 2, 27)
        city_alert: AlertResult = { 'city': city, 'date': yesterday, 'message': '' }
        alerts = response.json()

        for alert in alerts:
            alert_data_city: str = alert['data']
            alert_data_date_str: str = alert['alertDate']
            alert_data_message: str = alert['title']
            alert_data_date = datetime.strptime(alert_data_date_str, alert_date_string_format)

            if alert_data_city.find(city) != -1 and alert_data_date > city_alert['date']:
                print(f'Previous message {city_alert['message']} new message {alert_data_message}')
                city_alert['date'] = alert_data_date
                city_alert['message'] = alert_data_message


        if not city_alert:
            print('No alerts found')
            return None

        return city_alert
    except Exception as e:
        print('Failed to parse response', e)
        print('Terminating')
        exit(1)

if __name__ == '__main__':
    max_calls = 200
    call_no = 0
    last_alert: AlertResult | None = None

    while call_no < max_calls:
        alert_result = fetch_last_alert('ראשון לציון - מזרח')

        print(alert_result)

        if alert_result and (alert_result['message'].find('ניתן לצאת') != -1 or alert_result['message'].find('האירוע הסתיים') != -1):
            call_no += 1
            show_notification("Mamad time is over!", alert_result['message'])
            print('Done')
            exit(0)

        call_no += 1
        sleep(5)

    show_notification('Reached max calls', 'Reached max calls', [524, 524, 494], 250)
    exit(1)