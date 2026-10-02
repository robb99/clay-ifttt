#!/usr/bin/env python3
"""
clay-ifttt - IFTTT Webhook Trigger CLI

Trigger IFTTT webhooks to connect Clay to thousands of services.

Usage:
    python3 clay_ifttt.py trigger <event> [value1] [value2] [value3]
    python3 clay_ifttt.py add <event> <webhook_url>
    python3 clay_ifttt.py list
    python3 clay_ifttt.py remove <event>
    python3 clay_ifttt.py test

Examples:
    python3 clay_ifttt.py trigger phone_notification "Hello" "From Clay"
    python3 clay_ifttt.py add my_event "https://maker.ifttt.com/trigger/my_event/with/key/xxx"
    python3 clay_ifttt.py list
"""

import argparse
import json
import os
import sys
import requests
from pathlib import Path

CONFIG_DIR = Path.home() / ".clay"
CONFIG_FILE = CONFIG_DIR / "ifttt.json"

# Default IFTTT config
DEFAULT_CONFIG = {
    "webhooks": {},
    "default_key": None
}


def load_config():
    """Load IFTTT configuration."""
    if not CONFIG_FILE.exists():
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()
    
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)


def save_config(config):
    """Save IFTTT configuration."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)


def parse_webhook_url(url):
    """Extract event name and key from webhook URL."""
    # URL format: https://maker.ifttt.com/trigger/{event}/with/key/{key}
    parts = url.strip('/').split('/')
    try:
        key_idx = parts.index('with') + 2
        key = parts[key_idx]
        
        # Find the trigger part
        trigger_idx = parts.index('trigger') + 1
        event = parts[trigger_idx]
        
        return event, key
    except (ValueError, IndexError):
        return None, None


def build_webhook_url(event, key=None):
    """Build webhook URL from event and key."""
    if key:
        return f"https://maker.ifttt.com/trigger/{event}/with/key/{key}"
    return f"https://maker.ifttt.com/trigger/{event}/with/key/YOUR_IFTTT_KEY"


def trigger_webhook(event, value1=None, value2=None, value3=None, key=None):
    """Trigger an IFTTT webhook."""
    config = load_config()
    
    # Get key from config or parameter
    if not key:
        key = config.get('default_key')
    
    if not key:
        print("Error: No IFTTT key configured. Run 'clay_ifttt.py set-key <key>'")
        return False
    
    # Build URL
    url = f"https://maker.ifttt.com/trigger/{event}/with/key/{key}"
    
    # Build payload
    payload = {}
    if value1:
        payload['value1'] = value1
    if value2:
        payload['value2'] = value2
    if value3:
        payload['value3'] = value3
    
    try:
        response = requests.post(url, json=payload if payload else None, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ Successfully triggered '{event}'")
            if payload:
                print(f"   Values: {payload}")
            return True
        elif response.status_code == 429:
            print(f"⏳ Rate limited. Wait before triggering again.")
            return False
        else:
            print(f"❌ Failed to trigger '{event}': {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return False


def add_event(name, webhook_url, make_default=False):
    """Add a named event with webhook URL."""
    config = load_config()
    
    # Extract key from URL if provided
    event, key = parse_webhook_url(webhook_url)
    
    if key and not config.get('default_key'):
        config['default_key'] = key
        print(f"🔑 Set default IFTTT key from URL")
    
    config['webhooks'][name] = webhook_url
    
    if make_default:
        if not key:
            print("⚠️  No key found in URL, cannot set as default")
        else:
            config['default_key'] = key
    
    save_config(config)
    print(f"✅ Added event '{name}' -> {webhook_url}")
    return True


def list_events():
    """List all configured events."""
    config = load_config()
    
    if not config['webhooks']:
        print("No events configured.")
        print("  Add one: clay_ifttt.py add <name> <webhook_url>")
        return
    
    print(f"Configured IFTTT Events ({len(config['webhooks'])}):")
    print("-" * 50)
    
    for name, url in config['webhooks'].items():
        # Mask the key
        masked_url = url[:60] + "..." if len(url) > 60 else url
        print(f"  {name}: {masked_url}")
    
    if config.get('default_key'):
        print(f"\n🔑 Default key: {config['default_key'][:10]}...")


def remove_event(name):
    """Remove a configured event."""
    config = load_config()
    
    if name in config['webhooks']:
        del config['webhooks'][name]
        save_config(config)
        print(f"✅ Removed event '{name}'")
        return True
    else:
        print(f"❌ Event '{name}' not found")
        return False


def set_key(key):
    """Set the default IFTTT key."""
    config = load_config()
    config['default_key'] = key
    save_config(config)
    print(f"✅ Set default IFTTT key: {key[:10]}...")


def test_connection():
    """Test IFTTT connection."""
    config = load_config()
    key = config.get('default_key')
    
    if not key:
        print("❌ No IFTTT key configured")
        print("   Run: clay_ifttt.py set-key YOUR_IFTTT_KEY")
        return False
    
    # Try to trigger a test event
    url = f"https://maker.ifttt.com/trigger/test/with/key/{key}"
    
    try:
        response = requests.post(url, json={"value1": "Clay test"}, timeout=10)
        
        if response.status_code == 200:
            print("✅ IFTTT connection working!")
            return True
        elif response.status_code == 404:
            print("⚠️  Connection OK, but 'test' event doesn't exist in IFTTT")
            print("   Create a test applet at: https://ifttt.com/create")
            return True
        else:
            print(f"❌ IFTTT returned: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection failed: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='clay-ifttt - Trigger IFTTT webhooks from CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s trigger phone_notification "Hello from Clay!"
  %(prog)s add my_event "https://maker.ifttt.com/trigger/my_event/with/key/xxx"
  %(prog)s list
  %(prog)s set-key your_ifttt_key
  %(prog)s test

Setup:
  1. Go to https://ifttt.com/maker_webhooks
  2. Copy your key (click "Documentation")
  3. Run: %(prog)s set-key YOUR_KEY
  4. Create applets at https://ifttt.com/create
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # trigger command
    trigger_parser = subparsers.add_parser('trigger', help='Trigger an IFTTT event')
    trigger_parser.add_argument('event', help='Event name to trigger')
    trigger_parser.add_argument('value1', nargs='?', default=None, help='Value 1')
    trigger_parser.add_argument('value2', nargs='?', default=None, help='Value 2')
    trigger_parser.add_argument('value3', nargs='?', default=None, help='Value 3')
    trigger_parser.add_argument('--key', '-k', help='IFTTT key (overrides config)')
    
    # add command
    add_parser = subparsers.add_parser('add', help='Add a named event')
    add_parser.add_argument('name', help='Event name')
    add_parser.add_argument('url', help='Webhook URL')
    add_parser.add_argument('--default', '-d', action='store_true', help='Set as default key')
    
    # list command
    subparsers.add_parser('list', help='List configured events')
    
    # remove command
    remove_parser = subparsers.add_parser('remove', help='Remove an event')
    remove_parser.add_argument('name', help='Event name to remove')
    
    # set-key command
    key_parser = subparsers.add_parser('set-key', help='Set default IFTTT key')
    key_parser.add_argument('key', help='IFTTT webhook key')
    
    # test command
    subparsers.add_parser('test', help='Test IFTTT connection')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    if args.command == 'trigger':
        success = trigger_webhook(args.event, args.value1, args.value2, args.value3, args.key)
        return 0 if success else 1
    
    elif args.command == 'add':
        add_event(args.name, args.url, args.default)
        return 0
    
    elif args.command == 'list':
        list_events()
        return 0
    
    elif args.command == 'remove':
        success = remove_event(args.name)
        return 0 if success else 1
    
    elif args.command == 'set-key':
        set_key(args.key)
        return 0
    
    elif args.command == 'test':
        success = test_connection()
        return 0 if success else 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
