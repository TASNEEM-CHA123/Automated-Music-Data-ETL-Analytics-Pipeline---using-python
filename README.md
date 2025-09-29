# 🎵 Automated-Music-Data-ETL-Analytics-Pipeline---using-python


> **Project in Brief**
>
> The goal is to build an **ETL pipeline** that automatically collects and processes trending music data (e.g., global top songs from Spotify) every week. Over time, this will create a dataset that can help your client (a music label) **analyze patterns in popular music** (e.g., genres, artists, song structures) and potentially guide their own production.

---

## 🔹 Architecture Overview

`Spotify API → Lambda Extract → Raw S3 → Lambda Transform → Processed S3 → Glue → Athena`

![Architecture diagram](assets/architecture.png)

> Brief: A Lambda-based, serverless pipeline that extracts playlist data from Spotify, stores raw JSON in S3, triggers a second Lambda to transform and persist cleaned Parquet/CSV artifacts, catalogs them with Glue, and enables SQL analytics through Athena.

---

## 🔹 ETL Pipeline Components

### 1. Extract

* **Source:** Spotify API (use Spotipy or any preferred Python client).
* **Implementation:** Python script running inside **AWS Lambda**.
* **Scheduling:** CloudWatch Events (EventBridge) scheduled rule — weekly trigger.
* **Output:** Raw JSON files written to `s3://<bucket>/raw/spotify/<YYYY-MM-DD>/playlist.json`.

**Important environment variables** for the extractor Lambda:

```
SPOTIPY_CLIENT_ID=<your_client_id>
SPOTIPY_CLIENT_SECRET=<your_client_secret>
SPOTIPY_REDIRECT_URI=https://example.com/callback
S3_BUCKET=<your_bucket>
PLAYLIST_ID=<spotify_playlist_id_or_env_override>
```

### 2. Transform

* **Trigger:** S3 `ObjectCreated` event on the `raw/spotify/` prefix.
* **Job:** Lambda function reads JSON, cleans and normalizes data into tables (songs, artists, albums, track_features, playlist_metadata).
* **Output formats:** Parquet (preferred for analytics) and/or CSV, written to `s3://<bucket>/processed/spotify/<table>/year=YYYY/month=MM/day=DD/`.

Example transform tasks:

* Flatten nested JSON for artists and album details.
* Normalize numeric columns (popularity, duration_ms).
* Enrich tracks with audio features (via Spotify audio-features endpoint) and compute derived columns (e.g., duration_min).

### 3. Load (Catalog + Query)

* **Glue Crawler** scans the `processed/spotify/` prefix and infers table schemas.
* **Glue Data Catalog** stores table metadata.
* **Amazon Athena** is used to run SQL queries and build analytics dashboards over S3 data.

Example Athena query — Top 10 artists by average popularity in the last 6 months:

```sql
WITH recent_tracks AS (
  SELECT *, date_parse(date, '%Y-%m-%d') AS track_date
  FROM spotify_tracks
  WHERE track_date >= date_add('month', -6, current_date)
)
SELECT artist_name, avg(popularity) AS avg_pop
FROM recent_tracks
GROUP BY artist_name
ORDER BY avg_pop DESC
LIMIT 10;
```

---

## 🔹 Folder structure (suggested)

```
├── README.md
├── extractor/
│   ├── lambda_function.py
│   ├── requirements.txt
│   └── README.md
├── transformer/
│   ├── lambda_function.py
│   ├── requirements.txt
│   └── README.md
├── infra/
│   ├── sam-template.yaml   # or cloudformation / terraform modules
│   └── deploy.sh
├── analytics/
│   ├── athena-queries.sql
│   └── notebooks/
└── assets/
    ├── architecture.png
    └── sample_output.png
```

---

## 🔹 Example Lambda Extractor (handler sketch)

```python
# extractor/lambda_function.py
import os
import json
import boto3
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials

s3 = boto3.client('s3')

def lambda_handler(event, context):
    client_id = os.environ['SPOTIPY_CLIENT_ID']
    client_secret = os.environ['SPOTIPY_CLIENT_SECRET']
    playlist_id = os.environ.get('PLAYLIST_ID')
    bucket = os.environ['S3_BUCKET']

    auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp = Spotify(auth_manager=auth_manager)

    playlist = sp.playlist(playlist_id)
    key = f"raw/spotify/{context.aws_request_id}/playlist.json"
    s3.put_object(Bucket=bucket, Key=key, Body=json.dumps(playlist))

    return {"statusCode": 200, "body": key}
```

---

## 🔹 Suggested IAM Permissions (minimum)

* **Extractor Lambda**:

  * `s3:PutObject` on the raw prefix
  * `logs:CreateLogGroup`, `logs:CreateLogStream`, `logs:PutLogEvents`
* **Transformer Lambda**:

  * `s3:GetObject` on raw prefix
  * `s3:PutObject` on processed prefix
  * `glue:CreateTable`, `glue:UpdateTable` (if managing catalog programmatically)
* **Glue Crawler**: permissions to read processed prefix and write to Glue Data Catalog
* **Athena**: permissions to read from S3 processed prefix and to run queries

---

## 🔹 Deployment / Infra options

* Use **AWS SAM** or **Serverless Framework** to package and deploy Lambdas, deploy CloudWatch rules and S3 notifications.
* Alternatively, use **Terraform** or native CloudFormation templates.

Example SAM snippet for scheduled extractor (infra/sam-template.yaml):

```yaml
Resources:
  SpotifyExtractor:
    Type: AWS::Serverless::Function
    Properties:
      Handler: lambda_function.lambda_handler
      Runtime: python3.11
      Environment:
        Variables:
          S3_BUCKET: !Ref DataBucket
          SPOTIPY_CLIENT_ID: 'REPLACE_ME'
          SPOTIPY_CLIENT_SECRET: 'REPLACE_ME'
      Events:
        WeeklyTrigger:
          Type: Schedule
          Properties:
            Schedule: rate(7 days)
```

---

## 🔹 Observability & Cost

* Enable CloudWatch logs and set retention (e.g., 30 days).
* Use CloudWatch metrics and alarms on Lambda errors and duration.
* Parquet + partitioning reduces Athena query costs and improves performance.

---

## 🔹 Sample Athena queries / analytics ideas

* Trend genres over time (`GROUP BY genre, month`)
* Average energy / danceability for top tracks vs non-top tracks
* Artist churn rate — new vs returning artists in the weekly top playlist

---

## 🔹 Images & Assets

Place your images in `assets/` and reference them in the README. Example filenames used above:

* `assets/architecture.png` — architecture diagram (recommended size: 1200×600)
* `assets/sample_output.png` — sample query screenshot (recommended size: 1000×600)

---

## 🔹 Contributing

Contributions welcome — open issues and PRs. Please include tests for transformer logic and keep Lambda package sizes small (use Lambda layers if needed).

---

## 🔹 License

MIT © Your Name

---

## 🔹 Contact

Project maintainer — `your.email@example.com`

*Generated README for the Weekly Spotify Trending ETL Pipeline. Replace placeholders and secrets before deploying.*
