# Cloudflare-status-exporter

Exports cloudflare's status endpoint as a scrapable /metrics endpoint in the container. This will only grab the status endpoint by default. You can modify which endpoints you want to hit with the env var `CLOUDFLARE_STATUS_OUTPUT` below

## tl;dr
 
### Kubernetes
Assumes a prometheus operator
```
git clone https://github.com/lukaszzalewski/cloudflare-status-exporter.git
kubectl apply -f cloudflare-status-exporter/kube-deploy/*
kubectl port-forward -n monitoring cloudflare-status-exporter 8000:8000
```

### Docker
```
docker pull justonecommand/cloudflare-status-exporter:latest
docker run -p 8000:8000 justonecommand/cloudflare-status-exporter:latest
```

### Status export targets
Which status endpoints you would like to export to prometheus. The list is comma seperated with no spaces
For example:
CLOUDFLARE_STATUS_OUTPUT='status,components,unresolved_incidents'
Available options: summary, status, components, unresolved_incidents, all_incidents, schedualed_maintenance, active_maintenance, all_maintenance

| Env Var | Default |
|---| --- |
| CLOUDFLARE_STATUS_OUTPUT | status  

### Status endpoint targets
The urls of the varous json files that provide the current status of cloudflare

| Env Var | Default |
|---| --- |
| CLOUDFLARE_SUMMARY | https://yh6f0r4529hb.statuspage.io/api/v2/summary.json
| CLOUDFLARE_STATUS | https://yh6f0r4529hb.statuspage.io/api/v2/status.json
| CLOUDFLARE_COMPONENTS | https://yh6f0r4529hb.statuspage.io/api/v2/components.json
| CLOUDFLARE_UNRESOLVED_INCIDENTS | https://yh6f0r4529hb.statuspage.io/api/v2/incidents/unresolved.json
| CLOUDFLARE_ALL_INCIDENTS | https://yh6f0r4529hb.statuspage.io/api/v2/incidents.json
| CLOUDFLARE_SCHEDUALED_MAINTENANCES | https://yh6f0r4529hb.statuspage.io/api/v2/scheduled-maintenances/upcoming.json
| CLOUDFLARE_ACTIVE_MAINTENANCES | https://yh6f0r4529hb.statuspage.io/api/v2/scheduled-maintenances/active.json
| CLOUDFLARE_ALL_MAINTENANCES | https://yh6f0r4529hb.statuspage.io/api/v2/scheduled-maintenances.json

## Gauge translation values
All the values that the status endpoints get translated into Gauges. Impact and components will show between 1.0(up) and 0.0(down) depending on the severity of the issues. Incidents and Maintenance will show a 1.0 if the event in question is not resolved. It will show 0.0 is it is resolved. All of these are changeable.
### impact env variables
| Env Var | Default |
|---| --- |
| STATUS_IMPACT_NONE_GAUGE_VAULE | 1.0
| STATUS_IMPACT_MINOR_GAUGE_VAULE | 0.66
| STATUS_IMPACT_MAJOR_GAUGE_VAULE | 0.33
| STATUS_IMPACT_CRITICAL_GAUGE_VAULE | 0.0
### components env variables
| Env Var | Default |
|---| --- |
| STATUS_COMPONENTS_OPERATIONAL_GAUGE_VAULE | 1.0
| STATUS_COMPONENTS_DEGRADED_PERFORMANCE_GAUGE_VAULE | 1.0
| STATUS_COMPONENTS_PARTIAL_OUTAGE_GAUGE_VAULE | 1.0

| STATUS_COMPONENTS_MAJOR_OUTAGE_GAUGE_VAULE | 1.0
### incidents env variables
| Env Var | Default |
|---| --- |
| STATUS_INCIDENTS_INVESTIGATING_GAUGE_VAULE | 1.0
| STATUS_INCIDENTS_IDENTIFIED_GAUGE_VAULE | 1.0
| STATUS_INCIDENTS_MONITORING_GAUGE_VAULE | 1.0
| STATUS_INCIDENTS_RESOLVED_GAUGE_VAULE | 1.0
| STATUS_INCIDENTS_POSTMORTEM_GAUGE_VAULE | 1.0
### maintenance env variables
| Env Var | Default |
|---| --- |
| STATUS_MAINTENANCE_SCHEDULED_GAUGE_VAULE | 1.0
| STATUS_MAINTENANCE_IN_PROGRESS_GAUGE_VAULE | 1.0
| STATUS_MAINTENANCE_VERIFYING_GAUGE_VAULE | 1.0
| STATUS_MAINTENANCE_COMPLETED_GAUGE_VAULE | 0.0

