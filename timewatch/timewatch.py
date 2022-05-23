# coding=utf8
import requests
from enum import IntEnum
from bs4 import BeautifulSoup
import os
import time
import logging
import tqdm

from timewatch.day_record import DayRecord

try:
    strtypes = (str, unicode)
except:
    strtypes = str


class Override(IntEnum):
    work_days = 0
    all = 1
    unreported = 2

    @staticmethod
    def describe():
        return f"{Override.work_days.value}({Override.work_days.name})  - override all working days, including ones already reported, but not vacation/sick days. " \
               f"{Override.all.value}({Override.all.name}) - override all working days, including ones already reported, including vacation/sick days. " \
               f'{Override.unreported.value}({Override.unreported.name}) - override only unreported days.'


class TimeWatchException(Exception):
    pass


class TimeWatch:
    def __init__(self, loglevel=logging.WARNING, **kwargs):
        """Assigning all pre-req fields"""
        self.site = "https://c.timewatch.co.il/"
        self.edit_path = "punch/editwh3.php"
        self.days_path = "punch/editwh.php"
        self.validate_user_path = "user/validate_user.php"
        self.override = Override.unreported.value
        self.jitter = 0
        self.start_time = '10:00'
        self.duration = 0
        self.config = ['override', 'jitter', 'start_time', 'duration']

        self.company = ""
        self.employee_id = ""

        logging.basicConfig()
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(loglevel)
        self.session = requests.Session()

        self.set_config(**kwargs)

    def set_config(self, **kws):
        for key, value in kws.items():
            if key not in self.config:
                self.logger.warning(f"Skipping parameter not listed in config: {key}")

            if hasattr(self, "set_" + key):
                getattr(self, "set_" + key)(value)
            else:
                setattr(self, key, value)

            self.logger.debug(f"Set {key} = '{value}'")

    def post(self, path, data, headers=None):
        return self.session.post(os.path.join(self.site, path), data, headers or self.session.headers)

    def get(self, path, data):
        return self.session.get(os.path.join(self.site, path), params=data)

    def login(self, company, user, password):
        data = {'comp': company, 'name': user, 'pw': password}
        r = self.post(self.validate_user_path, data)
        if "התנתק" not in r.text:
            raise TimeWatchException("Login failed!")

        self.company = company
        self.employee_id = int(BeautifulSoup(r.text, 'html.parser').find('input', id='ixemplee').get('value'))
        self.logger.info(f"successfully logged in as {user}: id {self.employee_id}")
        return r

    def _parse_month(self):
        month_data = self._get_month_data(year=self.year, month=self.month)
        relevant_table_part = month_data.split("</thead>")[1].split("</tbody>")[0]
        self.csrf_token = month_data.split("csrf_token=\"")[1].split("\";")[0]
        table_lines = relevant_table_part.split("</tr>")
        return [DayRecord(l) for l in table_lines if l]

    @staticmethod
    def month_number(month):
        if isinstance(month, int):
            return month

        if isinstance(month, strtypes) and month.isdigit():
            return int(month)

        for fmt in ['%b', '%B']:
            return time.strptime(month, fmt).tm_mon

    def _get_month_data(self, month, year):
        data = {'ee': self.employee_id, 'e': self.company, 'y': year, 'm': month}
        r = self.get(self.days_path, data)
        if r.status_code != 200:
            raise TimeWatchException(f'Failed to get month {month}-{year}: {r.status_code}, {r.text}')
        return r.text

    def edit_month(self, year, month):
        self.month = self.month_number(month)
        self.year = year

        self.logger.info(f'Month: {month} - parsing dates to operate on')
        day_records = self._parse_month()
        for day in day_records:
            self.logger.info(repr(day))

        self.logger.info(f'Month: {self.month}, Override: {self.override} ({Override(self.override).name}) - punching')
        if self.override == Override.all.value:
            days_to_update = [day for day in day_records if not day.is_rest_day]
        elif self.override == Override.work_days.value:
            days_to_update = [day for day in day_records if not day.is_rest_day and not day.reported_not_working]
        elif self.override == Override.unreported.value:
            days_to_update = [day for day in day_records if not day.is_rest_day and not day.manually_reported_day]
        else:
            raise RuntimeError()

        self.session.headers.update({
            'Content-Type': "application/x-www-form-urlencoded; charset=UTF-8",
            'referer': f"{self.site}{self.days_path}?month={self.month}&year={self.year}&teamldr={self.employee_id}&empl_name={self.company}"
        })

        self._punch_in_list_of_days(days_to_update)
        self._verify_update_days(days_to_update)

    def _verify_update_days(self, days_to_update):
        missing_days = []
        current_days = self._parse_month()
        date_to_day_record = {day.day: day for day in current_days}
        for day_record in days_to_update:
            current_day = date_to_day_record[day_record.day]
            if not current_day.matches_required_duration(required_start_time=self.start_time, required_hr_dur=self.duration):
                missing_days.append(current_day)
        if missing_days:
            self.logger.warning(f'repeating dates: {[day.day for day in missing_days]}')
            self._punch_in_list_of_days(missing_days)
            self._verify_update_days(missing_days)
        if not missing_days:
            self.logger.info(f'finished punching in {self.month}-{self.year}')
            for day in current_days:
                self.logger.info(repr(day))

    def _punch_in_list_of_days(self, days_to_update):
        for day in tqdm.tqdm(days_to_update):
            day_data = day.punch_in_data(start_time=self.start_time, minutes_jitter=self.jitter, duration=self.duration)
            day_data.update({'e': str(self.employee_id), 'tl': str(self.employee_id), 'c': str(self.company), 'csrf_token': self.csrf_token})
            r = self.post(self.edit_path, day_data)
            if r.status_code != 200 or r.text != '0':
                raise TimeWatchException(f'Failed to update day {day.day}: {r.status_code}, {r.text}. Request data: {day_data}')
            time.sleep(.1)
