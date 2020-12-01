# similar-day-forecasting-vae

Research project into using Variational Auto-Encoders to do similar-day forecasting of electricity demand in the NEM.

## Setup

Due to the wide variety in options for managing virtual environments, we leave it up to the user to create and activate your virtual environment.

```bash
$ make requirements; make dotenv; make init;
```

## Data pipeline

```bash
$ make dl
$ make pipe
```

## Use

```bash
$ make app
```
