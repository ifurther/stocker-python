# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START drive_quickstart]
from __future__ import print_function
import os.path
import io
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.file','https://www.googleapis.com/auth/drive.appdata','https://www.googleapis.com/auth/drive.readonly']

def main():
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('drive', 'v3', credentials=creds)

    # Call the Drive v3 API
    results = service.files().list(
        q="mimeType = 'application/vnd.google-apps.folder'", pageSize=10, fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])
    stock_dir=[item for item in items if item['name'] == "twstock"][0]
    print("id: {}, fold_name:{}".format(stock_dir['name'],stock_dir['id']))

    results = service.files().list(
        q="'{}' in parents".format(stock_dir['id']), pageSize=10, fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])

    if not items:
        print('No files found.')
    else:
        print('Files:')
        for item in items:
            print(u'{0} ({1})'.format(item['name'], item['id']))
     
    stock_db=[item for item in items if item['name'] == "twstock.db"][0]
    print("id: {}, fold_name:{}".format(stock_db['name'],stock_db['id']))
    request = service.files().get_media(fileId=stock_db['id'])
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print("Download %d%%." % int(status.progress() * 100))

        fh.seek(0)
        with open(os.path.join(stock_db['name']), 'wb') as f:
            f.write(fh.read())
            f.close()
    response = service.files().list(spaces='appDataFolder',
                                          fields='nextPageToken, files(id, name)',
                                          pageSize=10).execute()
    for file in response.get('files', []):
        # Process change
        print('Found file: %s (%s)' % (file.get('name'), file.get('id')))

if __name__ == '__main__':
    main()
# [END drive_quickstart]
