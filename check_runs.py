from mlflow.tracking import MlflowClient

client = MlflowClient('http://127.0.0.1:5000')

# List experiments
experiments = client.list_experiments()
print(f'Experiments: {len(experiments)}')
for e in experiments:
    print(f'  [{e.experiment_id}] {e.name}')
    print(f'    artifact_location: {e.artifact_location}')

# Search runs in experiment 1 (test-from-cli)
print('\nRuns in experiment 1:')
runs = client.search_runs(experiment_ids=['1'])
for r in runs:
    print(f"  {r.info.run_id}: {r.info.status}")
    print(f"    artifact_uri: {r.info.artifact_uri}")
    for k, v in r.data.metrics.items():
        print(f"    {k}: {v}")