# 🚨 AWS CloudTrail Threat Detection System

A fully serverless security monitoring solution that detects suspicious activities in your AWS environment using CloudTrail, CloudWatch, AWS Lambda, DynamoDB, and SNS. Automatically sends real-time email alerts for potential threats and stores incidents for auditing.

---

## 📌 Project Overview

This system monitors AWS account activities in real-time and detects:

* Suspicious logins from other regions (China, Russia).
* Usage of AWS root account.
* Other customizable suspicious activities.

When a threat is detected:

* The incident is stored in DynamoDB.
* An email alert is sent via Amazon SNS.

---

## 📊 Architecture Diagram

```
[ CloudTrail ]
      ↓
[ CloudWatch Log Group ]
      ↓ (Subscription Filter)
[ AWS Lambda (ThreatAnalyzer) ]
      ↓                    ↓
[DynamoDB (SecurityIncidents)]      [SNS (SecurityAlerts)]
```

---

## ⚙️ AWS Services Used

| Service         | Purpose                                                  |
| --------------- | -------------------------------------------------------- |
| AWS CloudTrail  | Captures all AWS account activities (logins, API calls). |
| CloudWatch Logs | Collects CloudTrail logs for processing.                 |
| Lambda Function | Analyzes logs for suspicious events in real-time.        |
| DynamoDB Table  | Stores detected incidents for auditing.                  |
| SNS Topic       | Sends real-time email alerts.                            |

---

## 🚀 Features

* 📡 Real-time monitoring of AWS account activity.
* 🔐 Detection of:

  * Logins from suspicious regions.
  * Root account usage.
* 📬 Instant email alerts.
* 🗄️ Incident storage in DynamoDB.
* 🛠️ 100% serverless, auto-scalable solution.

---

## 📦 DynamoDB Table – `SecurityIncidents`

| Field       | Description                      |
| ----------- | -------------------------------- |
| eventTime   | Time of event (Primary Key).     |
| user        | IAM user involved.               |
| event       | Name of AWS event.               |
| ip          | Source IP address.               |
| region      | AWS region where event occurred. |
| threatLevel | HIGH / CRITICAL.                 |
| reason      | Reason for flagging as a threat. |

---

## 📧 SNS Topic – `SecurityAlerts`

* Sends real-time email alerts for each detected threat.
* Subscription required (confirmation email must be accepted).

---

## 🛠️ Setup Instructions (Step-by-Step)

### 1️⃣ Create DynamoDB Table

* Go to **AWS Console** → **DynamoDB** → **Tables** → **Create Table**.
* Table name: `SecurityIncidents`.
* Partition key: `eventTime` (Type: String).
* Click **Create**.

---

### 2️⃣ Create SNS Topic (Email Alerts)

* Go to **SNS** → **Topics** → **Create Topic**.
* Type: **Standard**.
* Name: `SecurityAlerts`.
* Click **Create**.
* Inside the topic:
  * Click **Create Subscription**.
  * Protocol: **Email**.
  * Endpoint: Your email address.
  * Confirm the subscription via your email inbox.

---

### 3️⃣ Deploy Lambda Function (`ThreatAnalyzer`)

* Go to **AWS Lambda** → **Create Function**.
* Author from scratch:
  * Name: `ThreatAnalyzer`.
  * Runtime: Python 3.12+.
* Paste the Lambda code and set:
  * `SecurityIncidents` as DynamoDB Table.
  * SNS Topic ARN from your topic.
* Deploy the function.

---

### 4️⃣ Assign Lambda Permissions

* In Lambda → **Configuration** → **Permissions**.
* Open the execution role.
* Attach:
  * `AmazonDynamoDBFullAccess`
  * `AmazonSNSFullAccess`
  * `AWSLambdaBasicExecutionRole`

---

### 5️⃣ Configure CloudTrail Log Group

* Go to **CloudTrail**:
  * Ensure your account has an active Trail.
  * Logs must be forwarded to **CloudWatch Logs**.
* Note the Log Group (e.g., `/aws/cloudtrail/logs`).

---

### 6️⃣ Create Subscription Filter (CloudWatch to Lambda)

* Go to **CloudWatch** → **Logs** → **Log Groups**.
* Select your CloudTrail Log Group.
* Go to **Subscription Filters** → **Create**.
* Destination: **Lambda Function** (`ThreatAnalyzer`).
* Filter Pattern: (leave blank to capture all logs).
* Create the filter.

---

### 7️⃣ Testing & Monitoring

* Trigger AWS activity (logins, API calls, etc.).
* Lambda will auto-trigger upon new CloudTrail logs.
* Check:
  * **CloudWatch Logs** (Lambda function).
  * **DynamoDB** (`SecurityIncidents` table).
  * **SNS Email Alerts**.

---

## 📩 Sample log file

```
------aws-log
{
  "awslogs": {
    "data": "H4sIAAAAAAAAAGVQwW7jMBC951cMMl..."
  }
}
------- After decode data
{
  "messageType": "DATA_MESSAGE",
  "owner": "123456789012",
  "logGroup": "/aws/cloudtrail/logs",
  "logStream": "123456789012_CloudTrail_ap-south-1",
  "logEvents": [
        {
      "id": "e1",
      "timestamp": 1734829292000,
      "message": "{\"eventName\":\"ConsoleLogin\",\"userIdentity\":{\"type\":\"IAMUser\",\"userName\":\"Admin\"},\"sourceIPAddress\":\"203.0.113.25\",\"awsRegion\":\"us-east-1\",\"eventTime\":\"2025-08-21T10:34:52Z\"}"
    },
    {
      "id": "e2",
      "timestamp": 1734829305000,
      "message": "{\"eventName\":\"DeleteBucket\",\"userIdentity\":{\"type\":\"IAMUser\",\"userName\":\"TestUser\"},\"sourceIPAddress\":\"198.51.100.10\",\"awsRegion\":\"cn-north-1\",\"eventTime\":\"2025-08-21T10:35:05Z\"}"
    },
    {
      "id": "e3",
      "timestamp": 1734829317000,
      "message": "{\"eventName\":\"StartInstances\",\"userIdentity\":{\"type\":\"Root\"},\"sourceIPAddress\":\"192.0.2.44\",\"awsRegion\":\"ap-south-1\",\"eventTime\":\"2025-08-21T10:35:17Z\"}"
    }
  ]
}


```

## 📩 Sample Email file
```
Subject: 🚨 HIGH Threat Detected

Security Alert:
Event: ConsoleLogin
User: unknown
IP: 203.0.113.1
Region: cn-north-1
Time: 2025-07-14T12:30:00
Reason: Suspicious region access
```


## 👨‍💻 Built By

Muthuraj
AWS Security Enthusiast | Cloud Practitioner
