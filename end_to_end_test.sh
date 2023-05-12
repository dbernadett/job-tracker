#!/usr/bin/bash
rm -rf staging
mkdir staging
python3 src/job_search.py -c staging init
python3 src/job_search.py -c staging add "https://getcruise.com/careers/jobs/2449571/"
python3 src/job_search.py -c staging mark_applied 1 --resume_used distributed
python3 src/job_search.py -c staging list
