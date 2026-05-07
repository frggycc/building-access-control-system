## Registered Card List
<img width="1033" height="300" alt="image" src="https://github.com/user-attachments/assets/fe72764a-35de-4372-ade0-acab8db4c232" />

This shows the current card registry. When Lambda sends the query to the database, this is the table the query targets to either return an entry or return null. In the latter case, it will indicate to Lambda that the card is unknown and unregistered.

## Logs of Scans
<img width="1801" height="336" alt="image" src="https://github.com/user-attachments/assets/966c0807-c99b-4494-8afe-cee01b59c174" />

This table shows the access logs for each scan that the badge reader read. It presents 4 of the 5 possible cases for a card being scanned to the reader. 
<img width="973" height="311" alt="image" src="https://github.com/user-attachments/assets/42f2500f-dd4b-43fe-89cf-b9228c0796a0" />

1. Alice: Passes all four conditions
2. Bob: Fails the "access level" condition
3. Carol: Fails the "activation" condition
4. Unknown: Fails the "registered cards" condition

The only condition not shown is the one where access is denied because the scan was performed outside the *allowed_hours* assigned to the user of the register card. To showcase that, I temporarily set Alice's *allowed_hours* to one that would fail when I scanned the card. That can be seen here:
<img width="939" height="42" alt="image" src="https://github.com/user-attachments/assets/16f8c139-06bf-4b66-a407-17c56d220927" />
<img width="1538" height="40" alt="image" src="https://github.com/user-attachments/assets/0735265b-a47e-4109-be1d-704f7956465a" />

