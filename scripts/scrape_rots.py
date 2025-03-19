import dateutil.parser
import numpy as np
import os
import pandas as pd
import random
import re
import tabula
import time
from datetime import datetime
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

def web_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--verbose")
    options.add_argument('--no-sandbox')
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920, 1200')
    options.add_argument('--disable-dev-shm-usage')

    options.add_experimental_option('prefs', {
        "download.default_directory": "/content/PDFs", # Change default directory for downloads
        "download.prompt_for_download": False, # To auto download the file
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True # It will not show PDF directly in chrome
    })

    driver = webdriver.Chrome(options=options)
    return driver

def get_rotUrls(n=8):
    rot_urls = []

    driver = web_driver()
    driver.get('https://www.srpe.gov.hk/opip/disclaimer_newly_upload_sales_brochure_price_list.htm')
    driver.find_element(By.CLASS_NAME, 'checkbox').click()
    driver.find_element(By.ID, 'continueBtn').click()
    driver.find_element(By.ID, 'search_sales_brochure_check').click()
    driver.find_element(By.ID, 'search_price_list_check').click()
    driver.find_element(By.ID, 'search_sales_arrangement_check').click()
    driver.execute_script("arguments[0].style.display = 'block';", driver.find_element(By.ID, 'transactions_day_chooser'))
    select = Select(driver.find_element(By.ID, 'transactions_day_chooser'))
    select.select_by_value(f'{n}')
    driver.find_element(By.ID, 'submitBtn').click()

    rows = driver.find_element(By.ID, 'display_3_2').find_element(By.TAG_NAME, 'tbody').find_elements(By.TAG_NAME, 'tr')
    for row in rows:
      cols = row.find_elements(By.TAG_NAME, 'td')
      rot_urls.append(cols[0].find_element(By.TAG_NAME, 'a').get_attribute('href'))

    driver.quit()
    df = pd.DataFrame(rot_urls, columns=['rot_url'])
    df['prop_id'] = df['rot_url'].apply(lambda x: x.split('devId=')[-1])

    print(f'No. of Properties: {len(df)}')
    return df

def download_rot(df, pdf_path):
    prop_names = []
    pdf_codes = []

    for i in range(len(df)):
        prop_id = df.iloc[i]["prop_id"]
        prop_name = df.iloc[i]["property"]
        print(f'Downloading ROT of {prop_name}... ({i+1}/{len(df)})')

        max_errors = 4
        errors = 0
        while True:
            try:
              driver = web_driver()
              driver.get('https://www.srpe.gov.hk/opip/disclaimer_for_year_of_first_printing_of_sale_brochure.htm')
              driver.find_element(By.CLASS_NAME, 'checkbox').click()
              driver.find_element(By.ID, 'continueBtn').click()
              driver.find_element(By.ID, 'submitBtn').click()
              driver.get(f"https://www.srpe.gov.hk/opip/selected_dev_by_year_of_sb.htm?devId={prop_id}")
              pdf_ele = driver.find_element(By.ID, 'transaction')
              break
            except NoSuchElementException:
              errors += 1
              print(f'Failed: {errors}')
              time.sleep(5)
              if errors > max_errors:
                  raise NoSuchElementException

        pdf_url = pdf_ele.find_element(By.TAG_NAME, 'a').get_attribute('href')
        date_ele = pdf_ele.find_element(By.CLASS_NAME, "engFont").text
        print(f'---------- Last updated on {date_ele} ----------')
        driver.get(pdf_url)

        prop_names.append(f"{prop_name}_{datetime.strptime(date_ele, '%d %b %Y %I:%M %p').strftime('%Y%m%d%H%M')}")
        pdf_codes.append(pdf_url.split("/")[-1][:-4])

        time.sleep(random.randint(1, 3))

    time.sleep(10)

    for new_name, old_name in dict(zip(prop_names, pdf_codes)).items():
        try:
            os.rename(f'{pdf_path}/{old_name}.PDF', f'{pdf_path}/{new_name}.pdf')
        except FileNotFoundError:
            pass

    return prop_names, pdf_codes

def extract_rots(pdf_path, pdf):
    df_list1 = []
    df_list2 = []

    dfs = tabula.read_pdf(f'{pdf_path}/{pdf}', pages='all', silent=True)
    cols = ['(A)', '(B)', '(C)', '(D)', '(E)', '(F)', '(G)', '(H)', '(I)', '(J)']

    for df in dfs:
        col_length = len(df.columns)
        if col_length == 11:
            df_list1.append(df)
        elif col_length == 8:
            df_list2.append(df)

    if df_list1:
        try:
            df1 = pd.concat(df_list1)
            df1 = df1[df1['(A)'].str.contains('20', na=False)]
            df1.rename(columns={'Unnamed: 0': '(I)', 'Unnamed: 1': '(J)'}, inplace=True)
            df1 = df1[cols]
        except KeyError:
            pass
    else:
        df1 = pd.DataFrame()

    if df_list2:
        try:
            df2 = pd.concat(df_list2)
            df2 = df2[df2['(A)'].str.contains('20', na=False)]
            df2.rename(columns={'(E)': '(H)', '(F)': '(I)', '(G)': '(J)', '(H)': 'Unnamed: 0'}, inplace=True)
            df2[['(D)', '(E)', '(F)']] = df2['(D)'].str.rsplit(' ', n=2, expand=True)
            df2['(G)'] = np.nan
            df2 = df2[cols]
        except KeyError:
            pass
    else:
        df2 = pd.DataFrame()

    try:
        df2.drop(['Unnamed: 0'], axis=1, inplace=True)
    except KeyError:
        pass

    df = pd.concat([df1, df2])
    df['Property'] = pdf.split("_")[0]

    return df

