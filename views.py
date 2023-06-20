import requests
from bs4 import BeautifulSoup
from datetime import date, datetime
from django.http import JsonResponse


def get_holidays(request, start_date: str, stop_date: str) -> JsonResponse:
    try:
        start_date = datetime.strptime(start_date, '%d-%m-%Y').date()
        stop_date = datetime.strptime(stop_date, '%d-%m-%Y').date()
    except ValueError:
        return JsonResponse({'date format error': 'dates format mus be like 25-6-1986'})

    def parse_holiday_dates(start_date, stop_date):
        months_translation = {
            'Январь': 1,
            'Февраль': 2,
            'Март': 3,
            'Апрель': 4,
            'Май': 5,
            'Июнь': 6,
            'Июль': 7,
            'Август': 8,
            'Сентябрь': 9,
            'Октябрь': 10,
            'Ноябрь': 11,
            'Декабрь': 12
        }

        holiday_dates = []
        start_year = start_date.year
        stop_year = stop_date.year
        years = range(start_year, stop_year + 1)

        if start_year == stop_year:
            years = [start_year]

        # FIXME: что будет, если год окончания меньше года старта?

        for year in years:
            url = f"https://www.consultant.ru/law/ref/calendar/proizvodstvennye/{year}"
            response = requests.get(url)

            if response.status_code != 200:
                raise requests.exceptions.HTTPError(
                    "Не удалось получить список праздников, "
                    f"www.consultant.ru вернул код {response.status_code}"
                )

            html_content = response.text
            soup = BeautifulSoup(html_content, 'html.parser')
            tables = soup.find_all('table', {'class': 'cal'})

            for table in tables:
                month = table.find('th', {'class': 'month'}).text.strip()
                td_elements = table.find_all('td', {'class': 'holiday'})
                holidays = [int(td_element.get_text()) for td_element in td_elements]

                month_number = months_translation.get(month)
                if month_number:
                    holiday_dates.extend(
                        date(year, month_number, day) for day in holidays
                        if start_date <= date(year, month_number, day) <= stop_date
                    )

        return holiday_dates

    holiday_dates = parse_holiday_dates(start_date, stop_date)
    holiday_dates_str = [str(dt) for dt in holiday_dates]

    return JsonResponse({'holidays not on weekends': holiday_dates_str})
