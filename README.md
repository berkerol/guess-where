# Guess Where

[![Sonarcloud Status](https://sonarcloud.io/api/project_badges/measure?project=berkerol_guess-where&metric=alert_status)](https://sonarcloud.io/dashboard?id=berkerol_guess-where)
[![CI](https://github.com/berkerol/guess-where/actions/workflows/lint_and_test_and_build.yml/badge.svg?branch=master)](https://github.com/berkerol/guess-where/actions/workflows/lint_and_test_and_build.yml)
[![contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)](https://github.com/berkerol/guess-where/issues)
[![license](https://img.shields.io/badge/license-GNU%20GPL%20v3.0-blue.svg)](https://github.com/berkerol/guess-where/blob/master/LICENSE)

Try to guess the location of random photo.

## Overview

A random photo is chosen and shown for 5 seconds (configurable) then you need to enter your guess and you will have 2 seconds (configurable) to see result then it continues with another photo. As statistics, it also shows correct and total number of guesses and current and highest streak. Made with [tkinter](https://docs.python.org/3/library/tkinter.html). Inspired by [GeoGuessr](https://www.geoguessr.com).

## Installation & Usage

```sh
pipenv install
pipenv shell # without this you can also do: pipenv run python3 guess_where.py
python3 guess_where.py
```

### Testing

Test everything: `pytest`

Test stuff that doesn't require actual files on disk and S3: `pytest test_get_guess_name.py`

You need to run the second, since other tests use my current directories.

Game loop (main method) is tested manually.

## Prerequisites

AWS CLI should be [configured](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html) to use S3.

## Photo Structure

Photos can only be read if they are structured in a specific way.

### Directories by city as last directory

`{PATH}/{COUNTRY}/{CITY}/**/{PHOTO}.jpg`

City directory name should be guessed. `{COUNTRY}` **DOESN'T** have to be country, it can be anything. It is just my current setup. `**` in between can contain any number of directories from 0 to N.

### Directory by city as last element

`{PATH}/{DATE} - {ORDER} - {COUNTRY} - {CITY}/**/{PHOTO}.jpg`

City name should be guessed. `{DATE} - {ORDER} - {COUNTRY}` part **DOESN'T** have to be in that structure as long as elements are separated with ` - ` and city is the last element. It is just my current setup. `**` in between can contain any number of directories from 0 to N.

## Photo Source

Photos can be read from either local disk or from S3 bucket.

### Local disk

Choose the directory that contains photo directories in choose directory popup.

### S3 Bucket

Use with or without prefix, for example `s3://{BUCKET}` or `s3://{BUCKET}/{PREFIX}/`

There must be a directory between bucket and photo directories in your structure, for example `s3://{BUCKET}/Photos/{COUNTRY}/{CITY}/**/{PHOTO}.jpg` or `s3://{BUCKET}/Photos 2/{DATE} - {ORDER} - {COUNTRY} - {CITY}/**/{PHOTO}.jpg`

Photos need to be downloaded before they can be viewed. They are downloaded to `/home/{LOGIN}/Pictures/Guess Where/`

## References

* [boto3 S3](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html)
* [Pillow](https://pillow.readthedocs.io/en/stable)

## Continous Integration

It is setup using GitHub Actions in `lint` and `test` jobs in `.github/workflows/lint_and_test_and_build.yml`

## Continuous Delivery

Releases with executables for Windows, MacOS and Linux are published automatically (when a new tag is created) using GitHub Actions in `build` job in `.github/workflows/lint_and_test_and_build.yml`

## Contribution

Feel free to [contribute](https://github.com/berkerol/guess-where/issues).

## Distribution

You can distribute this software freely under [GNU GPL v3.0](https://github.com/berkerol/guess-where/blob/master/LICENSE).
