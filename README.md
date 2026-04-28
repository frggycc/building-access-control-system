# Building Access Control System Setup Guide
This repository will serve as a tutorial on setting up the AWS side of this system. For assistance with setting up the hardware portion of the system, refer to external resources, as the setup and requirements differ slightly between Raspberry Pi machines. 

You can also refer to the following tutorials:
* [Reading and Writing RFID Cards with Raspberry Pi](https://admantium.medium.com/reading-and-writing-rfid-cards-with-raspberry-pi-eaf042617c61)
* [Raspberry Pi RFID Tutorial](https://www.sunfounder.com/blogs/news/raspberry-pi-rfid-tutorial-setup-wiring-and-projects-for-beginners?srsltid=AfmBOooPJaidPO0oPqtZhli71AXHEjwFSrdDTy92xi4zjuhLcQMW8f5F)
---
# AWS Account and IAM Admin User
## Create an AWS Account
If you haven't already, go to aws.amazon.com and create an account. AWS offers a free tier where AWS gives a new user a 6-month trial with $100 in credets to use with their service.

To avoid exceeding the cost of your credits, you can set a budget alert using the Billing and Cost Management service.
1. On the left side menu of the service, click *Budgets*
2. On the top, click *Create budget*
3. Select *Use a template* and choose the *Monthly cost budget* template
4. Name the budget however you like and set a monthly limit alongside alerts for when the services exceed that limit

## Create an IAM Admin User
You will create a project admin user. This user will be the primary account used to set up all AWS services for this project.
