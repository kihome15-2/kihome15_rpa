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
# set chrome driver and master data folder path
chrome_driver_path = 'C:/Users/scatt/Python/selenium/chromedriver.exe' # abspath로 입력해야함
output_path = 'output'
os.makedirs(output_path, exist_ok=True)

# %%
# Crawling main information
#--- 기준 데이터 로드 ---#
data1_list= []
start_point = 0
for idx1, check_no in enumerate(tqdm_notebook(np.arange(start_point, 10))):
    # request를 보내서 기초 데이터를 받음
    try:
        req = requests.get(f"https://apis.zigbang.com/v2/danjis/{check_no}")
        if 'NotFoundError' not in str(req.text):
            data1 = json.loads(req.text)
            # json 데이터 정리 (사용승인일은 에러나서 이렇게 정리)
            try:
                use_appoval_date = pd.to_datetime(data1['사용승인일'], format='%Y-%m-%d').strftime('%Y-%m-%d'),
            except:
                use_appoval_date = data1['사용승인일']

            data1_list.append([check_no, data1['local1'], data1['local2'], data1['local3'], data1['jibunAddress'],
                                    data1['시행사'], data1['시공사'], data1['서비스구분'],
                                    use_appoval_date,
                                    data1['분양세대수'], data1['분양년월'], data1['분양년월표기'],
                                    data1['총세대수'], data1['총동수'], data1['최고층수'],
                                    data1['최저층수'], data1['가구당주차대수'],
                                    data1['총주차대수'], data1['주차위치'],
                                    data1['난방방식'], data1['난방연료'], data1['편의시설'],
                                    data1['용적율'], data1['건폐율'], data1['건설사'],
                                    ]) 
        if (idx1 != 0)&(idx1 % 1000 == 0)&(len(data1_list) != 0):
            # dataframe으로 저장
            temp_main_info_df = pd.DataFrame(data1_list, columns = ['check_no', 'main_시', 'main_구', 'main_동', 'main_지번', 'main_시행사', 
                                            'main_시공사', 'main_서비스구분','main_사용승인일', 'main_분양세대수', 
                                            'main_분양년월', 'main_분양년월표기','main_총세대수', 'main_총동수', 'main_최고층수',
                                            'main_최저층수', 'main_가구당주차대수','main_총주차대수', 'main_주차위치','main_난방방식', 
                                            'main_난방연료', 'main_편의시설','main_용적율', 'main_건폐율', 'main_건설사'])
            temp_main_info_df.to_csv(f"{output_path}/main_info_df_{str(temp_main_info_df['check_no'].min())}.csv")
            print(f"{idx1} - no {temp_main_info_df['check_no'].max()} - shape {temp_main_info_df.shape}")
            data1_list = []
    except:
        pass

# %%
# Merge main information
print('# Merge main_info_df')
main_info_df = pd.DataFrame([])
file_path_list = [os.path.join(output_path,i) for i in os.listdir(output_path) if ('main_info_df' in i)&('csv' in i)]
for file_path in tqdm_notebook(file_path_list):
    temp_df = pd.read_csv(file_path)
    main_info_df = pd.concat([main_info_df, temp_df],0)
main_info_df = main_info_df.sort_values(['check_no'],ascending=True).drop_duplicates(keep='first').reset_index(drop=True)
main_info_df.to_excel(f"{output_path}/main_info_df.xlsx", index=False)
print(main_info_df.shape)

