# clay-ifttt - IFTTT Webhook Trigger CLI

Trigger IFTTT webhooks from the command line to connect Clay to thousands of services.

## What It Does

IFTTT (If This Then That) connects to 600+ services. This tool lets Clay trigger any IFTTT applet via webhook — opening up notifications, smart home control, reminders, and more.

## Why It Matters

Clay already has:
- Voice announcements (clay-voice)
- Camera snapshots (clay-camera)
- Presence detection (clay-presence-monitor)
- Home Assistant control

**clay-ifttt** adds:
- Push notifications to your phone
- SMS alerts
- Smart home triggers (lights, plugs, locks)
- Calendar events
- Note-taking (Evernote, Notion)
- And 600+ more services

## Setup

### 1. Get Your IFTTT Key

1. Go to https://ifttt.com/maker_webhooks
2. Click "Documentation" (top right)
3. Copy your key (it's in the URL after `key=`)

### 2. Configure Clay

```bash
# Set your IFTTT key
python3 tools/clay_ifttt.py set-key YOUR_IFTTT_KEY

# Test the connection
python3 tools/clay_ifttt.py test
```

### 3. Create Applets

Go to https://ifttt.com/create and create applets:
- **If** → Webhook (Receive a web request) → Event name: `phone_alert`
- **Then** → Notifications (Send a notification)

## Usage

```bash
# Trigger an event with values
python3 tools/clay_ifttt.py trigger phone_alert "Hello from Clay!"

# With multiple values
python3 tools/clay_ifttt.py trigger door_opened "Front door" "Robb" "10:30 AM"

# Add a named event for easy reuse
python3 tools/clay_ifttt.py add notification "https://maker.ifttt.com/trigger/notify/with/key/xxx"

# List all configured events
python3 tools/clay_ifttt.py list

# Remove an event
python3 tools/clay_ifttt.py remove notification
```

## Example Applets

### Push Notification
- **If:** Webhook `push` → **Then:** Notifications → "Send notification"
- **Values:** `{{Value1}}` = Title, `{{Value2}}` = Message

### SMS Alert
- **If:** Webhook `sms` → **Then:** SMS → "Send SMS"
- **Values:** `{{Value1}}` = Message

### Light Flash (Smart Home)
- **If:** Webhook `light_flash` → **Then:** Your smart light
- Use for visual alerts when voice might not be heard

### Add to Calendar
- **If:** Webhook `calendar_event` → **Then:** Google Calendar
- **Values:** `{{Value1}}` = Title, `{{Value2}}` = Date/Time

### Add to Todoist
- **If:** Webhook `todo` → **Then:** Todoist
- **Values:** `{{Value1}}` = Task title

## Use Cases

```bash
# Morning briefing - send summary to phone
python3 tools/clay_ifttt.py trigger morning_brief "Weather: 72°F" "Calendar: 2 events"

# Alert when package detected
python3 tools/clay_ifttt.py trigger package_alert "Package at door" "Front camera"

# Reminder integration
python3 tools/clay_ifttt.py trigger reminder "Buy milk" "High"

# Location-based triggers
python3 tools/clay_ifttt.py trigger leaving_work "Left office" "ETA: 25 min"
```

## Files

- `clay_ifttt.py` - Main CLI tool
- `requirements.txt` - Dependencies
- `README.md` - This file

## Requirements

```bash
pip install -r requirements.txt
```

## Notes

- IFTTT has rate limits (~100 requests/hour for free tier)
- Webhook URLs contain your key — don't share publicly
- Values are passed to IFTTT as `value1`, `value2`, `value3`
- Use `{{Value1}}`, `{{Value2}}`, `{{Value3}}` in your applets
