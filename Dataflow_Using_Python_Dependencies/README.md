## LAUNCHING PYTHON DATAFLOW PIPELINES USING ([following official tutorial here](https://beam.apache.org/documentation/sdks/python-pipeline-dependencies/#multiple-file-dependencies):
### 1. PyPI dependencies with requirement files. Bear in mind that [many dependencies are already pre-installed](https://cloud.google.com/dataflow/docs/concepts/sdk-worker-dependencies)
### 2. Local or Non-PyPI dependencies
### 3. Multi File Dependencies

--------

### Pre-Setup

In our examples below we'll run a Dataflow Pipeline which will be reading from PubSub, do some basic
transformation on our data (using the python libraries we'll install) and finally writing our data to BigQuery.

To run our pipeline we need to have `apache-beam[gcp]` package installed. Create a virtual environment and install the packages:

```bash
virtualenv -p python3 py3env_beam 
source py3env_beam/bin/activate
pip install apache-beam[gcp]
```

Be aware that the previous will create a virtual environment using Python3, which is still not fully supported for Apache Beam.
It will work for these examples, but if you want to add additional functionalities or use some other Beam IOs they may not work.

Now we'll create our PubSub topic and BigQuery table (modify the following environment variables to your particular case): 

```bash
export PROJECT=<your-project-name>
export DATASET=dataflow_test_dataset
export TABLE=pubsub_bq_table
bq mk ${DATASET}
bq mk ${DATASET}.${TABLE} case_id:INTEGER,post:STRING,comment:BOOLEAN

export TOPIC=pubsub-bq-topic
gcloud pubsub topics create ${TOPIC}
```

# 1. PYPI dependencies using requirements.txt file

To run a pipeline that makes use of PyPI packages simply add the flag `--requirements_file=requirements.txt`, 
where your `requirements.txt` file contains the packages to be installed. In this case we'll only install Pandas Package:
> requirements.txt
```
pandas==0.24.2
```

It is actually installed by default in Dataflow Workers (at least for PythonSDK 2.11), but this is for demonstration purposes only.
Code in `pubsub_input_bq_output_pipy_dep.py` will deploy a pipeline reading from PubSub, doing some transformation to the data 
using our installed Pandas package and finally writing to BQ. 

Run the pipeline with the following command:
```bash
export GCS_BUCKET=billing-bucket-vgea
export JOB_NAME=pubstobqreq-only-pandas 
python pubsub_input_bq_output_pipy_dep.py --job_name=${JOB_NAME} --requirements_file=requirements.txt --runner=DataflowRunner --temp_location=gs://${GCS_BUCKET}/temp --streaming --input_topic projects/${PROJECT}/topics/${TOPIC} --table=${TABLE} --dataset=${DATASET} --project_id=${PROJECT} 
```

If you check the logs you will eventually see some logging like:

```python
Executing: /usr/local/bin/pip install -r /var/opt/google/staged/requirements.txt
Building wheels for collected packages: pandas
Building wheel for pandas (setup.py): still running..
Successfully installed pandas-0.24.2
```

This means your the pandas package has been successfully installed. Now you can publish a message:

```bash
gcloud pubsub topics publish pubsub-bq-topic --message "[{'case_id':465,'post':'','comment':True}]"
```

# 2. Local or Non-PyPI dependencies

First let's create some Non-PyPI dependencies:
- Our Non-PyPI module is in folder `nonpypimodule`. It has the following structure:

```tree
nonpypimodule
├── setup.py
└── nonpypimodule
   └── __init__.py
```

Enter to the first `nonpypimodule` directory and run command:

Run command below, which will create a `dist` folder and a package's tarball. Tarball path will be added to the `--extra-package` flag  when running our pipeline.
```bash
python setup.py sdist
```

Run code in `pubsub_input_bq_output_non_pipy_dep.py`  with command:
```bash
export JOB_NAME=pubstobqreq-non-pypi
python pubsub_input_bq_output_non_pipy_dep.py --job_name=${JOB_NAME} --extra_package=<paht-to-nonpypi-tarball>/nonpypimodule/dist/nonpypimodule-0.1.tar.gz --runner=DataflowRunner --temp_location=gs://${GCS_BUCKET}/temp --streaming --input_topic projects/${PROJECT}/topics/${TOPIC} --table=${TABLE} --dataset=${DATASET} --project_id=${PROJECT} 
```

If you check the logs you will eventually see some logging like:

```python
Downloading: gs://billing-bucket-vgea/temp/pubstobqreq-non-pypi.1554717408.856450/nonpypimodule2-0.0.0.tar.gz to /var/opt/google/tmp/download.0.641644710/file.0 (size: 0 Kb, MD5: Ou48TOCEfsG7KubvEVZHiw==)
Installing extra package: nonpypimodule2-0.0.0.tar.gz
Building wheel for nonpypimodule2 (setup.py): started
Successfully installed nonpypimodule2-0.0.0
```

This means your non-PyPI package has been successfully installed. Now you can publish a message:

```bash
gcloud pubsub topics publish pubsub-bq-topic --message "[{'case_id':123,'post':'asfca','comment':True}]"
```

# 3. Multi File Dependencies  

For this example we have first created two Non-PyPI libraries. We'll work with contents in `python_packaging/` folder. There we have two Non-PyPI modules, a `setup.py` file to install them and our python file for running the pipeline: `pubsub_input_bq_output_non_pipy_multifiledependencies.py`


To run our pipeline we'll add the `--setup_file` flag pointing to our `setup.py` path.
```bash
export JOB_NAME=pubstobqreq-non-pypi-multidependencies
python pubsub_input_bq_output_non_pipy_multifiledependencies.py --job_name ${JOB_NAME} --setup_file /<path-to-setup-file>/setup.py --runner=DataflowRunner --temp_location=gs://${GCS_BUCKET}/temp --streaming --input_topic projects/${PROJECT}/topics/${TOPIC} --table=${TABLE} --dataset=${DATASET} --project_id=${PROJECT}
```

If you check the logs you will eventually see some logging like:

```python
Building wheel for additional-packages (setup.py): started
Building wheel for additional-packages (setup.py): finished with status 'done'
Successfully installed additional-packages-0.1
```

This means your non-PyPI packages have been successfully installed. Now you can publish a message:

```bash
gcloud pubsub topics publish pubsub-bq-topic --message "[{'case_id':313,'post':'aasdfsfca','comment':True}]"
```

# CLEAN-UP

To avoid incurring charges to your GCP account for the resources used in this tutorial, don't forget to delete all the resources created:
- Dataflow pipelines, PubSub topic, BigQuery table and dataset, GCS bucket.
