# %%
import pandas as pd
import numpy as np

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
import requests, json, inspect, os, platform, time, random, time, warnings
warnings.filterwarnings(action='ignore')  

from IPython.display import clear_output
from datetime import datetime
from tqdm import tqdm_notebook

def replace_str_int(input_list):
    output_list = []
    for i in input_list:
        try:
            output_list.append(int(i.replace(",","")))
        except:
            output_list.append(int(i))
    return output_list

# %%
# set chrome driver path
chrome_driver_path = 'C:/Users/scatt/Python/selenium/chromedriver.exe' # abspath로 입력해야함
output_path = 'output'
os.makedirs(output_path, exist_ok=True)

# %%
# read main information dataset
main_info_df = pd.read_excel(f"{output_path}/main_info_df.xlsx")
main_info_df.shape

# %%
# set city and dong/gu information
print(f"# 다음 중 검색할 도시를 입력하세요 : {main_info_df['main_시'].unique()}")
input_si = input()
if len(input_si) != 0:
    temp_main_info_df = main_info_df[main_info_df['main_시'] == input_si]
else:
    temp_main_info_df = main_info_df
print(temp_main_info_df.shape)
print('-'*50)

print(f"# 다음 중 검색할 구를 입력하세요(미입력시 전체 검색) : {temp_main_info_df['main_구'].unique()}")
input_gu = input()
if len(input_gu) != 0:
    temp_main_info_df = temp_main_info_df[temp_main_info_df['main_구'] == input_gu]
else:
    temp_main_info_df = temp_main_info_df
print(temp_main_info_df.shape)
print('-'*50)

print(f"# 다음 중 검색할 동을 입력하세요(미입력시 전체 검색) : {temp_main_info_df['main_동'].unique()}")
input_dong = input()
if len(input_dong) != 0:
    temp_main_info_df = temp_main_info_df[temp_main_info_df['main_동'] == input_dong]
print(temp_main_info_df.shape)
print('-'*50)

print(f"# 검색할 최소 세대수를 입력하세요(미입력시 전체 검색) ")
input_living_count = input()
temp_main_info_df['main_총세대수'] = temp_main_info_df['main_총세대수'].astype('int')
if len(input_living_count) != 0:
    temp_main_info_df = temp_main_info_df[temp_main_info_df['main_총세대수'] >= int(input_living_count)]
print(temp_main_info_df.shape)
print('-'*50)

search_list = list(temp_main_info_df['check_no'])
print(f"# 탐색할 단지 개수 : {len(search_list)}")

temp_main_info_df.head()

# %%
# start crawling
# 기존 데이터 삭제
for file_name in ['type_info_df', 'now_sale_df', 'past_sale_df']:
    try:
        os.remove(f"output/{file_name}.xlsx")
    except:
        pass

#--- 크롬드라이버 로딩 ---#
options = webdriver.ChromeOptions()
options.add_argument('--disable-gpu')
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36')

current_folder = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile(inspect.currentframe()))[0]))

# https://chromedriver.chromium.org/downloads
driver = webdriver.Chrome(chrome_driver_path, options=options)
driver.implicitly_wait(10)
driver.get("https://apis.zigbang.com/")

#--- search ---#
os.makedirs(output_path, exist_ok=True)

# 크롤링 
name_idx = -1