def clean_date(x):
    if type(x) == str:
        if '20' not in x:
            return 'PASP Not Proceeded'
        elif '不適用' in x:
            return '-'
        else:
            x = re.findall(r'[0-9\-\/]+', x)[-1]
            x = x.replace('//', '/')
            # x = x[-10:]
            delimiter = re.findall(r'-|/', x)[0]
            x = '/'.join([num.zfill(2) for num in x.split(delimiter)])
            return dateutil.parser.parse(x, dayfirst=True).date()
    else:
        return x

def clean_tower(df):
    """
    Unsolved Case: e.g. 
    (1) "第2座 15", in which "15" is floor number.
    """

    if str(df['Tower']) != 'nan':
        scenario_1 = re.findall(r'第(.*?)座 \((.*?)\)', df['Tower'])
        scenario_2 = re.findall(r'第(.*?)座', df['Tower'])
        scenario_3 = re.findall(r'(H).*?(\d+)', df['Tower'])
        scenario_4 = re.findall(r'COURT ([A-Z]) TOWER ([0-9])', df['Tower'])

        if scenario_4:
            return ''.join(scenario_4[0])
        elif scenario_1:
            if scenario_1[0][0] in scenario_1[0][1]:
                return scenario_1[0][1].strip()
            else:
                return scenario_1[0][0].strip()
        elif scenario_2:
            return scenario_2[0].strip()
        elif scenario_3:
            return ''.join(scenario_3[0])
        elif df['Property'].lower() in df['Tower'].lower():
            return '1'
        else:
            return df['Tower'].replace('T', '').replace('別墅', '').lstrip('0').strip()
    else:
        return '1'

def clean_floor(x):
    """
    Unsolved Case: e.g. 
    (1) "12 12 12", "B1, G-2".
    """

    if type(x) == str:
        return x.replace('/F', '').replace(' ', '').lstrip('0')
    else:
        return x

def clean_unit(x):
    """
    Unsolved Case: e.g. 
    (1) "A B C", "8286".
    """

    if type(x) == str:
        scenario_1 = re.findall(r'\((.*?)\)', x)
        scenario_2 = re.findall(r'Duplex (\w+)', x)

        if scenario_1:
            return scenario_1[0].strip()
        elif scenario_2:
            return scenario_2[0].strip()
        else:
            return x.replace(' ', '')
    else:
        return x

def clean_price(x):
    """
    Unsolved Case: e.g. 
    (1) "在03-06-2024,基".
    """

    if type(x) == str:
        scenario_1 = re.findall(r'to\s*(?:HK)?\$\s*(\d+[,\d+]+)', x)

        if scenario_1:
            return scenario_1[0].replace(',', '')
        else:
            return '-'
    else:
        return x

def extract_pl_plan(x):
    """
    Unsolved Case: e.g. 
    (1) Incomprehensive remarks, 
    (2) PL is not mentioned but it is not by tender, 
    (3) 1st / 2nd Mortgage.
    x.lower()?
    """

    scenario_1 = re.findall(r'(\d+)[^\w][d|D]ays?.*? Payment(?:\s*Plan)?', x)
    scenario_2 = re.findall(r'\/\s?.*?\/\s?(.*?[s|S]tage)', x)
    scenario_3 = re.findall(r'[s|S]tage', x)
    scenario_4 = re.findall(r'[s|S]ee.*?[r|R]emark.*?(\(?[7|8].*?[\(\w+\)]+)', x)
    scenario_5 = re.findall(r'後\s*(\d+)\s*[日/天]', x)
    scenario_6 = re.findall(r'\((.*?)\)', x)

    if scenario_1:
        plan = scenario_1[0] + ' Days Cash'
    elif scenario_2:
        plan = scenario_2[0]
    elif scenario_3:
        plan = 'Stage'
    elif scenario_4:
        plan = scenario_4[0]
    elif scenario_5:
        plan = scenario_5[-1] + ' Days Cash'
    elif scenario_6 and (scenario_6[0] != 's'):
        plan = scenario_6[0]
    else:
        plan = '-'

    pl = re.findall(r'價單第?(.*?)號', x)
    tender = re.findall(r'[t|T]ender', x)

    if pl:
        pl = pl[0].strip()
    elif tender or plan != '-':
        pl = 'Tender'
    else:
        pl = '-'

    return plan+', '+pl

def clean_rots(df, date):
    df['Date (PASP)'] = df['Date (PASP)'].apply(transform_date).apply(clean_date)

    # https://stackoverflow.com/questions/47256212/convert-dates-to-pd-to-datetime-where-month-could-be-either-a-number-or-month-na
    df['Date (PASP)'] = pd.to_datetime(df[df['Date (PASP)'].str.len() == 10]['Date (PASP)'], format='%d-%m-%Y', errors="coerce")
    df['PASP Date'] = df['PASP Date'].dt.date
    df = df[df['PASP Date'] >= date-timedelta(days=7)]
    # df['ASP Date'] = df['ASP Date'].apply(transform_date).apply(clean_date) # Didn't run
    # df['Term Date'] = df['Term Date'].apply(clean_date) # Didn't run
    df['Tower'].fillna('1', inplace=True)
    df['Tower'] = df['Tower'].apply(clean_tower)
    # df['Adj. Price'].fillna(df['Price'], inplace=True) # Didn't run
    # df['Adj. Price'] = df['Adj. Price'].apply(lambda x: re.findall(r'\$\s?(\d+[,\d+]+)', x)[0]) # Didn't run
    df['Payment'] = df['Payment'].apply(extract_pl_plan)
    df[['PL', 'Plan']] = df['Payment'].str.split(', ', expand=True, n=1)

    return df
