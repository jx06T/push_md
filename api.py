import os 
from dotenv import load_dotenv
import requests
import time

load_dotenv()

REFRESH_TOKEN = os.getenv("REFRESH_TOKEN")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
AUTHORIZATION = os.getenv("AUTHORIZATION")


def get_current_time_formatted():
    current_time = time.localtime()
    formatted_time = time.strftime('%y-%m-%d %H:%M:%S', current_time)
    return formatted_time

def get_access_token():
    url = "https://api.imgur.com/oauth2/token"
    payload = {'refresh_token': REFRESH_TOKEN,
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET,
    'grant_type': 'refresh_token'}
    files=[

    ]
    headers = {
    'Authorization': AUTHORIZATION
    }

    response = requests.request("POST", url, headers=headers, data=payload, files=files)
    access_token = response.json().get("access_token")
    print("access_token:",access_token)
    return access_token

def post_image(file_path,title = get_current_time_formatted() ,description = "post at "+get_current_time_formatted()):
    url = "https://api.imgur.com/3/image"

    payload = {'type': 'image',
    'title': title,
    'description': description}

    headers = {
    'Authorization': AUTHORIZATION
    }
    
    try:
        with open(file_path, 'rb') as file:
            # files=[('image',(os.path.basename(file_path),open(file_path,'rb'),'image/jpeg'))]
            files = {'image': (os.path.basename(file_path), file, 'image/jpeg')}

            response = requests.request("POST", url, headers=headers, data=payload, files=files)
            if response.status_code == 200:
                link = response.json().get("data").get("link")
                print("Upload successful. Link:", link)
                return link
            else:
                print(f"Failed to upload image. Status code: {response.status_code}")
                return None

    except (FileNotFoundError, PermissionError) as e:
        print("檔案錯誤",e)
        return None

if __name__ == "__main__":
    formatted_current_time = get_current_time_formatted()
    print("Formatted Current Time:", formatted_current_time)
    # access_token = get_access_token()
    post_image("D:\Pictures_J\T1228\下操場.jpg")