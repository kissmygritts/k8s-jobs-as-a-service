# controller.py
from flask import Flask, request, jsonify
from kubernetes import client, config
import uuid
import os

app = Flask(__name__)

# Load K8s config (in-cluster or local)
try:
    config.load_incluster_config()  # When running in cluster
except:
    config.load_kube_config()  # When running locally

batch_v1 = client.BatchV1Api()

@app.route('/healthcheck', methods=['GET'])
def healthcheck():
    return jsonify({
        "status": "ok"
    })

@app.route('/submit-job', methods=['POST'])
def submit_job():
    job_id = str(uuid.uuid4())[:8]
    
    # Get parameters from request
    data = request.json
    message = data.get('message', 'Hello World')
    
    # Create Job manifest
    job_manifest = {
        "apiVersion": "batch/v1",
        "kind": "Job",
        "metadata": {
            "name": f"k8s-jaas-job-{job_id}",
            "namespace": "default"
        },
        "spec": {
            "template": {
                "spec": {
                    "containers": [{
                        "name": "k8s-jaas-worker",
                        "image": "localhost/k8s-jaas-worker:1.0",
                        "env": [
                            {"name": "MESSAGE", "value": message},
                            {"name": "JOB_ID", "value": job_id}
                        ]
                    }],
                    "restartPolicy": "Never"
                }
            }
        }
    }
    
    # Submit job to Kubernetes
    try:
        batch_v1.create_namespaced_job(
            namespace="default",
            body=job_manifest
        )
        return jsonify({
            "job_id": job_id,
            "status": "submitted",
            "message": f"Job {job_id} created successfully"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/job-status/<job_id>')
def job_status(job_id):
    try:
        job = batch_v1.read_namespaced_job(
            name=f"k8s-jaas-job-{job_id}",
            namespace="default"
        )
        
        conditions = job.status.conditions or []
        if any(c.type == "Complete" for c in conditions):
            status = "completed"
        elif any(c.type == "Failed" for c in conditions):
            status = "failed"
        else:
            status = "running"
            
        return jsonify({
            "job_id": job_id,
            "status": status,
            "active_pods": job.status.active or 0,
            "succeeded_pods": job.status.succeeded or 0,
            "failed_pods": job.status.failed or 0
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)