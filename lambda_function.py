import json
import boto3
import gzip
import base64
from datetime import datetime

# DynamoDB & SNS setup
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('yourtablename')

sns = boto3.client('sns')
sns_topic_arn = 'yoursnslink'

def lambda_handler(event, context):
    print("🛡️ Lambda triggered — log monitoring started.")

    # CloudWatch logs subscription delivers compressed data
    if 'awslogs' not in event:
        print("⚠️ ERROR: Invalid event. No awslogs data received.")
        return {'statusCode': 400, 'body': 'Invalid event'}

    # Decode and decompress
    compressed_payload = base64.b64decode(event['awslogs']['data'])
    decompressed_payload = gzip.decompress(compressed_payload)
    logs_data = json.loads(decompressed_payload)

    print(f"🔍 Received {len(logs_data['logEvents'])} log events.")

    # Process each log event
    for log_event in logs_data['logEvents']:
        log = json.loads(log_event['message'])

        event_name = log.get('eventName', 'UnknownEvent')
        user_identity = log.get('userIdentity', {})
        user = user_identity.get('userName', 'UnknownUser')
        source_ip = log.get('sourceIPAddress', 'UnknownIP')
        region = log.get('awsRegion', 'UnknownRegion')
        time = log.get('eventTime', str(datetime.now()))

        # Suspicion checks
        if region in ['cn-north-1', 'ru-central1']:
            threat_level = 'HIGH'
            reason = 'Suspicious region access'
        elif user_identity.get('type') == 'Root':
            threat_level = 'CRITICAL'
            reason = 'Root account used'
        else:
            continue  # Not suspicious

        print(f"🚨 THREAT DETECTED: {event_name} by {user} from {region}")

        # Save to DynamoDB
        table.put_item(Item={
            'eventTime': time,
            'user': user,
            'event': event_name,
            'ip': source_ip,
            'region': region,
            'threatLevel': threat_level,
            'reason': reason
        })
        print("💾 Incident stored in DynamoDB.")

        # Send SNS Alert
        sns.publish(
            TopicArn=sns_topic_arn,
            Subject=f"🚨 {threat_level} Threat Detected",
            Message=f"""
Security Alert:
Event: {event_name}
User: {user}
IP: {source_ip}
Region: {region}
Time: {time}
Reason: {reason}
            """
        )
        print("📧 SNS Alert sent.")

    return {'statusCode': 200, 'body': 'Log analysis complete'}
