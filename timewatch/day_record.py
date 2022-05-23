import datetime
import random


class DayRecord:
    day_replacers = {
        "א": "Sun",
        "ב": "Mon",
        "ג": "Tue",
        "ד": "Wed",
        "ה": "Thu",
        "ו": "Fri",
        "ש": "Sat"
    }

    dirt = "&nbsp;"
    not_working_comments = ["חופש", "מחלה"]
    rest_day = "יום מנוחה"

    def __init__(self, day_line: str):
        path, day, _, comment, hours, entry1, exit1, entry2, exit2, entry3, exit3, manual_comment, _, _, _ = day_line.split("<td align=center")
        self.reported_not_working = False
        self.reported_working = False
        self.durations = []
        self.handle_day(day)

        self.comment = self.parse_str(comment)
        self.handle_manual_comment(manual_comment)
        self.handle_path(path)
        if not self.is_rest_day:
            self.handle_required_hours(hours)
        self.handle_duration_pair(entry1, exit1)
        self.handle_duration_pair(entry2, exit2)
        self.handle_duration_pair(entry3, exit3)
        if self.durations:
            self.reported_working = True

    def __repr__(self):
        desc = f"{self.day}: "
        if self.is_rest_day:
            desc += "is a rest day. "
        else:
            desc += f"required hours: {self.hours.hour:02}:{self.hours.minute:02}. "
        if self.reported_not_working:
            desc += f"reported not working ({self.absent}). "
        if self.durations:
            desc += "Reported time durations: "
            desc += ",".join([f'{duration[0]}-{duration[1]}' for duration in self.durations])
        return desc

    def handle_day(self, day: str):
        self.day = self.parse_str(day)
        for heb_day, replace in self.day_replacers.items():
            if heb_day in self.day:
                self.day = self.day.replace(heb_day, replace)
                break

    def handle_manual_comment(self, manual_comment):
        self.absent = None
        for c in self.not_working_comments:
            if c in manual_comment:
                self.reported_not_working = True
                self.absent = c

    def handle_required_hours(self, hours: str):
        hours_str = self.parse_str(hours)
        self.hours = self.datetime_entry(hours_str.replace(" ", ""))

    def handle_path(self, path: str):
        self.jdate = path.split("jd=")[1].split("&")[0]

    def handle_duration_pair(self, entry_str: str, exit_str: str):
        entry = self.parse_entry(entry_str)
        exit = self.parse_entry(exit_str)
        if entry == self.dirt and exit == self.dirt:
            return

        if entry != self.dirt and exit != self.dirt:
            self.durations.append((entry, exit))

    def matches_required_duration(self, required_start_time: str, required_hr_dur: int):
        if not self.durations:
            return False
        start, end = self.durations[0][0], self.durations[0][1]
        if required_start_time != start:
            return False
        if (self.datetime_entry(end) - self.datetime_entry(start)).total_seconds() * 1.0/3600 < required_hr_dur:
            return False
        return True

    @property
    def is_rest_day(self):
        return self.rest_day in self.comment

    @property
    def manually_reported_day(self):
        return self.reported_working or self.reported_not_working

    @property
    def date(self):
        return self.day.split(' ')[1]

    @staticmethod
    def parse_str(st: str):
        return st.strip("</td>").replace(">", "").replace("class=mobileView", "")

    @staticmethod
    def parse_entry(en: str):
        return en.strip("</span></td>").split(">")[-1].split("<")[0]

    @staticmethod
    def datetime_entry(en: str):
        return datetime.datetime.strptime(en, '%H:%M')

    def punch_in_data(self, start_time: str, minutes_jitter: int, duration: int = 0):
        start_time = self.datetime_entry(start_time)
        jitter = random.randint(1, minutes_jitter) if minutes_jitter else 0
        end_time = start_time + datetime.timedelta(hours=duration or self.hours.hour, minutes=jitter + self.hours.minute)
        year, month, day = self.date.split("-")
        data = {'d': f"{day}-{month}-{year}",
                'jd': self.jdate,
                'nextdate': '',
                'task0': '0',
                'taskdescr0': '',
                'what0': '1',
                'emm0': f'{start_time.minute:02}', 'ehh0': f'{start_time.hour:02}',
                'xmm0': f'{end_time.minute:02}', 'xhh0': f'{end_time.hour:02}'
                }
        return data
