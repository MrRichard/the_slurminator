import os
import secrets

class SlurmWorkflowManager:
    """
    A class to manage SLURM workflow jobs.

    Attributes:
    -----------
    jobs : list
        A list to store job details.
    workflow : list
        A list to store the order of job IDs in the workflow.
    """

    def __init__(self, batch_file_dir: str = ".", logs_dir: str = "./logs"):
        """
        Initializes the SlurmWorkflowManager with empty jobs and workflow lists.

        Parameters:
        -----------
        batch_file_dir : str, optional
            The directory where batch files will be created (default is current directory).
        logs_dir : str, optional
            The directory where logs will be saved (default is ./logs).
        """
        self.jobs = []
        self.workflow = []
        
        self.batch_file_dir = batch_file_dir
        if not os.path.exists(self.batch_file_dir):
            os.makedirs(self.batch_file_dir)
        
        self.logs_dir = logs_dir
        if not os.path.exists(self.logs_dir):
            os.makedirs(self.logs_dir)
            
    def _generate_unique_job_id(self):
        """
        Generates a unique 7-character HEX string for job identification.

        Returns:
        --------
        str
            A unique 7-character HEX string.
        """
        return secrets.token_hex(3)  # 3 bytes = 6 hex characters, plus 1 for uniqueness

    def add_job(self, job_name:str, job_type: str, script_path: str, params: dict, dependencies: list = []):
        """
        Adds a job to the workflow.

        Parameters:
        -----------
        job_type : str
            The type of the job (e.g., 'singularity').
        script_path : str
            The path to the job script.
        params : dict
            A dictionary of SLURM parameters for the job.
        dependencies : list, optional
            A list of job IDs that this job depends on (default is an empty list).
        """
        job_id = self._generate_unique_job_id()
        job = {
            'id': f"{job_name}_{job_id}",
            'type': job_type,
            'script_path': script_path,
            'params': params,
            'dependencies': dependencies,
            'modules': [],
            'singularity': None
        }
        self.jobs.append(job)
        self.workflow.append(job_id)
        
        return job['id']

    def set_slurm_params(self, job_id: int, params: dict):
        """
        Sets or updates SLURM parameters for a specific job.

        Parameters:
        -----------
        job_id : int
            The ID of the job to update.
        params : dict
            A dictionary of SLURM parameters to set or update.
        """
        for job in self.jobs:
            if job['id'] == job_id:
                job['params'].update(params)
                break

    def set_modules(self, job_id: int, modules: list):
        """
        Sets the modules to load for a specific job.

        Parameters:
        -----------
        job_id : int
            The ID of the job to update.
        modules : list
            A list of modules to load.
        """
        for job in self.jobs:
            if job['id'] == job_id:
                job['modules'] = modules
                break

    def set_singularity_params(self, job_id: int, container: str, bind_paths: list):
        """
        Sets the Singularity container parameters for a specific job.

        Parameters:
        -----------
        job_id : int
            The ID of the job to update.
        container : str
            The path to the Singularity container.
        bind_paths : list
            A list of paths to bind to the container.
        """
        for job in self.jobs:
            if job['id'] == job_id:
                job['singularity'] = {
                    'container': container,
                    'bind_paths': bind_paths
                }
                break

    def generate_batch_file(self, job_id: int):
        """
        Generates a SLURM batch file for a specific job.

        Parameters:
        -----------
        job_id : int
            The ID of the job to generate the batch file for.
        """
        for job in self.jobs:
            if job['id'] == job_id:
                batch_file_content = self._create_batch_file_content(job)
                batch_file_path = f"{self.batch_file_dir}/job_{job_id}.slurm"
                with open(batch_file_path, "w") as f:
                    f.write(batch_file_content)
                break

    def create_workflow(self):
        """
        Generates batch files for all jobs in the workflow.
        """
        for job in self.jobs:
            self.generate_batch_file(job['id'])

    def _create_batch_file_content(self, job):
        """
        Creates the content for a SLURM batch file.

        Parameters:
        -----------
        job : dict
            The job dictionary containing job details.

        Returns:
        --------
        str
            The content of the SLURM batch file.
        """
        
        params = job['params']
        log_file = f"{self.logs_dir}/job_{job['id']}.log"
        lines = [
            f"#!/bin/bash",
            f"#SBATCH --job-name={job['id']}",
            f"#SBATCH --cpus-per-task={params.get('cpus', 1)}",
            f"#SBATCH --mem={params.get('mem', '1G')}",
            f"#SBATCH --time={params.get('runtime', '1:00:00')}",
            f"#SBATCH --partition={params.get('partition', 'defq')}",
            f"#SBATCH --output={log_file}",
            f"#SBATCH --error={log_file}"
        ]
        
        if job['dependencies']:
            for dep in job['dependencies']:
                if dep:
                    if isinstance(dep, list):
                        dependency_str = ":".join(dep)
                    else:
                        dependency_str = dep
                    lines.append(f"#SBATCH --dependency=afterok:{dependency_str}")

        if 'env_vars' in params:
            for var, value in params['env_vars'].items():
                lines.append(f"export {var}={value}")

        if job['modules']:
            for module in job['modules']:
                lines.append(f"module load {module}")

        if job['type'] == 'singularity' and job['singularity']:
            singularity_cmd = f"singularity exec --bind {','.join(job['singularity']['bind_paths'])} {job['singularity']['container']} {job['script_path']}"
            lines.append(singularity_cmd)
        elif job['type'] == 'matlab':
            matlab_cmd = f"matlab -nodisplay -nosplash -r \"{job['script_path']}('target_path', options_struct); exit;\""
            lines.append(matlab_cmd)
        elif job['type'] == 'bash':
            bash_cmd = f"bash {job['script_path']}"
            lines.append(bash_cmd)
        elif job['type'] == 'python':
            python_cmd = f"python3 {job['script_path']} command_arg1 arg2 arg3"
            lines.append(python_cmd)
        else:
            lines.append(f"{job['script_path']}")

        return "\n".join(lines)
    
    def submit_job(self, job_id: int):
        """
        Submits a job to the SLURM workload manager.

        Parameters:
        -----------
        job_id : int
            The ID of the job to submit.
        """
        batch_file_path = f"{self.batch_file_dir}/job_{job_id}.slurm"
        os.system(f"sbatch {batch_file_path}")

    def submit_all_jobs(self):
        """
        Submits all jobs in the workflow to the SLURM workload manager.
        """
        for job_id in self.workflow:
            self.submit_job(job_id)