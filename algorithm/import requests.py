import requests
import serial
import json
import time

def send_webex_message(token, room_id, message):
    headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
    }
    payload = {
        'roomId': room_id,
        'text': message
    }
    response = requests.post('https://webexapis.com/v1/messages', json=payload, headers=headers)
    return response.status_code

while True:
    organizationId = "1551713"
    url = "https://api.meraki.com/api/v1/organizations/" + organizationId + "/sensor/readings/latest"
    headers = {
    "Authorization": "Bearer ebc411a02fcda27b01a2434fe7c62d809ca39603",
    "Accept": "application/json"
    }

    max_ca2lls = 2
    current_call = 1
    countdate_count = 0
    total_eco2 = 0  # 값을 누적할 변수
    total_tvoc = 0 
    total_indoorAirQuality = 0 
    total_humidity = 0 
    total_temperature = 0 
    total_noise = 0 

    tmp = {}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        # 여기서는 'noise' 카테고리의 'ambient' 타입의 'level' 값을 추출하여 누적합니다.
        # API 응답 구조와 데이터의 존재 여부를 가정하에 작성되었습니다.
        #level_value = data[0]['readings'][5]['noise']['ambient']['level']
        for i in data[0]['readings']:
            tmp[i['metric']] = i[i['metric']]
        total_eco2 += tmp['eco2']['concentration']
        average_eco2 = total_eco2/current_call
        print(f"현재 eco2 값: {tmp['eco2']['concentration']}, 평균 eco2 값: {average_eco2}")

        #total_tvoc += tmp['tvoc']['concentration']
        #average_tvoc = total_tvoc/current_call
        #print(f"현재 tvoc 값: {tmp['tvoc']['concentration']}, 평균 tvoc 값: {average_tvoc}")

        #3total_indoorAirQuality += tmp['indoorAirQuality']['score']
        #average_indoorAirQuality = total_indoorAirQuality/current_call
        #print(f"현재 indoorAirQuality 값: {tmp['indoorAirQuality']['score']}, 평균 indoorAirQuality 값: {average_indoorAirQuality}")
    
        total_humidity += tmp['humidity']['relativePercentage']
        average_humidity = total_humidity/current_call
        print(f"현재 humidity 값: {tmp['humidity']['relativePercentage']}, 평균 humidity 값: {average_humidity}")
    
        total_temperature += tmp['temperature']['celsius']
        average_temperature = total_temperature/current_call

        #if current_call == 1:
        #    tempbiggest = tmp['temperature']['celsius']
       #     tempsmallest = tmp['temperature']['celsius']

       # if 1 < current_call < 289:
        #    if tempbiggest < tmp['temperature']['celsius']:
        #        tempbiggest = tmp['temperature']['celsius']
        #    elif tempsmallest > tmp['temperature']['celsius']:
        #        tempsmallest = tmp['temperature']['celsius']

        print(f"현재 temperature 값: {tmp['temperature']['celsius']}, 평균 temperature 값: {average_temperature}")
    
       # total_noise += tmp['noise']['ambient']['level']
       # average_noise = total_noise/current_call
       # print(f"현재 noise 값: {tmp['noise']['ambient']['level']}, 평균 noise 값: {average_noise}")
        print()
    else:
        print("데이터를 가져오는 데 실패했습니다.")
    
    current_call += 1
    '''
    if current_call % 288 == 0:
        countdate = 1
        countdate_count += 1
    else:
        countdate = 0
    '''


    # 시리얼 통신을 통해 광시간 데이터와 풍속 데이터를 읽는 함수
    def read_sensor_data(serial_port='COM7', baud_rate=9600):
        light = None
        windblow = None
        try:
            with serial.Serial(serial_port, baud_rate, timeout=1) as ser:
                print(f"Connected to {serial_port}")
                time.sleep(1)  # 장치가 데이터를 전송할 시간을 기다립니다.
                data = ""
                while light is None or windblow is None:
                    if ser.in_waiting > 0:  
                        incoming_data = ser.read(ser.in_waiting).decode('utf-8')
                        print(f"Received raw data: {incoming_data}")
                        data += incoming_data
                        lines = data.strip().split("\n")
                        for line in lines:
                            if "light" in line:
                                temp_light = float(line.split(":")[1].strip())
                                if temp_light != 0:
                                    light = temp_light
                            elif "windblow" in line:
                                temp_windblow = float(line.split(":")[1].strip())
                                if temp_windblow != 0:
                                    windblow = temp_windblow
                            elif "humidity" in line:
                                temp_humidity = float(line.split(":")[1].strip())
                                if temp_humidity != 0:
                                    humidity = temp_humidity
                            elif "temperature" in line:
                                temp_temperature = float(line.split(":")[1].strip())
                                if temp_temperature != 0:
                                    temperature = temp_temperature
                    else:
                        print("No data in waiting, trying again...")
                        time.sleep(0.5)

        except Exception as e:
            print(f"Error reading serial data: {e}")

        return light if light is not None else 0, windblow if windblow is not None else 0, humidity if humidity is not None else 0, temperature if temperature is not None else 0

    # 파싱 함수
    def parse_serial_data(serial_data):
        light = None
        windblow = None
        humidity = None
        temperature = None
        # Serial 데이터를 줄 단위로 분리하여 처리
        lines = serial_data.strip().split("\n")
        for line in lines:
            parts = line.split(":")
            if len(parts) == 2:
                key, value = parts[0].strip(), parts[1].strip()
                if key == "light":
                    light = float(value)
                elif key == "windblow":
                    windblow = float(value)
                elif key == "humidity":
                    humidity = float(value)
                elif key == "temperature":
                    temperature = float(value)
        return light, windblow, humidity, temperature

    # 나무 추천 알고리즘
    def recommend_tree(env_data, trees_preferences):
        temp, humidity, co2, light, wind = env_data

        # 각 환경 요소별 가중치 설정
        weights = {
            'temp': 1,
            'humidity': 1.2,
            'co2': 0.5,
            'light': 2,
            'wind': 0.8
        }

        scores = {}
        for tree, prefs in trees_preferences.items():
            # 생존 습도 조건 검사
            if 'survival_humidity' in prefs and not(prefs['survival_humidity'][0] <= humidity <= prefs['survival_humidity'][1]):
                continue  # 생존 조건에 맞지 않으면 추천 목록에서 제외

            # 생존 풍향 조건 검사
            if 'survival_wind' in prefs and not(prefs['survival_wind'][0] <= wind <= prefs['survival_wind'][1]):
                continue  # 풍향 조건에 부합하지 않으면 추천 목록에서 제외

            score = 0
            score += (prefs['temp'][0] <= temp <= prefs['temp'][1]) * weights['temp']
            score += (prefs['humidity'][0] <= humidity <= prefs['humidity'][1]) * weights['humidity']
            score += (prefs['co2'][0] <= co2 <= prefs['co2'][1]) * weights['co2']
            score += (prefs['light'][0] <= light <= prefs['light'][1]) * weights['light']
            score += (prefs['wind'][0] <= wind <= prefs['wind'][1]) * weights['wind']
            scores[tree] = score

        # 상위 3개 나무를 점수 순으로 추천
        recommended_trees = sorted(scores, key=scores.get, reverse=True)[:3]
        return recommended_trees

    # 나무 데이터
    trees_preferences = {

        '소나무': {'temp': (-18, 38), 'humidity': (50, 80), 'co2': (0, 1000), 'light': (6, 24), 'wind': (0, 17)},
        '은행나무': {'temp': (-30, 35), 'humidity': (50, 70), 'co2': (0, 900), 'light': (4, 24), 'wind': (0, 60)},
        '전나무': {'temp': (-30, 20), 'humidity': (60, 100), 'co2': (0, 1000), 'light': (1, 24), 'wind': (0, 17),'survival_humidity': (30, 100)},
        '향나무': {'temp': (-1, 18), 'humidity': (0, 40), 'co2': (0, 600), 'light': (6, 24), 'wind': (0, 17),'survival_humidity': (80, 100)},
        '메타세콰이어': {'temp': (15, 25), 'humidity': (60, 100), 'co2': (0, 450), 'light': (6, 24), 'wind': (0, 50)},
        '가문비나무': {'temp': (-3, 22), 'humidity': (20, 50), 'co2': (0, 500), 'light': (4, 24), 'wind': (0, 14),'survival_humidity': (80, 100)},
        '느티나무': {'temp': (-10, 38), 'humidity': (50, 100), 'co2': (0, 600), 'light': (1, 24), 'wind': (0, 40)},
        '먼나무': {'temp': (15, 25), 'humidity': (70, 90), 'co2': (0, 600), 'light': (4, 24), 'wind': (0, 14),'survival_wind': (6, 20)},
        '삼나무': {'temp': (-5, 35), 'humidity': (60, 100), 'co2': (0, 500), 'light': (1, 24), 'wind': (0, 17),'survival_humidity': (30, 100)},
        '플라타너스': {'temp': (-5, 35), 'humidity': (0, 50), 'co2': (0, 1000), 'light': (6, 24), 'wind': (0, 50),'survival_humidity': (20, 100)},
        '단풍나무': {'temp': (-30, 35), 'humidity': (60, 80), 'co2': (0, 1000), 'light': (3, 24), 'wind': (0, 14)}
    
        
    }

    # 시리얼 통신을 통해 실시간으로 값을 받아온 데이터
    real_time_light, real_time_windblow, real_time_humid, real_time_temperature= read_sensor_data(serial_port='COM7', baud_rate=9600)
    temp_serial, humidity_serial, light_serial, wind_serial = real_time_temperature, real_time_humid, real_time_light, real_time_windblow  # 예시 값

    # API 등에서 받아온 다른 환경 데이터
    temp_api, humidity_api, co2_api = average_temperature, average_humidity, average_eco2  # 예시 값

    # 고정값 환경 데이터 설정 

    #환경 고정값 1
    fixed_light_1 = 6  # 고정 광시간 값
    fixed_wind_1 = 10
    fixed_humid_1 = 20
    fixed_temperature_1 = 15
    fixed_co2_1 = 500

    #환경 고정값 2
    fixed_light_2 = 7
    fixed_wind_2 = 15
    fixed_humid_2 = 20
    fixed_temperature_2 = 15
    fixed_co2_2 = 500

    #환경 고정값 3
    fixed_light_3 = 3
    fixed_wind_3 = 30
    fixed_humid_3 = 40
    fixed_temperature_3 = 35
    fixed_co2_3 = 500

    #환경 고정값 4
    fixed_light_4 = 8
    fixed_wind_4 = 20
    fixed_humid_4 = 40
    fixed_temperature_4 = 15
    fixed_co2_4 = 500

    # 테스트 환경 데이터 세트에 광시간 데이터 포함
    test_env_data_area0 = (temp_api, humidity_api, co2_api, fixed_light_1, fixed_wind_1)
    test_env_data_area1 = (tmp['temperature']['celsius'], tmp['humidity']['relativePercentage'], tmp['eco2']['concentration'], fixed_light_2, fixed_wind_2)
    test_env_data_area2 = (temp_serial, humidity_serial, fixed_co2_1, light_serial, wind_serial)
    test_env_data_area3 = (fixed_temperature_3, fixed_humid_3, fixed_co2_3 , fixed_light_3, fixed_wind_3)
    test_env_data_area4 = (fixed_temperature_4, fixed_humid_4, fixed_co2_4 , fixed_light_4, fixed_wind_4)



    ###################################################################################################
    # 영등포구의 평균 기후 데이터
    yeongdeungpo_avg_env_data = (23, 40, 500, 3, 7)#온습씨라윈

    # 각 변수별 최소값과 최대값 설정
    yeongdeungpo_min_max_values = {
        'temp': (2, 19),
        'humidity': (13, 55),
        'co2': (0, 8000000),
        'light': (1, 4),
        'wind': (0, 12)
        
             
    }

    def calculate_climate_difference(env_data, avg_env_data):
        # 차이 계산
        diff = [env_data[i] - avg_env_data[i] for i in range(len(env_data))]
        return diff

    def calculate_change_rate(diff, min_max):
        # 변화율 계산
        change_rate = []
        for d, (min_val, max_val) in zip(diff, min_max.values()):
            range_val = max_val - min_val
            if range_val != 0:
                rate = d / range_val
            else:
                rate = 0
            change_rate.append(rate)
        return change_rate

    def get_top_two_differences(env_data, avg_env_data):
        climate_diff = calculate_climate_difference(env_data, avg_env_data)
        climate_change_rates = calculate_change_rate(climate_diff, yeongdeungpo_min_max_values)
        
        change_rate_dict = {
            'temp': climate_change_rates[0],
            'humidity': climate_change_rates[1], 
            'wind': climate_change_rates[3],
        }

        top_two_diffs = sorted(change_rate_dict.items(), key=lambda x: abs(x[1]), reverse=True)[:2]
        return top_two_diffs

    # 가상의 환경 데이터로 함수 테스트
    
    top_two_differences_area0 = get_top_two_differences(test_env_data_area1, yeongdeungpo_avg_env_data)
    top_two_differences_area1 = get_top_two_differences(test_env_data_area1, yeongdeungpo_avg_env_data)
    top_two_differences_area2 = get_top_two_differences(test_env_data_area2, yeongdeungpo_avg_env_data)
    top_two_differences_area3 = get_top_two_differences(test_env_data_area3, yeongdeungpo_avg_env_data)
    top_two_differences_area4 = get_top_two_differences(test_env_data_area4, yeongdeungpo_avg_env_data)

    token = 'MzViZmRiNjItZDE1Ni00ODQ5LThmYjktMmRmMzg2ODZhZjc3MWMzNWE2ZDgtYjBj_P0A1_719e5834-e6ce-4718-b3d0-7b6ed355fd8e'
    room_id = 'a510cc80-dac8-11ee-9d90-7150475d7dfd'
    message = 0
    for top_two in [top_two_differences_area1, top_two_differences_area2, top_two_differences_area3, top_two_differences_area4]:
        for feature, change_rate in top_two:
            if abs(change_rate) > 0.7:
                message = f"경고: {feature} 값이 급격히 변화했습니다. 변화율: {change_rate*100:.2f}%"
                send_webex_message(token, room_id, message)



    #############################################################################################

    # 나무 추천 알고리즘 실행
    recommended_trees_area1 = recommend_tree(test_env_data_area0, trees_preferences)      
    recommended_trees_area1 = recommend_tree(test_env_data_area1, trees_preferences)
    recommended_trees_area2 = recommend_tree(test_env_data_area2, trees_preferences)
    recommended_trees_area3 = recommend_tree(test_env_data_area3, trees_preferences)    
    recommended_trees_area4 = recommend_tree(test_env_data_area4, trees_preferences)   

    class ServerUpdateError(Exception):
        def __init__(self, error_message: str = "Failed to put data to server"):
            super().__init__(error_message)


    def updater(url: str, key: str, data: str):
        data = {
            key: data
        }

        res = requests.patch(
            url + ".json",
            json=data
        )

        if res.status_code != 200:
            raise ServerUpdateError("Failed to put data to server")


    # area0 전송
    url0 = "https://cisco-map-417104-default-rtdb.asia-southeast1.firebasedatabase.app/area0/"
    key = "climate"
    updater(url0, key, [temp_api, humidity_api, co2_api, fixed_light_1, fixed_wind_1])
    key = "recommend"
    updater(url0, key, recommended_trees_area1)    
    key = "feature"
    updater(url0, key, top_two_differences_area1)

    # area1 전송
    url = "https://cisco-map-417104-default-rtdb.asia-southeast1.firebasedatabase.app/area1/"
    key = "climate"
    updater(url, key, [tmp['temperature']['celsius'], tmp['humidity']['relativePercentage'], tmp['eco2']['concentration'], fixed_light_2, fixed_wind_2])
    key = "recommend"
    updater(url, key, recommended_trees_area1)    
    key = "feature"
    updater(url, key, top_two_differences_area1)


    # area2 전송
    url2 = "https://cisco-map-417104-default-rtdb.asia-southeast1.firebasedatabase.app/area2/"
    key = "climate"
    updater(url2, key, [temp_serial, humidity_serial, fixed_co2_1, light_serial, wind_serial])
    key = "recommend"
    updater(url2, key, recommended_trees_area2)
    key = "feature"
    updater(url2, key, top_two_differences_area2)

    # area3 전송
    url3 = "https://cisco-map-417104-default-rtdb.asia-southeast1.firebasedatabase.app/area3/"
    key = "climate"
    updater(url3, key, [fixed_temperature_3, fixed_humid_3, fixed_co2_3 , fixed_light_3, fixed_wind_3])
    key = "recommend"
    updater(url3, key, recommended_trees_area3)
    key = "feature"
    updater(url3, key, top_two_differences_area3) 

    # area4 전송
    url4 = "https://cisco-map-417104-default-rtdb.asia-southeast1.firebasedatabase.app/area4/"
    key = "climate"
    updater(url4, key, [fixed_temperature_4, fixed_humid_4, fixed_co2_4 , fixed_light_4, fixed_wind_4])
    key = "recommend"
    updater(url4, key, recommended_trees_area4)
    key = "feature"
    updater(url4, key, top_two_differences_area4) 


    # webex

    time.sleep(10)