
# Chrobry Zastępstwa

A Messenger bot which notifies its users of substitutions at Bolesław I the Brave High School in Piotrków Trybunalski

https://chrobry-zastepstwa.vercel.app



## Features

- Fully automated data fetching
- Data filtering
- Administration dashboard
- Statistics


## Environment Variables


|Variable|Description|Required (bot)|Required (dashboard)
|---|---|---|---|
|DATABASE_URL|Database URL. Has to include username and password|yes|yes|
|ACCESS_TOKEN|Facebook API page access token|yes|yes|
|VERIFY_TOKEN|Facebook API webhhok verify token|yes|yes|
|CHECK_TOKEN|Custom token used to verify /bot/check endpoint|yes|yes|
|DASHBOARD_USERNAME|Dashboard username|no|yes|
|DASHBOARD_PASSWORD|Dashboard password|no|yes|
|CRONJOB_API_KEY|Cronjob.org API key|no|yes|
|CRONJOB_JOB_ID|Cronjob.org job ID trigerring /bot/check endpoint|no|yes|


## Database Setup
Before installing the application import necessary data to your database using database.sql file
## Installation

```bash
  git clone https://github.com/bartoszstepien01/Chrobry-Zast-pstwa
  cd Chrobry-Zast-pstwa
  pip install -r requirements.txt
  flask run
```  
## License

[MIT](https://choosealicense.com/licenses/mit/)