for idx1, check_no in enumerate(tqdm_notebook(search_list[1900:])):
    for reset_idx in range(3):
        try:
            if (idx1 % 95 == 0)&(idx1 != 0):
                time.sleep(300)
                print('# timesleep 300s')
            data1_list, data2_list, data3_list, data4_list = [], [], [], []
            ttl_data = []
            req = requests.get(f"https://apis.zigbang.com/v2/danjis/{check_no}")
            if 'NotFoundError' not in str(req.text):
                #--- data1  ---#
                data1 = json.loads(req.text)
                LOCAL1 = data1['local1']
                LOCAL2 = data1['local2']
                LOCAL3 = data1['local3']
                JIBUN_ADDRESS = data1['jibunAddress']
                APT_NAME = data1['name']

                URL_PATH = f"https://www.zigbang.com/home/apt/danjis/{check_no}"
                driver.get(URL_PATH)
                time.sleep(1)

                # 단지 이름 긁어오기(가끔씩 xpath를 바꾸는 경우가 있어서 매번 확인해서 진행)
                if name_idx == -1:
                    for name_idx in range(10):
                        try:
                            elem = driver.find_element_by_xpath(f'//*[@id="__next"]/div[2]/div/div[2]/div/div/div[1]/div[2]/div[2]/div/div[2]/div[{name_idx}]/div[1]/div[1]/div/div[1]/div/div[1]/div/div[1]/div[1]')
                            danji_name = elem.text
                            break
                        except:
                            pass
                else:
                    try:
                        elem = driver.find_element_by_xpath(f'//*[@id="__next"]/div[2]/div/div[2]/div/div/div[1]/div[2]/div[2]/div/div[2]/div[{name_idx}]/div[1]/div[1]/div/div[1]/div/div[1]/div/div[1]/div[1]')
                        danji_name = elem.text
                    except:
                        for name_idx in range(10):
                            try:
                                elem = driver.find_element_by_xpath(f'//*[@id="__next"]/div[2]/div/div[2]/div/div/div[1]/div[2]/div[2]/div/div[2]/div[{name_idx}]/div[1]/div[1]/div/div[1]/div/div[1]/div/div[1]/div[1]')
                                danji_name = elem.text
                                break
                            except:
                                pass

                #--- data2 : 전체 매매/전세 기록 긁어오기 ---#
                # 더보기 계속 클릭
                past_data2 = ""
                for idx4 in range(50):
                    try:
                        elem = driver.find_element_by_xpath('//*[@id="__next"]/div[2]/div/div[2]/div/div/div[1]/div[2]/div[2]/div/div[4]/div/div[1]/div[2]/div/div[3]/div/div[2]/div[3]/div')
                        elem.click()
                        time.sleep(0.2)

                        # 모든 데이터 긁어오기
                        elem = driver.find_element_by_xpath('//*[@id="__next"]/div[2]/div/div[2]/div/div/div[1]/div[2]/div[2]')
                        data2 = elem.text
                        if idx4 % 5 == 0:
                            if len(past_data2) == len(data2):
                                break
                            else:
                                past_data2 = data2
                    except:
                        break

                sale_count = int(data2.split('매물보기')[1].split('개')[0].replace(",","").strip()) # 매물 개수
                people_count = int(data2.split('세대')[0].strip().split(' ')[-1].replace(",","").strip()) # 세대수

                # 실거래 내역 정리
                data2_raw_list = data2.replace(" ","").split('\n')
                date2_arrange_list = []
                for idx3, text in enumerate(data2_raw_list):
                    if (text == '매매')|(text == '전세')|(text == '월세'):
                        if '전월세' not in data2_raw_list[idx3+1]:
                            sell_type = data2_raw_list[idx3]
                            price_raw = data2_raw_list[idx3+1]
                            try:
                                floor_idx = data2_raw_list[idx3:idx3+10].index('층') - 1
                            except:
                                break
                            floor = data2_raw_list[idx3+floor_idx]
                            house_type = data2_raw_list[idx3+2]
                            date = data2_raw_list[idx3-1]
                            sell_date = pd.to_datetime(f"{int(date.split('.')[0]) +2000}.{int(date.split('.')[1])}.{int(date.split('.')[2])}", format='%Y-%m-%d').strftime('%Y-%m-%d')

                            # 이전 거래 기록 전월세 
                            if text == '월세': # 월세
                                monthly_price = int(price_raw.split('/')[1])*10000
                                if '억' in price_raw.split('/')[0]:
                                    price_a = int(price_raw.split('/')[0].replace(",","").split('억')[0])*100000000
                                    try:
                                        price_b = int(price_raw.split('/')[0].replace(",","").split('억')[1].replace(',',''))*10000
                                    except:
                                        price_b = 0
                                else:
                                    price_a = 0
                                    try:
                                        try:
                                            price_b = int(price_raw.split('/')[0].replace(",","").split('억')[1].replace(',',''))*10000
                                        except:
                                            price_b = int(price_raw.split('/')[0].replace(',',''))*10000
                                    except:
                                        price_b = 0

                            else: # 전월세
                                monthly_price = 0
                                if '억' in price_raw:
                                    price_a = int(price_raw.split('억')[0])*100000000
                                    try:
                                        price_b = int(price_raw.split('억')[1].replace(',',''))*10000
                                    except:
                                        price_b = 0
                                else:
                                    price_a = 0
                                    price_b = int(price_raw.split('/')[0].replace(',',''))*10000
                            past_price = price_a + price_b 
                            data2_list.append([check_no, house_type, sell_date, sell_type, past_price, monthly_price, floor])

                try:
                    existing_past_sale_df = pd.read_excel(f"{output_path}/past_sale_df.xlsx")                  
                except:
                    existing_past_sale_df = pd.DataFrame([])
                    pass
                past_sale_df = pd.DataFrame(data2_list, columns = ['check_no', '타입정보_타입', '과거거래_일자', '과거거래_유형', '과거거래_가격', '과거거래_월세', '과거거래_층수'])
                past_sale_df['과거거래_가격'] = replace_str_int(past_sale_df['과거거래_가격'])

                past_sale_df = pd.concat([past_sale_df, existing_past_sale_df],0).drop_duplicates(subset=None, keep='first').reset_index(drop=True)
                past_sale_df.to_excel(f"{output_path}/past_sale_df.xlsx",index=False)

                #--- data3 : Room 타입 정보 긁어오기 ---#
                data3 = []
                for idx2 in range(2,20):
                    try:
                        # 타입정보 클릭
                        elem = driver.find_element_by_xpath(f'//*[@id="__next"]/div[2]/div/div[2]/div/div/div[1]/div[2]/div[2]/div/div[3]/div/div/div/div/div[2]/div/div/div[1]/div/div[{idx2}]/div[1]')
                        elem.click()

                        # 타입정보 긁어오기
                        elem = driver.find_element_by_xpath('//*[@id="__next"]/div[2]/div/div[2]/div/div/div[1]/div[2]/div[2]/div/div[4]/div/div[1]/div[2]/div/div[1]/div/div[2]')
                        data3.append(elem.text)
                        time.sleep(0.5)
                    except:
                        break

                # data3 타입 정보 정리 
                for i in data3:
                    try:
                        house_type = i.split('\n')[0].split('㎡')[0]
                    except:
                        house_type = 0

                    try:
                        house_type_count = int(i.split('\n')[0].split('(')[1].split('세대')[0])
                    except:
                        house_type_count = 0

                    try:
                        supply_size = float(i.split('\n')[1].split('㎡')[0].split('공급')[1].strip())
                    except:
                        supply_size = 0

                    try:
                        real_size = float(i.split('\n')[1].split('전용')[1].split('㎡')[0].strip())
                    except:
                        real_size = 0

                    try:
                        room_count = int(i.split('\n')[2].split('방')[1].split('개')[0].strip())
                    except:
                        room_count = 0

                    try:
                        bathroom_count = int(i.split('\n')[2].split('욕실')[1].split('개')[0].strip())
                    except:
                        bathroom_count = 0

                    try:
                        hallway = i.split('\n')[2].split('·')[-1].strip()
                    except:
                        hallway = ''

                    data3_list.append([check_no, house_type, house_type_count, supply_size, real_size, room_count, bathroom_count, URL_PATH])

                try:
                    existing_type_info_df = pd.read_excel(f"{output_path}/type_info_df.xlsx")                  
                except:
                    existing_type_info_df = pd.DataFrame([])
                    pass
                type_info_df = pd.DataFrame(data3_list, columns = ['check_no','타입정보_타입', '타입정보_개수','타입정보_공급','타입정보_전용','타입정보_방개수','타입정보_화장실개수', '타입정보_URL'])
                type_info_df['단지이름'] = danji_name
                type_info_df = pd.concat([type_info_df, existing_type_info_df],0).drop_duplicates(subset=None, keep='first').reset_index(drop=True)
                type_info_df.to_excel(f"{output_path}/type_info_df.xlsx",index=False)

                #--- data4 : 매물 정보 정리 ---#
                if sale_count > 0:
                    driver.get(URL_PATH)
                    time.sleep(1)
                    for i in range(5):
                        try:
                            # 매물보기
                            elem = driver.find_element_by_xpath('//*[@id="__next"]/div[2]/div/div[2]/div/div/div[1]/div[2]/div[2]/div/div[2]/div[1]/div/div[1]/div')
                            elem.click()
                            time.sleep(1)

                            # 매물 정보 정리
                            elem = driver.find_element_by_xpath('//*[@id="__next"]/div[2]/div/div[2]/div/div[2]')
                            sailing_product_list = elem.text.split('\n')
                            break
                        except:
                            time.sleep(1)
                    for idx, i in enumerate(sailing_product_list):
                        if (('매매' in i)|('전세' in i)|('월세' in i))&('억' in i):
                            sailing_house_type = sailing_product_list[idx+1].split('/')[0]
                            sailing_type = sailing_product_list[idx].split(' ')[0].strip()
                            # 매물가격
                            price_a = int(sailing_product_list[4].split('억')[0].split(' ')[1]) * 100000000
                            try:
                                price_b = int(sailing_product_list[4].split('억')[1].replace(',','').strip()) * 10000
                            except:
                                price_b = 0
                            sailing_price = price_a + price_b
                            sailing_house_size = float(sailing_product_list[idx+1].split('/')[1].split('㎡')[0])
                            sailing_house_size_pyung = float(sailing_product_list[idx+1].split('/')[1].split('㎡')[0])/3.3058
                            sailing_floor_site = sailing_product_list[idx+1].split('·')[1].strip()
                            sailing_today = datetime.now().strftime('%Y-%m-%d')
                            data4_list.append([check_no, sailing_house_type, sailing_today, sailing_type, sailing_price, sailing_house_size, sailing_house_size_pyung, sailing_floor_site])
                else:
                    data4_list = []
                try:
                    existing_now_sale_df = pd.read_excel(f"{output_path}/now_sale_df.xlsx")                  
                except:
                    existing_now_sale_df = pd.DataFrame([])
                    pass
                now_sale_df = pd.DataFrame(data4_list, columns = ['check_no', '타입정보_타입', '현재매물_일자', '현재매물_유형', '현재매물_가격', '현재매물_사이즈','현재매물_평수','현재매물_동호수'])
                now_sale_df['현재매물_가격'] = replace_str_int(now_sale_df['현재매물_가격'])
                now_sale_df = pd.concat([now_sale_df, existing_now_sale_df],0).drop_duplicates(subset=None, keep='first').reset_index(drop=True)
                now_sale_df.to_excel(f"{output_path}/now_sale_df.xlsx",index=False)
            break
        except:
            print('# PROCESS ERROR - ', idx1, '-', reset_idx)
            pass

