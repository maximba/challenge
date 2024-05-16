# Install LB
```
go install sigs.k8s.io/cloud-provider-kind@latest
```

# Setup DNS additional Zone
```
kubectl -n kube-system get configmap coredns -o jsonpath='{.data.Corefile}' > ./Corefile
Add file /etc/coredns/dominicus-zone.db dominicus.techandtapas {
      upstream
    }
   
kubectl -n kube-system create configmap coredns --from-file=Corefile --from-file=dominicus.techandtapas --save-config=true --dry-run -o yaml > coredns.yaml

kubectl -n kube-system apply -f ./coredns.yaml

kubectl -n kube-system edit deployment coredns

In the "volumes" section, add the following key/path pair:

volumes:
- configMap:
    defaultMode: 420
    items:
    - key: Corefile
      path: Corefile
    - key: dominicus-zone.db
      path: dominicus-zone.db
```
