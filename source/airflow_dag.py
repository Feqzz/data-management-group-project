# [START import_module]
from datetime import timedelta, datetime
from textwrap import dedent

# The DAG object; we'll need this to instantiate a DAG
from airflow import DAG

# Operators; we need this to operate!
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from airflow.models.baseoperator import chain

# user defined functions
from tasks import extract_data_from_apis
from tasks import transform_data_to_lod
from tasks import build_cloud
from tasks import restart_fuseki
from tasks import restart_lodview

# [END import_module]

# [START default_args]
# These args will get passed on to each operator
# You can override them on a per-task basis during operator initialization
default_args = {
        'owner': 'airflow',
        'depends_on_past': False,
        'email': ['norpark@gmail.com'],
        'email_on_failure': False,
        'email_on_retry': False,
        'retries': 1,
        'retry_delay': timedelta(minutes=1),
        'end_date': datetime(2023, 1, 1),
}
# [END default_args]

# [START instantiate_dag]
with DAG(
        'ParkingPipelineDAG',
        default_args=default_args,
        description='Pipeline for converting data to linked open data and republishing it',
        schedule_interval=timedelta(days=1),
        start_date=datetime(2021, 9, 11),
        tags=['parkingpipeline'],
) as dag:
        # [END instantiate_dag]

        # t1, t2 and t3 are examples of tasks created by instantiating operators
        # [START basic_task]
        task1 = PythonOperator(
                task_id='extract_data',
                python_callable=extract_data_from_apis,
                retries=3
        )

        task2 = PythonOperator(
                task_id='transform_data_to_lod',
                python_callable=transform_data_to_lod,
                retries=3,
        )

        task3 = PythonOperator(
                task_id='restart_fuseki',
                python_callable=restart_fuseki,
                retries=3,
        )

        task4 = PythonOperator(
                task_id='restart_lodview',
                python_callable=restart_lodview,
                retries=3,
        )

        task5 = PythonOperator(
                task_id='build_cloud',
                python_callable=build_cloud,
                retries=3,
        )

        # [END basic_task]

        # [START documentation]
        task1.doc_md = dedent(
                """\
                #### Task Documentation
                You can document your task using the attributes `doc_md` (markdown),
                `doc` (plain text), `doc_rst`, `doc_json`, `doc_yaml` which gets
                rendered in the UI's Task Instance Details page.
                ![img](http://montcs.bloomu.edu/~bobmon/Semesters/2012-01/491/import%20soul.png)

                """
        )

        dag.doc_md = __doc__  # providing that you have a docstring at the beggining of the DAG
        dag.doc_md = """
    This is a documentation placed anywhere
        """  # otherwise, type it like this
        # [END documentation]
        # [END ParkingPipelineDag]


        # [START dependency ]

        # chain(task1, task2, [task3, task5, task6], [task4])
        task1 >> task2 >> task3 >> task4 >> task5

        # [END dependency ]

