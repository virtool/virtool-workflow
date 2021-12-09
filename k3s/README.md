# Deploying Virtool Workflows Using k3s

## Install k3s

### Master Node / Control Pane

> `curl -sfL https://get.k3s.io | sh -`

### Agent/Worker Nodes

The `K3S_TOKEN` is found on the master node under `/var/lib/rancher/k3s/server/node-token`.

> `curl -sfL https://get.k3s.io | K3S_URL=https://${host}:6443 K3S_TOKEN=${token} sh -`

After installing, the new node should show up when running `kubectl get nodes` on the master.

### [Optional] Use Local Docker Images

> `sudo systemctl stop k3s`

> `k3s server --docker`

## Deploy Services

:warning: This must be run on the master node / control-pane

> `sudo ./deploy.sh`

```text
deployment.apps/redis created
service/redis created
deployment.apps/redisinsight created
service/redisinsight created
persistentvolumeclaim/mongodb-pv-claim created
deployment.apps/mongodb created
service/mongo created
persistentvolumeclaim/postgres-pvc created
configmap/postgres-config unchanged
deployment.apps/postgres created
service/postgres created
persistentvolumeclaim/data-path-pvc created
deployment.apps/virtool-server created
service/virtool-server created
deployment.apps/jobs-api created
service/jobs-api created
deployment.apps/create-sample-runner created

Services:

Virtool Server: http://localhost:30908
Jobs API: http://localhost:32579
Redis Insight: http://localhost:31808
Redis Info: redis ClusterIP 10.43.67.186 <none> 6379/TCP 6s
```

After a few moments the output of `sudo kubectl get pods` look like:

```text
NAME                                    READY   STATUS    RESTARTS   AGE
redisinsight-77d974d87f-xbxbn           1/1     Running   0          100s
redis-c58b6d5bf-8njtl                   1/1     Running   0          101s
mongodb-5cc5c97db-dgdbw                 1/1     Running   0          99s
create-sample-runner-67d875694d-79zz2   1/1     Running   0          96s
postgres-769487cdf4-rbqvx               1/1     Running   0          98s
jobs-api-6f4b445b86-8hssz               1/1     Running   0          97s
virtool-server-88496fd96-5f4t7          1/1     Running   0          97s
```

Use the URLs printed by the `./deploy.sh` script to access the services.

## Tearing Down The Deployment

> `sudo ./teardown.sh`

After running `sudo kubectl get pods` should give:

```text
No resources found in default namespace.
```

## Manually Restart a Deployment

The `refresh.sh` script can be used to manually restart a deployment by name.

For example, I can restart the virtool server container using:

> `sudo ./refresh virtool-server`

This is useful when the docker image has been updated.

## Troubleshooting Connectivity Issues

Start a container with `curl` and `nslookup` available & enter a shell.

> `kubectl run curl --image=radial/busyboxplus:curl -i --tty`

From here you can use `curl`, `nslookup`, and other utilities to diagnose connectivity issues.

For example we can lookup the URL for a service by name using `nslookup`.

> [ root@curl:/ ]$ `nslookup jobs-api`


```text
Server:    10.43.0.10
Address 1: 10.43.0.10 kube-dns.kube-system.svc.cluster.local

Name:      jobs-api
Address 1: 10.43.27.20 jobs-api.default.svc.cluster.local
```

Now we can make a request to the jobs API.

> `kubectl exec curl curl http://jobs-api.default.svc.cluster.local`

```text
{
    "id": "unauthorized",
    "message": "No authorization header."
}
```