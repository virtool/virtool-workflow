# Deploying Virtool Workflows Using k3s

## Install k3s

### Master Node / Control Pane

> `curl -sfL https://get.k3s.io | sh -`

### Agent/Worker Nodes

The `K3S_TOKEN` is found on the master node under `/var/lib/rancher/k3s/server/node-token`.

> `curl -sfL https://get.k3s.io | K3S_URL=https://${host}:6443 K3S_TOKEN=${token} sh -`

After installing, the new node should show up when running `kubectl get nodes` on the master.

## Apply Dev Deployment

:warning: Make sure to run these commands on the k3s master node.

> `sudo kubectl apply -f dev-deployment.yml`

You should now see a running pod.

> `sudo kubectl get pods`

```text
NAME                               READY   STATUS    RESTARTS   AGE
workflow-k3s-dev-c58b6d5bf-mtv2n   1/1     Running   0          6m
```

## Redis

> `sudo kubectl apply -f redis/deployment.yml`

> `sudo kubectl apply -f redis/redis-service.yml`

You should now see `redis-service` in the running services list.

> `sudo kubectl get services`

```text
NAME            TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)          AGE
kubernetes      ClusterIP   10.43.0.1      <none>        443/TCP          106m
redis-service   NodePort    10.43.71.176   <none>        6379:31132/TCP   19s
```

### Verify Connection

You can use NetCat to verify that the redis service is running.

> `nc -v ${HOST_NODE} ${NODE_PORT}`

The `NODE_PORT` is shown in the `kubectl get services`. The `HOST_NODE` is the
host name of the node which is running the redis service.

You can figure out which node the service is running on using `kubectl get pods -o wide`.

## Postgres

Apply the config map storing the required environment variables.

> `kubectl apply -f postgres/config.yml`

Create a volume so that data can be persisted.

> `kubectl apply -f postgres/volume.yml`

Create a deployment running postgres.

> `kubectl apply -f postgres/deployment.yml`

Create a service so that the database can be accessed.

> `kubectl apply -f postgres/service.yml`

## Mongo

Create a volume so that data can be persisted.

> `kubectl apply -f mongo/volume.yml`

Create a deployment running mongo.

> `kubectl apply -f mongo/deployment.yml`

Create a service so that the database can be accessed.

> `kubectl apply -f mongo/service.yml`

## Jobs API

Create a deployment running the jobs API.

> `kubectl apply -f jobsAPI/deployment.yml`

Create a service exposing the jobs API.

> `kubectl apply -f jobsAPI/service.yml`

### Test Connection

#### NodePort

The jobs API should be exposed via a NodePort.

Find the port number in the output of

> `kubectl get service jobs-api`

Then try to make a request to the jobs API.

> `curl http://{NODE_IP}:{NODE_PORT}`/api

```text
{
    "id": "unauthorized",
    "message": "No authorization header."
}
```

#### In Cluster Using Curl

Start a container with `curl` and `nslookup` available.

> `kubectl run curl --image=radial/busyboxplus:curl`

You can use `nslookup` to find the cluster URLs for services

> `kubectl exec curl nslookup jobs-api`

```text
Server:    10.43.0.10
Address 1: 10.43.0.10 kube-dns.kube-system.svc.cluster.local

Name:      jobs-api
Address 1: 10.43.27.20 jobs-api.default.svc.cluster.local
```

Now we can make a request to the jobs API.

> `kubectl exec curl curl http://jobs-api.default.svc.cluster.local/api`

```text
{
    "id": "unauthorized",
    "message": "No authorization header."
}
```

