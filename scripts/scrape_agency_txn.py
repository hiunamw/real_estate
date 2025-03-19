import requests
import pandas as pd
from datetime import datetime, timedelta

def get_cenTxn(n, type, days, by, codes, cookies, headers):
    # n = {no. of txn}
    # type = Sale / Rent
    # days = 30, 90, 180, 365, 1095
    # by = Area / Property (MTR, School Net?)
    # codes = [{code(s)}]

    data = []
    for i in range(0, n, 50):
        json_data = {
            'postType': type,
            'firstOrSecondHand': ['SecondHand'],
            'estateUsages': ['RE'],
            'day': f'Day{days}',
            'sort': 'InsOrRegDate',
            'order': 'Descending',
            'size': 50,
            'offset': i,
            'pageSource': 'search'
        }

        if by == 'Area':
            json_data['typeCodes'] = codes
        elif by == 'Property':
            json_data['bigestAndEstate'] = codes

        response = requests.post(
            'https://hk.centanet.com/findproperty/api/Transaction/Search',
            cookies=cookies,
            headers=headers,
            json=json_data,
        )

        data.extend(response.json()['data'])

    temp = []
    for txn in data:
        prop_id = txn['typeCode']
        try:
          date = txn['regDate'][:10]
        except:
          date = txn['insDate'][:10]
        district = txn['districtName']
        _property = txn['bigEstateName']
        phase = txn['estateName']
        tower = txn['buildingName']
        floor = txn['yAxis']
        unit = txn['xAxis']
        try:
            sfa = txn['nArea']
        except:
            sfa = '-'
        price = txn['transactionPrice']
        try:
            br = txn['bedroomCount']
            if br == 0:
                br = 'Studio'
            else:
                br = f'{br}BR'
        except:
            br = '-'
        source = txn['dataSource']

        temp.append(
            {
                'Date': date,
                'District': district,
                'Prop_ID': prop_id,
                'Property': _property,
                'Phase': phase,
                'Tower': tower,
                'Floor': floor,
                'Unit': unit,
                'SFA': sfa,
                'Price': price,
                'BR': br,
                'Source1': 'Centanet',
                'Source2': source
            }
        )

    return pd.DataFrame(temp)

def get_midTxn(n, type, days, by, codes, cookies, headers):
    # n = {no. of txn}
    # type = S / L
    # days = 30, 90, 180, 365, 1095
    # by = Area / Property (MTR, School Net?)
    # codes = [{code(s)}]

    if days > 180:
        period = f'{int(days/365)}year'
    else:
        period = f'{days}days'

    if len(codes) == 1:
        params = {
            'ad': 'true',
            'hash': 'true',
            'chart': 'true',
            'lang': 'en',
            'currency': 'HKD',
            'unit': 'feet',
            'search_behavior': 'normal',
            'tx_type': type,
            'mkt_type': '2',
            'tx_date': period,
            'type': 'private',
            'page': '1',
            'limit': f'{n}',
        }

        if by == 'Area':
            params['intsmdist_ids'] = codes[0]
        elif by == 'Property':
            params['est_ids'] = codes[0]

        response = requests.get('https://data.midland.com.hk/search/v2/transactions', params=params, headers=headers)

    else:
        if by == 'Area':
            code_param = f'intsmdist_ids={",".join(codes)}'
        elif by == 'Property':
            code_param = f'est_ids={",".join(codes)}'

        response = requests.get(
            'https://data.midland.com.hk/search/v2/transactions?ad=true&hash=true&chart=true&lang=en&currency=HKD&unit=feet&search_behavior=normal&' + code_param + f'&tx_type={type}&tx_date={period}&type=private&page=1&limit={n}',
            headers=headers,
        )

    data = response.json()['result']

    temp = []
    for txn in data:
        try:
            date = str((datetime.strptime(txn['tx_date'][:10], '%Y-%m-%d')+timedelta(days=1)).date())
            district = txn['int_sm_district']['name']
            _property = txn['estate']['name']
            try:
                phase = txn['phase']['name']
            except:
                phase = '-'
            tower = txn['building']['name']
            try:
                floor = txn['floor']
            except:
                floor = txn['floor_level']['name']
            unit = txn['flat']
            sfa = txn['net_area']
            price = txn['price']
            br = txn['bedroom']
            if br == '0':
                br = 'Studio'
            else:
                br = f'{br}BR'
            source = txn['source']

        except:
            pass

        temp.append(
            {
                'Date': date,
                'District': district,
                'Property': _property,
                'Phase': phase,
                'Tower': tower,
                'Floor': floor,
                'Unit': unit,
                'SFA': sfa,
                'Price': price,
                'BR': br,
                'Source1': 'Midland',
                'Source2': source
            }
        )

    return pd.DataFrame(temp)
