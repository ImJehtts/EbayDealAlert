# AWS eBay Deal Alert
This Project is a serverless deal-alert app for eBay: you set a keyword, a max price, and (optionally) a category, and it watches eBay for matching listings and emails you when a new one shows up. 

[Link to Project (https://d3dbutpcivdhu3.cloudfront.net/)](https://d3dbutpcivdhu3.cloudfront.net/)

## Video Demo

It's a fully serverless AWS backend behind a React frontend. A CRUD API (API Gateway + Lambda + DynamoDB) lets users create, list, and delete alerts. A scheduled Lambda (EventBridge Scheduler) polls the eBay Browse API for every active alert, deduplicates matches against previously-seen items in DynamoDB (with TTL-based cleanup), and batches new hits into a single email per alert via SES. The frontend is a static React app served from S3 through CloudFront.

## AWS Diagram
<img width="952" height="689" alt="image" src="https://github.com/user-attachments/assets/47594de9-05a6-46f4-b19e-fc7aa68f8b2c" />

## AWS Services used
AWS Lambda, API Gateway (HTTP API), DynamoDB, EventBridge Scheduler, SES, SSM Parameter Store, S3, CloudFront, IAM, React (Vite), eBay API

## Key Decisions 
1. **Category selection at alert creation and not keyword-only search**: Searching for a phone model under a $300 cap returns chargers, cases, and more. eBay's CATEGORY_REFINEMENTS filters the axis that actually separates a phone from a phone case. The refinements call happens once at alert creation, not per scan and all following scans will only look for listings returned in the category wanted.
2. **Serverless over EC2**: The workload runs a few seconds every four hours. An always-on server bills 24/7 to be idle 99.9% of the time. Lambdas are also kept out of a VPC on purpose: nothing here lives in a private network, and a VPC'd Lambda needing outbound internet requires a NAT Gateway.
3. **Four Lambdas with separate IAM roles, not one router Lambda**: A single proxy Lambda would need the union of every permission, so a bug in the create path would run with delete rights. Separate functions mean listAlerts holds only dynamodb:Query and deleteAlert only dynamodb:DeleteItem.
4. **Console-first, not Infrastructure as Code**: Built through the console to learn what the resources are. Having had no experience in AWS, using the console made it easier to learn what the services do, how they interact, and made it easier to resolve any problems I ran into.

## Known Limitations/What's Next?
1. **Authentication**: Currently users can only use the email that is hardcoded and provided. Plan to add Cognito authentication so I can start working towards authentication and users being able to use their verified email address and keep track of their own alerts.
2. **Email deliverability**: Currently, the SES is in sandbox. Planning to move it to production so users can use their own addresses, can make use of the authentication from the first fix, and have a verified domain to prevent alerts being sent to spam folder.
3. **Unsubscribing**: Currently users can not unsubscribe from alerts using the email and have to use the site. The fix is adding an unsubscribe option in the email.
4. **Pricing accuracy**: Currently there is no minimum pricing and shipping is not factored into the price. These changes will allow for more accurate results.
5. **Multi-Category alerts**: Users can only add a single category maximum to their alerts and this will allow them to add more to broaden their search
6. **Email only**: Adding SMS Support to provide both Email via SES and SMS via SNS.
