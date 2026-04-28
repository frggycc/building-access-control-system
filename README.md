# Building Access Control System - Setup Guide
This repository will serve as a tutorial on setting up the AWS side of this system. For assistance with setting up the hardware portion of the system, refer to external resources, as the setup and requirements differ slightly between Raspberry Pi machines. 

You can also refer to the following tutorials:
* [Reading and Writing RFID Cards with Raspberry Pi](https://admantium.medium.com/reading-and-writing-rfid-cards-with-raspberry-pi-eaf042617c61)
* [Raspberry Pi RFID Tutorial](https://www.sunfounder.com/blogs/news/raspberry-pi-rfid-tutorial-setup-wiring-and-projects-for-beginners?srsltid=AfmBOooPJaidPO0oPqtZhli71AXHEjwFSrdDTy92xi4zjuhLcQMW8f5F)
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

