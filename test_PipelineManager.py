from utilities.PipelineManager import PipelineManager

def main():
    # Initialize the pipeline manager with JSON and XML files
    pipeline_manager = PipelineManager(
        json_file='sample_pipeline_config.json', 
        xml_file='sample_xnat_output.xml',
        subject_dir='/isilon/datalake/riipl/original/pipeline/the_slurminator/test_subject'
    )

    # # Set additional user parameters if needed
    # user_params = {
    #     'additional_param1': 'value1',
    #     'additional_param2': 'value2'
    # }
    # pipeline_manager.set_user_params(user_params)

    # # Create the pipeline and generate the workflow
    pipeline_manager.create_pipeline()

if __name__ == "__main__":
    main()