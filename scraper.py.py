import os.path
import time

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1aO7RSbX-o2XP4c4tXVkBlCQxK-GGjTpIX6YEYqmNhbg'
SAMPLE_RANGE_NAME = 'Sheet1!A2:A15'


def get_values(spreadsheet_id, range_name):
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
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
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('sheets', 'v4', credentials=creds)

        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id, range=range_name).execute()
        rows = result.get('values', [])
        print(f"{len(rows)} rows retrieved")
        return result
    except HttpError as error:
        print(f"An error occurred: {error}")
        return error


def update_values(spreadsheet_id, range_name, value_input_option,
                  _values):
    """
    Creates the batch_update the user has access to.
    Load pre-authorized user credentials from the environment.
    TODO(developer) - See https://developers.google.com/identity
    for guides on implementing OAuth2 for the application.
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
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    # pylint: disable=maybe-no-member
    try:

        service = build('sheets', 'v4', credentials=creds)
        values = _values
        body = {
            'values': values
        }
        result = service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id, range=range_name,
            valueInputOption=value_input_option, body=body).execute()
        print(f"{result.get('updatedCells')} cells updated.")
        return result
    except HttpError as error:
        print(f"An error occurred: {error}")
        return error



options = Options()

options.headless = True

driver = webdriver.Chrome("/usr/bin/chromedriver", options=options)

def leet_scraper(profiles):
    l = []

    for profile in profiles:
        try:
            driver.get(f"https://leetcode.com/{profile[0]}/")

            time.sleep(10)
            problem = driver.find_element("xpath", "//a[starts-with(@href, '/submissions')]/div/span[1]").text
            time_solved = driver.find_element("xpath", "//a[starts-with(@href, '/submissions')]/div/span[2]").text
            max_streak = driver.find_element("xpath", "//*[contains(text(), 'Max streak')]/../span[2]").text

            easy_problems = int(driver.find_element("xpath", "//*[contains(text(), 'Easy')]/../div[2]").text.split("\n/")[0])
            medium_problems = int(driver.find_element("xpath", "//*[contains(text(), 'Medium')]/../div[2]").text.split("\n/")[0])
            hard_problems = int(driver.find_element("xpath", "//*[contains(text(), 'Hard')]/../div[2]").text.split("\n/")[0])

            last_solved = time_solved.split(" ")
            status = "Active"
            if last_solved[1] == "month":
                status = "Not Active"
            elif last_solved[1] in ["minutes", "hours"]:
                pass
            elif last_solved[0].isdigit() and int(last_solved[0]) > 10:
                status = "Not Active"
            
            total_solved = easy_problems + medium_problems + hard_problems

            l.append([problem, time_solved, max_streak, easy_problems, medium_problems, hard_problems, total_solved, status])
        except Exception as err:
            print(err)

    return l


if __name__ == '__main__':
    while True:
        l = get_values(SAMPLE_SPREADSHEET_ID, SAMPLE_RANGE_NAME)
    
        solutions = leet_scraper(l['values'])
        print(solutions)
        # # Pass: spreadsheet_id,  range_name, value_input_option and  _values
        update_values("1aO7RSbX-o2XP4c4tXVkBlCQxK-GGjTpIX6YEYqmNhbg",
                    "Sheet1!B2:I15", "USER_ENTERED",
                    solutions)


        time.sleep(300)