import yaml
import os
import subprocess
import requests
import sys


tag = '4.10.0'
sdk = {'4.10.0': 'https://mirror.openshift.com/pub/openshift-v4/x86_64/clients/operator-sdk/4.9.0/operator-sdk-v1.10.1-ocp-linux-x86_64.tar.gz'}
orig_bundle = 'quay.io/openshift-kni/cluster-group-upgrades-operator-bundle'
new_bundle = 'quay.io/vgrinber/cluster-group-upgrades-operator-bundle'

related_images = [
  f'quay.io/openshift-kni/cluster-group-upgrades-operator:{tag}',
  f'quay.io/openshift-kni/cluster-group-upgrades-operator-precache:{tag}',
  'gcr.io/kubebuilder/kube-rbac-proxy:v0.8.0'
]

csv_name = "cluster-group-upgrades-operator.clusterserviceversion.yaml"
cwd = os.getcwd()

def extract_bundle():
  output = subprocess.run([os.path.join(cwd, "talo.sh"), tag], cwd=cwd)
  print(output)


def get_sdk():
  # subprocess.run(["curl", "--output", "bin/sdk.tar.gz", sdk[tag]], cwd=cwd)
  # subprocess.run(["tar", "-xf", "bin/sdk.tar.gz", "-C", "bin"], cwd=cwd)
  # os.unlink("bin/sdk.tar.gz")
  pass
  

def get_digest_by_tag(img):
  split_img = img.split(':')
  cmp = split_img[0].split('/')
  url = f"https://{cmp[0]}/v2/{cmp[1]}/{cmp[2]}/manifests/{split_img[-1]}"
  headers = {'Accept': 'application/vnd.docker.distribution.manifest.v2+json'}
  r = requests.get(url, headers=headers)
  return f"{split_img[0]}@{r.headers.get('Docker-Content-Digest')}"

if __name__ == '__main__':
  
  extract_bundle()
  images = []
  for img in related_images:
    img_by_digest = get_digest_by_tag(img)
    images.append(img_by_digest)
  print(images)
  csv_path = os.path.join(os.getcwd(), 'artifacts', 'bundle', 'manifests', csv_name)
  with open(csv_path, 'r') as f:
    csv = yaml.safe_load(f)
  csv['spec']['relatedImages'] = []
  # Patch related images
  for img in images:
    image = {}
    image['name'] = ''
    image['image'] = img
    csv['spec']['relatedImages'].append(image)
  # Patch deployment
  for container in csv['spec']['install']['spec']['deployments'][0]['spec']['template']['spec']['containers']:
    image = container.get('image')
    index = related_images.index(image)
    image_with_digest = images[index]
    container['image'] = image_with_digest
    #patch images in environment variables
    if container.get('name') == 'manager':
      envs = container['env']
      for env in envs:
        val = env['value'].split(':')[0]
        print(val)
        patched_val = [i for i in images if val in i][0]
        print(patched_val)
        env['value'] = patched_val
  # write back
  with open(csv_path, 'w') as f:
    yaml.safe_dump(csv, f)

  # make bundle



