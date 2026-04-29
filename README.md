# Building Access Control System - Setup Guide
This repository will serve as a tutorial on setting up the AWS side of this system. For assistance with setting up the hardware portion of the system, refer to external resources, as the setup and requirements differ slightly between Raspberry Pi machines. 

You can also refer to the following tutorials:
* [Reading and Writing RFID Cards with Raspberry Pi](https://admantium.medium.com/reading-and-writing-rfid-cards-with-raspberry-pi-eaf042617c61)
* [Raspberry Pi RFID Tutorial](https://www.sunfounder.com/blogs/news/raspberry-pi-rfid-tutorial-setup-wiring-and-projects-for-beginners?srsltid=AfmBOooPJaidPO0oPqtZhli71AXHEjwFSrdDTy92xi4zjuhLcQMW8f5F)

### NOTE: As you follow through the tutorial, keep track of the ARNs as we implement each service
---
# AWS Account and IAM Admin User
## Create an AWS Account
If you haven't already, go to aws.amazon.com and create an account. AWS offers a free tier that gives new users a 6-month trial with $100 in credits to use across their services.

To avoid exceeding the cost of your credits, you can set a budget alert using the Billing and Cost Management service.
1. On the left side menu of the service, click **Budgets**
2. On the top, click **Create budget**
3. Select **Use a template** and choose the **Monthly cost budget** template
4. Name the budget however you like and set a monthly limit alongside alerts for when the services exceed that limit

## Create an IAM Admin User
<img width="1048" height="577" alt="image" src="https://github.com/user-attachments/assets/775cc894-d189-4a89-94ce-fc6c8d6c9056" />

You will create a project admin user. This user will be the primary account used to set up all AWS services for this project. It has access to all services but can be deleted by the root user in case the account is compromised.
1. As the root user, go to the **IAM** service -> **IAM Users**, and then **Create user**
2. Create a username for the new user (i.e. *project-admin*) and provide them with access to the AWS Console; Set up the password configurations to what you need, and hit next
3. Select **Attach policies directly**; Search and select the **AdministratorAccess** policy; Hit next
4. Hit **Create user** and download the credentials with **Download .csv file**

### [HIGHLY RECOMMENDED] Set up MFA for the user
<img width="1048" height="459" alt="image" src="https://github.com/user-attachments/assets/c0db7062-f254-4248-9a59-46039725fd7b" />

1. Go to IAM again -> IAM Users -> project-admin -> Security Credentials -> Assign MFA device
2. Use an MFA application on your phone like DUO or Google Authenticator

After the account has been set up, log out of root and log back in as *project-admin* for the remainder of the project

---
# Register the Raspberry Pi with AWS IoT Core
## Create an IoT Thing
<img width="1060" height="561" alt="image" src="https://github.com/user-attachments/assets/ebc0d4c6-4cf8-4a0e-a29d-6ff18f01b29b" />

This is where you will register your Raspberry Pi as an IoT device. You will need to create a new IoT Thing instance and then download several certificates into the Raspberry Pi. These certificates tell the IoT Core service that the Raspberry Pi is authorized to communicate with the service.
1. Go to the IoT Core service
2. On the left menu, under **Manage**, click **All devices** -> **Things** -> **Create things**
3. Choose to **Create single thing**
4. Enter an appropriate name for the RFID scanner (i.e. *rpi5-door-controller-01*); Hit next
5. Choose to **Auto-generate a new certificate** and hit next
6. **Create thing** without adding a policy (we'll create that next)
7. **! DO NOT MISS THIS STEP !** Download all the certificates and keys onto a USB so that you can transfer them to the Raspberry Pi

## Create an IoT Policy
<img width="1048" height="567" alt="image" src="https://github.com/user-attachments/assets/20eb2d31-9d73-422f-a8f7-84d58bbb6a8d" />

The policy for the IoT thing is to prevent several things from happening if the certificates or the system are stolen or compromised. The first is to restrict the certificate to the system; it cannot be used on any other machine. The second is to allow the badge reader to publish only to one topic, where scanned cards are sent to access AWS. Lastly, the final rule is that the badge reader can subscribe and receive the decision from the topic that receives the decision from Lambda.
1. Go to the IoT Core service
2. On the left menu, under **Manage**, click **Security** -> **Policies** -> **Create policy**
3. Name the policy something relevant (i.e. *building-door-controller-policy*)
4. Go to JSON view and paste the following (change the name of your resource when applicable)

```
{ 
	"Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "iot:Connect",
      "Resource": "arn:aws:iot:us-east-1:*:client/rpi5-door-controller-01"
    },
    {
      "Effect": "Allow",
      "Action": "iot:Publish",
      "Resource": "arn:aws:iot:us-east-1:*:topic/building/access/scan"
    },
    {
      "Effect": "Allow",
      "Action": "iot:Subscribe",
      "Resource": "arn:aws:iot:us-east-1:*:topicfilter/building/access/decision"
    },
    {
      "Effect": "Allow",
      "Action": "iot:Receive",
      "Resource": "arn:aws:iot:us-east-1:*:topic/building/access/decision"
    }
  ]
}
```

6. Go back to **Things** under **All devices** and select the badge Thing -> **Certificates** tab -> the **Certificate ID**
7. Under **Policies**, select **Attach policies** and choose the policy name that you just created

---
# Customer Managed Key
<img width="995" height="199" alt="image" src="https://github.com/user-attachments/assets/f82301d3-11bf-4e8c-a313-f2baf33bdae3" />

The next step is to create a key that can be used to encrypt and decrypt data at rest. So that includes your database, S3 archive, and CloudTrail logs.
1. Go to the Key Management Service (KMS) -> **Customer managed keys** -> **Create a key**
2. Choose to create a **Symmetric** key to use as a way to **Encrypt and decrypt**; Hit next
3. Choose an alias for the key (i.e. *building-access-cmk*); Hit next
4. For the key administrators, add the project-admin user that was created at the beginning of this guide; Hit next
5. Choose the same project-admin user for the key usage; Hit next again
6. Click next -> Finish

### [HIGHLY RECOMMENDED] Set up a key rotation schedule
<img width="982" height="221" alt="image" src="https://github.com/user-attachments/assets/32bfe42e-859b-493d-b29e-8a4fc80cc3a0" />

1. Go to KMS again -> **Customer managed keys** -> click the Key ID that we just created
2. Under the **Key material and rotations** tab, edit **Automatic key rotation** -> Enable -> Enter 365 -> Hit save

---
# DynamoDB
<img width="1079" height="277" alt="image" src="https://github.com/user-attachments/assets/ae974a2c-8469-4fbb-9e6f-d4ace96b18c8" />

DynamoDB is our choice for the database service. This part of the guide can be customized based on the attributes you need for your own badge reader. We'll be creating two tables; a table of authroized cards to register or delete RFID data and a table that will be used as a log to keep track of when a card gets scanned to the badge reader.
## Create a Card Registry Table
<img width="968" height="298" alt="image" src="https://github.com/user-attachments/assets/583eb71f-b451-4b62-a9ce-0305da8bcc57" />

We'll first build the table that will keep track of registered RFID cards/badges
1. Go to the DynamoDB service
2. On the left menu, go to **Tables** -> **Create Table**
3. Name the table something relevant to your card registry (i.e. *building_authorized_cards*)
4. For the partition key, use card_uid (String) with no Sort key
5. Customize settings -> Table class = **DynamoDB Standard** -> Read/write capacity settings = **On-demand**
6. Under **Encryption at rest**, choose the **Customer managed key** option and select the key that was created under the CMK portion of this guide
7. Click Create table and wait for the table to become **Active**
8. Now start adding items to your table by clicking your table ID and clicking **Create item**
9. It's up to you to decide what attribute to include in the table before adding your RFID cards/badges. For this project, I chose these attributes: 
card_uid (String), cardholder (String), access_level (List of Strings), allowed_hours (String, format HH:MM-HH:MM), active (Boolean)

## Create a Log Table
<img width="1462" height="342" alt="image" src="https://github.com/user-attachments/assets/022bde86-ac72-4b79-af85-e1932fb55f7e" />

1. Follow the same steps as the previous section (use the CMK, have capacity mode set to **On-demand**, etc), except name the partition key something more appropriate (i.e. *event_id* (String)) -> Click **Create table**
2. Start adding items to your table as you did in the previous section; Again, its up to you to decide what attributes ot include but this is what I chose:
event_uid (String), timestamp (Number), card_uid (String), cardholder (String), date_time (String), decision (DENIED, GRANTED), location (String), reader_id (String), reason (String)

---
# VPC Private Network
<img width="1641" height="788" alt="image" src="https://github.com/user-attachments/assets/c018eff6-1fcd-4233-b40c-0c00f3d929e8" />

By default, Lambda is unrestricted and has no network configuration. Meaning, Lambda could establish a connection to an external server, which we want to avoid. So we will create a Virtual Private Cloud for Lambda to deploy to. We'll dictate which AWS services Lambda can communicate with: DynamoDB, KMS, and IoT Core.

## Create the VPC and Subnets
## Create Security Groups
<img width="1269" height="498" alt="image" src="https://github.com/user-attachments/assets/c4c5851d-9cc2-48e7-8b66-b67c28660a42" />

## Create VPC Endpoints
## Create a NAT Gateway
