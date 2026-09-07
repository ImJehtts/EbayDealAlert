# AWS eBay Deal Alert
This Project is a serverless deal-alert app for eBay: you set a keyword, a max price, and (optionally) a category, and it watches eBay for matching listings and emails you when a new one shows up. 

## Video Demo

It's a fully serverless AWS backend behind a React frontend. A CRUD API (API Gateway + Lambda + DynamoDB) lets users create, list, and delete alerts. A scheduled Lambda (EventBridge Scheduler) polls the eBay Browse API for every active alert, deduplicates matches against previously-seen items in DynamoDB (with TTL-based cleanup), and batches new hits into a single email per alert via SES. The frontend is a static React app served from S3 through CloudFront.

## AWS Services used
AWS Lambda, API Gateway (HTTP API), DynamoDB, EventBridge Scheduler, SES, SSM Parameter Store, S3, CloudFront, IAM, React (Vite), eBay API

## Key Decisions 

## Known Limitations/What's Next?
