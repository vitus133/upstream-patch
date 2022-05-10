# How to patch the bundle and build the index #

#### Note: this only builds 4.10.0 TALO latest version as it is today. No parameterization, no other operators

Clone this repo and change to the cloned directory.
Search and replace \"\<your quay namespace\>\" text everywhere by your real quay namespace

Create your python environment:
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```
Patch the upstream bundle and push it to another location:
```bash
python rebundle.py
podman build -f artifacts/bundle.Dockerfile -t quay.io/<your quay namespace>/cluster-group-upgrades-operator-bundle:4.10.0 artifacts/
podman push quay.io/<your quay namespace>/cluster-group-upgrades-operator-bundle:4.10.0
```
Build and push the index:
```bash
podman build . --tag quay.io/<your quay namespace>/ran-operator-index:4.10.0 -f Containerfile.index
podman push quay.io/<your quay namespace>/ran-operator-index:4.10.0
```


## How to mirror to a disconnected registry ##

```bash
index_img=quay.io/<your quay namespace>/ran-operator-index:4.10.0
disconnected_reg=registry.hv6.telco5gran.eng.rdu2.redhat.com:8443
oc adm catalog mirror $index_img $disconnected_reg --manifests-only=true --icsp-scope registry --to-manifests=my_manifests --index-filter-by-os=linux/amd64
oc image mirror -f my_manifests/mapping.txt --keep-manifest-list
```

## How to configure your cluster to use mirrored images ##

```bash
oc patch OperatorHub cluster --type json -p '[{"op": "add", "path": "/spec/disableAllDefaultSources", "value": true}]'
oc apply -f my_manifests/imageContentSourcePolicy.yaml
oc apply -f my_manifests/catalogSource.yaml
```

The above assumes the registry is already properly configured in the cluster with pull secret and CA trust. If not, follow these:

https://docs.openshift.com/container-platform/4.10/openshift_images/image-configuration.html#images-configuration-cas_image-configuration

https://docs.openshift.com/container-platform/4.10/openshift_images/managing_images/using-image-pull-secrets.html#images-update-global-pull-secret_using-image-pull-secrets
