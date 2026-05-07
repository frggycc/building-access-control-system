import json, boto3, uuid, os
from datetime import datetime, timezone
import zoneinfo

dynamodb = boto3.resource('dynamodb')
iot_data = boto3.client('iot-data',
    endpoint_url=f"https://{os.environ['IOT_ENDPOINT']}")

CARDS_TABLE = dynamodb.Table('building_authorized_cards')
LOG_TABLE   = dynamodb.Table('building_access_log')

def lambda_handler(event, context):
    card_uid  = str(event.get('card_uid', ''))
    reader_id = event.get('reader_id', 'unknown')
    location  = event.get('location',  'unknown')
    timestamp = int(event.get('timestamp', 0))

    decision, reason, cardholder = evaluate_access(card_uid, location, timestamp)
    log_event(card_uid, cardholder, reader_id, location, decision, reason, timestamp)
    publish_decision(reader_id, decision)

    print(f'[{decision}] card={card_uid} cardholder={cardholder} reason={reason}')
    return {'decision': decision, 'reason': reason}


def evaluate_access(card_uid, location, timestamp):
    """Returns (decision, reason, cardholder_name)."""
    try:
        resp = CARDS_TABLE.get_item(Key={'card_uid': card_uid})
        card = resp.get('Item')

        if not card:
            return 'DENIED', 'unknown_card', 'Unknown'

        cardholder = card.get('cardholder', 'Unknown')

        if not card.get('active', False):
            return 'DENIED', 'card_deactivated', cardholder

        allowed = card.get('access_level', [])
        if location not in allowed and 'all' not in allowed:
            return 'DENIED', 'insufficient_access_level', cardholder

        hours_str = card.get('allowed_hours', '00:00-23:59')
        start_str, end_str = hours_str.split('-')
        sh, sm = map(int, start_str.split(':'))
        eh, em = map(int, end_str.split(':'))
        LOCAL_TZ = zoneinfo.ZoneInfo('America/Los_Angeles')
        now = datetime.fromtimestamp(timestamp, tz=LOCAL_TZ)
        current_min = now.hour * 60 + now.minute
        start_min = sh * 60 + sm
        end_min = eh * 60 + em

        if start_min <= end_min:
            in_window = start_min <= current_min <= end_min
        else:
            in_window = current_min >= start_min or current_min <= end_min
        if not in_window:
            return 'DENIED', 'outside_allowed_hours', cardholder

        return 'GRANTED', None, cardholder

    except Exception as e:
        print(f'ERROR: {e}')
        return 'DENIED', 'system_error', 'Unknown'


def log_event(card_uid, cardholder, reader_id, location, decision, reason, timestamp):
    """Write event to audit log including cardholder name and human-readable time."""
    # Convert Unix timestamp to human readable format
    dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
    readable_time = dt.strftime('%Y-%m-%d %H:%M:%S UTC')

    LOG_TABLE.put_item(Item={
        'event_id':     str(uuid.uuid4()),
        'timestamp':    timestamp,
        'date_time':    readable_time,
        'card_uid':     card_uid,
        'cardholder':   cardholder,
        'reader_id':    reader_id,
        'location':     location,
        'decision':     decision,
        'reason':       reason or 'access_granted'
    })


def publish_decision(reader_id, decision):
    iot_data.publish(
        topic='building/access/decision',
        qos=1,
        payload=json.dumps({'reader_id': reader_id, 'decision': decision})
    )
