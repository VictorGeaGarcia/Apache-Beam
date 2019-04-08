import argparse
import logging
import re

import pandas as pd 

from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.options.pipeline_options import SetupOptions
import apache_beam as beam
from apache_beam.io import ReadFromText
from apache_beam.io import WriteToText

from apache_beam.io.gcp.bigquery import WriteToBigQuery
from apache_beam.io.gcp.pubsub import ReadFromPubSub

def run(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_topic',
                        dest='input_topic',
                        help='Input topic in the form projects/<project>/topics/<topic>')
    parser.add_argument('--output',
                        dest='output_file',
                        help='Output file where to write')
    parser.add_argument('--table',
                        dest='table_name',
                        help='BQ table name')
    parser.add_argument('--dataset',
                        dest='dataset_id',
                        help='BQ dataset')
    parser.add_argument('--project_id',
                        dest='project_id',
                        help='Project ID')
    known_args, pipeline_args = parser.parse_known_args(argv)
    pipeline_args.extend(['--project=main-training-project','--streaming'])
    """
    pipeline_args.extend(['--runner=DataflowRunner',
                             '--project=yourprojectid',
                             '--staging_location=gs://yourgsbucket',
                             '--temp_location=gs://yourgsbucket',
                         '--job_name=your-job-name'])
    """
    pipeline_options = PipelineOptions(pipeline_args)
    #pipeline_options.view_as(SetupOptions).save_main_session = True
    

    with beam.Pipeline(options = pipeline_options) as p:
        lines = p | ReadFromPubSub(topic=known_args.input_topic)
 
        def str_to_dict(str_line):
            import pandas as pd
            import nonpypimodule
            import changecommentfield

            df_rows = eval(str_line)
            pd.DataFrame.from_dict(df_rows)
            bq_rows = eval(re.sub('\[|\]','',str_line.decode('utf-8')))
            bq_rows['post'] = nonpypimodule.return_sentence()
            bq_rows = changecommentfield.change_field(bq_rows)
            logging.info(bq_rows)
            return bq_rows
        
        lines = lines | 'String to dict' >> beam.Map(str_to_dict)
        lines = lines | 'Output to BQ' >> WriteToBigQuery(table =
                                                         known_args.table_name,
                                                        dataset =
                                                         known_args.dataset_id,
                                                         project=known_args.project_id)


if __name__=='__main__':
    logging.getLogger().setLevel(logging.INFO)
    run()
