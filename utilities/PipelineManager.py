import json
import xml.etree.ElementTree as ET
from SlurmWorkflowManager import SlurmWorkflowManager

class PipelineManager:
    def __init__(self, json_file: str, xml_file: str):
        self.default_values = {}
        self.specific_values = {}
        self.user_params = {}
        self.workflow_manager = SlurmWorkflowManager()
        self.load_default_values(json_file)
        self.load_specific_values(xml_file)

    def load_default_values(self, json_file: str):
        with open(json_file, 'r') as file:
            self.default_values = json.load(file)

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
        self.workflow_manager.create_workflow(combined_params)

# Example usage
if __name__ == "__main__":
    # Initialize the pipeline manager with JSON and XML files
    pipeline_manager = PipelineManager(json_file='default_values.json', xml_file='specific_values.xml')

    # Load default values and specific variables
    pipeline_manager.load_default_values('default_values.json')
    pipeline_manager.load_specific_values('specific_values.xml')

    # Set additional user parameters
    user_params = {
        'additional_param1': 'value1',
        'additional_param2': 'value2'
    }
    pipeline_manager.set_user_params(user_params)

    # Create the pipeline and generate the workflow
    pipeline_manager.create_pipeline()