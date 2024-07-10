from CreateSlurmJob import SlurmWorkflowManager

# Initialize the workflow manager
workflow_manager = SlurmWorkflowManager("./tmp/")

# Add jobs to the workflow
workflow_manager.add_job(
    job_type='matlab',
    script_path='/path/to/matlab_script.m',
    params={'cpus': 4, 'mem': '16G', 'runtime': '2:00:00', 'partition': 'standard'},
    dependencies=[]
)

workflow_manager.add_job(
    job_type='bash',
    script_path='/path/to/bash_script.sh',
    params={'cpus': 2, 'mem': '8G', 'runtime': '1:00:00', 'partition': 'short'},
    dependencies=[1]
)

workflow_manager.add_job(
    job_type='python',
    script_path='/path/to/python_script.py',
    params={'cpus': 4, 'mem': '16G', 'runtime': '3:00:00', 'partition': 'standard'},
    dependencies=[2]
)

workflow_manager.add_job(
    job_type='singularity',
    script_path='/path/to/singularity_script.sh',
    params={'cpus': 8, 'mem': '32G', 'runtime': '4:00:00', 'partition': 'long'},
    dependencies=[3]
)

# Set additional SLURM parameters and modules for specific jobs
workflow_manager.set_slurm_params(job_id=1, params={'env_vars': {'MY_VAR': 'value'}})
workflow_manager.set_modules(job_id=1, modules=['fsl/6.0.4'])
workflow_manager.set_singularity_params(job_id=4, container='/path/to/container.sif', bind_paths=['/input:/output'])

# Generate SLURM batch files for the entire workflow
workflow_manager.create_workflow()