# similar-day-forecasting-vae

Research project into using Variational Auto-Encoders to do similar-day forecasting of electricity demand in the NEM.

## Setup

Due to the wide variety in options for managing virtual environments, we leave it up to the user to create and activate your virtual environment.

```bash
$ make requirements; make dotenv; make init;
```

## Data pipeline

Use `nem-data` to download raw AEMO data and put into `DATAHOME/raw`

```bash
$ make dl
```

Run the data processing pipeline into `DATAHOME/processed` & the baselines into `DATAHOME/final`:

```bash
$ make pipe
```

## Streamlit app

```bash
$ make app
```
