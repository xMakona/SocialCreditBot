import datetime

# Creates a dict key using the given time and stripping any seconds or microseconds
# time parameter should be a datetime object
# delay is to add a certain number of minutes to the time key, if no delay needed just pass in 0
#
# Returns a new datetime object with the seconds/microseconds set to 0 and the delay added to the minutes
def get_time_key(time, delay=0):
    delta = datetime.timedelta(minutes=delay, seconds= -1 * time.second, microseconds= -1 * time.microsecond)
    return str(time + delta)