# %%
# merge dataset
type_info_df = pd.read_excel("output/type_info_df.xlsx") # 평수 관련 데이터
now_sale_df = pd.read_excel("output/now_sale_df.xlsx")  # 매물 가격 데이터
past_sale_df = pd.read_excel("output/past_sale_df.xlsx") # 과거 실거래 가격 데이터

print(main_info_df.shape, type_info_df.shape, now_sale_df.shape, past_sale_df.shape)
print(f"# main_info_df shape : {main_info_df.shape}")
print(f"# type_info_df shape : {type_info_df.shape}")
print(f"# now_sale_df shape : {now_sale_df.shape}")
print(f"# past_sale_df shape : {past_sale_df.shape}")

# make total dataset
temp_df1 = pd.merge(type_info_df, main_info_df, how='left', on=['check_no'])
temp_df2 = pd.merge(temp_df1, past_sale_df, how='left', on=['check_no','타입정보_타입'])
temp_df3 = pd.merge(temp_df2, now_sale_df, how='left', on=['check_no','타입정보_타입'])

# set total dataset columns
arrange_col_list = ['check_no', '타입정보_타입', '단지이름'] \
                    + [i for i in temp_df3 if 'main' in i] \
                    + [i for i in temp_df3 if '타입정보' in i] \
                    + [i for i in temp_df3 if '과거거래' in i] \
                    + [i for i in temp_df3 if '현재매물' in i]
temp_df4 = temp_df3[arrange_col_list]

# save total dataset
os.makedirs(output_path,exist_ok=True)
temp_df4.to_excel(f'{output_path}/result_{input_si}-{input_gu}-{input_dong}-{str(input_living_count)}.xlsx',index=False)
