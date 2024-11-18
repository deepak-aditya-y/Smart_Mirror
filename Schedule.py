import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import datetime

# Define the scope for Google Calendar API
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
TOKEN_FILE = "Security/token.json"  # Path to store token inside the Security folder


def get_credentials():
    """Function to get credentials, re-authenticate if necessary."""
    creds = None
    # Check if token file exists in Security folder, and load it if valid
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    # If credentials are not valid or expired, re-authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())  # Try refreshing the token
            except Exception as e:
                print(f"Error refreshing token: {e}")
                creds = None  # If refresh fails, we will re-authenticate
        if not creds:
            # If no credentials are available or refreshed, initiate new authentication flow
            flow = InstalledAppFlow.from_client_secrets_file("Security/Calender_Credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
            # Save credentials for the next time
            with open(TOKEN_FILE, "w") as token:
                token.write(creds.to_json())

    return creds


def get_schedule_for_today():
    """Function to get and return the schedule of events for the current day from Google Calendar."""
    try:
        creds = get_credentials()  # Get valid credentials
        # Initialize the Calendar API service
        service = build("calendar", "v3", credentials=creds)

        # Get today's date
        today_date = datetime.datetime.now().date()
        time_min = f"{today_date.isoformat()}T00:00:00Z"
        time_max = f"{today_date.isoformat()}T23:59:59Z"

        # Retrieve events for the specified date from Google Calendar
        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])

        if not events:
            return f"No events found for {today_date}."

        # Return the events for the current day
        event_list = []
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            event_time = datetime.datetime.fromisoformat(start.replace("Z", "+00:00"))
            event_summary = event["summary"]
            event_info = f"At {event_time.strftime('%I:%M %p')}, {event_summary}"
            event_list.append(event_info)

        return event_list

    except HttpError as error:
        return f"An error occurred: {error}"


# Run the function and print the result
if __name__ == "__main__":
    schedule = get_schedule_for_today()
    if isinstance(schedule, list):
        print("Today's Schedule:")
        for event in schedule:
            print(event)
    else:
        print(schedule)  # This handles the case if no events are found or an error occurs
