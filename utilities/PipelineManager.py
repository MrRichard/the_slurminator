import os
import json
import xml.etree.ElementTree as ET
from utilities.SlurmWorkflowManager import SlurmWorkflowManager

class PipelineManager:
    def __init__(self, json_file: str, xml_file: str, subject_dir: str = "."):
        self.default_values = {}
        self.specific_values = {}
        self.user_params = {}
        
        self.logs = os.path.join(subject_dir, 'logs')
        self.batches = os.path.join(subject_dir, 'jobs')
        
        self.workflow_manager = SlurmWorkflowManager(
            batch_file_dir=self.batches,
            logs_dir=self.logs
        )
        
        self.load_default_values(json_file)
        self.load_specific_values(xml_file)

    # Load default pipeline file
    def load_default_values(self, json_file: str):
        with open(json_file, 'r') as file:
            self.default_values = json.load(file)

    # Load specific XNAT XML file for pipeline
    def load_specific_values(self, xml_file: str):
        tree = ET.parse(xml_file)
        root = tree.getroot()
        self.specific_values = {child.tag: child.text for child in root}
        
    def set_user_params(self, params: dict):
        self.user_params.update(params)

    def create_pipeline(self):
        # Combine all parameters
        combined_params = {**self.default_values, **self.specific_values, **self.user_params}
        
        # Create and configure the workflow
        previous_job_id = None
        
        for job in combined_params['jobs']:
            
            job_id = self.workflow_manager.add_job(
                job_name=job['name'],
                job_type=job['type'],
                script_path=job['script'],
                params={},
                dependencies=[previous_job_id]
            )
            
            slurm_params = self.default_values.get('default_slurm_params', {}).copy()
            slurm_params.update(job.get('slurm_params', {}))
            self.workflow_manager.set_slurm_params(job_id, slurm_params)
            
            self.workflow_manager.set_modules(job_id, job.get('modules', []))
            
            previous_job_id = job_id
        
        self.workflow_manager.create_workflow()
        
        