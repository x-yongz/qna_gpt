def google_calendar_function():
    return [
        {
            "type": "function",
            "function": {
                "name": "get_details",
                "description": "Get the information needed to create a new calendar event",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "summary": {
                            "type": "string",
                            "description": "Title of event"
                        },
                        "location": {
                            "type": "string",
                            "description": "Location/address of event"
                        },
                        "start": {
                            "type": "string",
                            "description": "RFC3339 string of the starting datetime with offset, default Singapore time"
                        },
                        "end": {
                            "type": "string",
                            "description": "RFC3339 string of the ending datetime with offset, default Singapore time"
                        },
                        "timeZone": {
                            "type": "string",
                            "description": "IANA Time Zone Database name, default Singapore time"
                        },
                        "allDay": {
                            "type": "string",
                            "enum": ["yes", "no"],
                            "description": "Flag to indicate if its an all day event, assume its all day if time not provided"                            
                        }
                    },
                    "required": ["summary", "start", "end", "allDay"]
                },
            }
        }
    ]
