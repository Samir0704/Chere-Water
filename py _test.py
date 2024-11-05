from datetime import datetime

today = datetime.now()
day_of_year = today.timetuple().tm_yday

print(f"Today is day {day_of_year} of the year.")