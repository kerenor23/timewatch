## timewatch

Tired of reporting work hours every day/month?
Your boss trusts you with your time, but HR demands you fill timewatch's form?
You're too preoccupied with work, and forget filling up timewatch.co.il?

We've all been there, just set up a monthly timewatch cron and get back to work!

### What is this?
This script automatically sets default working hours for all work days using timewatch.co.il's web interface.
It reads expected work hours for each day and automatically sets each day's work to that amount.
It is therefor handling govt. off days and weekends, and is quite configurable.

## Usage
To report required working hours for the current month, simply execute
```./main.py <company id> <employee number> <password>```

### Full usage and functionality

```
usage: main.py [-h] [-y YEAR] [-m MONTH] [-v] [-o {0,1,2}] [-s START_TIME]
               [-j JITTER] [-d DURATION]
               company user password

Automatic work hours reporting for timewatch.co.il

positional arguments:
  company               Company ID
  user                  user name/id
  password              user password

optional arguments:
  -h, --help            show this help message and exit
  -y YEAR, --year YEAR  Year number to fill
  -m MONTH, --month MONTH
                        Month number or name
  -v, --verbose         increase logging level
  -o {0,1,2}, --override {0,1,2}
                        Control override behavior: work_days: 0,all:
                        1,unreported: 2. 1 - override all working days,
                        including ones already reported. unsafe to
                        vacation/sick days. 0 - override all working days,
                        including ones already reported, but keep vacation /
                        sick days2 - override only unreported days
  -s START_TIME, --start_time START_TIME
                        punch-in time
  -j JITTER, --jitter JITTER
                        punching time random range in minutes.
  -d DURATION, --duration DURATION
                        hours duration (override preset edfault)
```

### Installation

```
git clone https://github.com/kerenor23/timewatch.git
cd timewatch
pip3 install -r requirements.txt
python3 ./setup.py bdist_wheel
pip3 install ./dist/*
cd timewatch
./main.py <args>
```

Not on pypi or anywhere :P
