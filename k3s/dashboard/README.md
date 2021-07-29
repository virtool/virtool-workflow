# Deploy The Kubernetes Dashboard

## The Dashboard Service

```shell script
kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.2.0/aio/deploy/recommended.yaml

kubectl proxy
```

While `kubectl proxy` is running the dashboard can be viewed at http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/

## Admin user account

> `kubectl apply -f admin-user-role.yml`

This will create an account named admin-user and a token for this account.

### Get The Account Token

The token is stored in a kubernetes secret. You can find the name of the secret in the output of `kubectl -n kubernetes-dashboard get sa/admin-user -o yaml`.

Then get the token using:

> `kubectl -n kubernetes-dashboard get secrets {your secret}`

Copy the token and paste it into the web UI to log in.
