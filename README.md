# 🎵 Automated-Music-Data-ETL-Analytics-Pipeline---using-python


> **Project in Brief**
>
> The goal is to build an **ETL pipeline** that automatically collects and processes trending music data (e.g., global top songs from Spotify) every week. Over time, this will create a dataset that can help your client (a music label) **analyze patterns in popular music** (e.g., genres, artists, song structures) and potentially guide their own production.

---

## 🔹 Architecture Overview

`Spotify API → Lambda Extract → Raw S3 → Lambda Transform → Processed S3 → Glue → Athena`

![Architecture diagram](<img width="948" height="556" alt="image" src="https://github.com/user-attachments/assets/be12784a-2340-41ac-b519-4667902faacf" />
)

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









