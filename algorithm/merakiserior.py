import requests
import json
import time

organizationId = "1551713"
url = "https://api.meraki.com/api/v1/organizations/" + organizationId + "/sensor/readings/latest"
headers = {
   "Authorization": "Bearer ebc411a02fcda27b01a2434fe7c62d809ca39603",
   "Accept": "application/json"
}

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

max_calls = 289
current_call = 1
total_eco2 = 0  # 값을 누적할 변수
total_tvoc = 0 
total_indoorAirQuality = 0 
total_humidity = 0 
total_temperature = 0 
total_noise = 0

# 현재 날짜와 시간을 포함한 파일명 생성
current_time = time.strftime("%Y%m%d-%H%M%S")
filename = f"sensor_data_{current_time}.txt"


tmp = {}
while current_call < max_calls:
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
        

        total_tvoc += tmp['tvoc']['concentration']
        average_tvoc = total_tvoc/current_call
        #print(f"현재 tvoc 값: {tmp['tvoc']['concentration']}, 평균 tvoc 값: {average_tvoc}")

        total_indoorAirQuality += tmp['indoorAirQuality']['score']
        average_indoorAirQuality = total_indoorAirQuality/current_call
        #print(f"현재 indoorAirQuality 값: {tmp['indoorAirQuality']['score']}, 평균 indoorAirQuality 값: {average_indoorAirQuality}")
       
        total_humidity += tmp['humidity']['relativePercentage']
        average_humidity = total_humidity/current_call
        
       
        total_temperature += tmp['temperature']['celsius']
        average_temperature = total_temperature/current_call
        
       
        total_noise += tmp['noise']['ambient']['level']
        average_noise = total_noise/current_call
        #print(f"현재 noise 값: {tmp['noise']['ambient']['level']}, 평균 noise 값: {average_noise}")

        print(f"현재 temperature 값: {tmp['temperature']['celsius']}, 평균 temperature 값: {average_temperature}")
        print(f"현재 humidity 값: {tmp['humidity']['relativePercentage']}, 평균 humidity 값: {average_humidity}")
        print(f"현재 eco2 값: {tmp['eco2']['concentration']}, 평균 eco2 값: {average_eco2}")

        print()

        # 파일에 데이터 저장
        with open(filename, 'a', encoding='utf-8') as file:
            file.write(f"현재 temperature 값: {tmp['temperature']['celsius']}, 평균 temperature 값: {average_temperature}\n")
            file.write(f"현재 humidity 값: {tmp['humidity']['relativePercentage']}, 평균 humidity 값: {average_humidity}\n")
            file.write(f"현재 eco2 값: {tmp['eco2']['concentration']}, 평균 eco2 값: {average_eco2}\n\n")
    
    else:
        print("데이터를 가져오는 데 실패했습니다.")

    current_call += 1
    
    #GUI에 값보내기
    #import requests
    
    # 예시
    url_gui0 = "https://cisco-map-417104-default-rtdb.asia-southeast1.firebasedatabase.app/area0/"
    key = "climate"
    updater(url_gui0, key, [tmp['temperature']['celsius'],tmp['humidity']['relativePercentage'],tmp['eco2']['concentration'],average_temperature,average_humidity,average_eco2])
    
    url_gui2 = "https://cisco-map-417104-default-rtdb.asia-southeast1.firebasedatabase.app/area2/"
    key = "climate"
    updater(url_gui2, key, [tmp['temperature']['celsius'],tmp['humidity']['relativePercentage'],tmp['eco2']['concentration'],average_temperature,average_humidity,average_eco2])

    '''
    b = 'OWIwZGRmNDEtZmRmMi00NDFhLTgxZDItMDc3Nzk2NzdlMmRhYjU0NWRkZjEtZmU5_P0A1_719e5834-e6ce-4718-b3d0-7b6ed355fd8e'

    #import requests
    from requests_toolbelt.multipart.encoder import MultipartEncoder

    m = MultipartEncoder({'roomId': 'a510cc80-dac8-11ee-9d90-7150475d7dfd',
                      'text': f"현재 temperature 값: {tmp['temperature']['celsius']}, 평균 temperature 값: {average_temperature}\n"})

    r = requests.post('https://webexapis.com/v1/messages', data=m,
                  headers={'Authorization': 'Bearer '+b,
                  'Content-Type': m.content_type})

    print(r.text)
    '''
    
    time.sleep(10) 