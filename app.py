from flask import Flask, escape, request
from logging.config import dictConfig
from prometheus_flask_exporter import PrometheusMetrics, is_running_from_reloader, current_app, choose_encoder, Gauge, Histogram
from prometheus_client import Enum, Info, Summary

import requests
import json
import os

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': os.environ.get('LOG_LEVEL', 'INFO'),
        'handlers': ['wsgi']
    }
})

app = Flask(__name__)

class PrometheusMetricsWithExporter(PrometheusMetrics):

    def register_endpoint(self, path, app):
        """
        Register the metrics endpoint on the Flask application.

        :param path: the path of the endpoint
        :param app: the Flask application to register the endpoint on
            (by default it is the application registered with this class)
        """

        if is_running_from_reloader() and not os.environ.get('DEBUG_METRICS'):
            return

        if app is None:
            app = self.app or current_app

        @self.do_not_track()
        def prometheus_metrics():
            # import these here so they don't clash with our own multiprocess module
            from prometheus_client import multiprocess, CollectorRegistry

            if 'PROMETHEUS_MULTIPROC_DIR' in os.environ or 'prometheus_multiproc_dir' in os.environ:
                registry = CollectorRegistry()
            else:
                registry = self.registry

            if 'name[]' in request.args:
                registry = registry.restricted_registry(request.args.getlist('name[]'))

            if 'PROMETHEUS_MULTIPROC_DIR' in os.environ or 'prometheus_multiproc_dir' in os.environ:
                multiprocess.MultiProcessCollector(registry)

            generate_metrics()

            generate_latest, content_type = choose_encoder(request.headers.get("Accept"))
            headers = {'Content-Type': content_type}
            return generate_latest(registry), 200, headers

        # apply any user supplied decorators, like authentication
        if self._metrics_decorator:
            prometheus_metrics = self._metrics_decorator(prometheus_metrics)

        # apply the Flask route decorator on our metrics endpoint
        app.route(path)(prometheus_metrics)

metrics = PrometheusMetricsWithExporter(app, path='/metrics')
metrics.info('cloudflare_status_exporter', 'exports cloudflare status page for ingestion by prometheus', version='1.0.0')
by_path_counter = metrics.counter(
    'by_path_counter', 'Request count by request paths',
    labels={'path': lambda: request.path}
)
# status data endpoints
CLOUDFLARE_SUMMARY = os.environ.get('CLOUDFLARE_SUMMARY', 'https://yh6f0r4529hb.statuspage.io/api/v2/summary.json')
CLOUDFLARE_STATUS = os.environ.get('CLOUDFLARE_STATUS', 'https://yh6f0r4529hb.statuspage.io/api/v2/status.json')
CLOUDFLARE_COMPONENTS = os.environ.get('CLOUDFLARE_COMPONENTS', 'https://yh6f0r4529hb.statuspage.io/api/v2/components.json')
CLOUDFLARE_UNRESOLVED_INCIDENTS = os.environ.get('CLOUDFLARE_UNRESOLVED_INCIDENTS', 'https://yh6f0r4529hb.statuspage.io/api/v2/incidents/unresolved.json')
CLOUDFLARE_ALL_INCIDENTS = os.environ.get('CLOUDFLARE_ALL_INCIDENTS', 'https://yh6f0r4529hb.statuspage.io/api/v2/incidents.json')
CLOUDFLARE_SCHEDUALED_MAINTENANCES = os.environ.get('CLOUDFLARE_SCHEDUALED_MAINTENANCES', 'https://yh6f0r4529hb.statuspage.io/api/v2/scheduled-maintenances/upcoming.json')
CLOUDFLARE_ACTIVE_MAINTENANCES = os.environ.get('CLOUDFLARE_ACTIVE_MAINTENANCES', 'https://yh6f0r4529hb.statuspage.io/api/v2/scheduled-maintenances/active.json')
CLOUDFLARE_ALL_MAINTENANCES = os.environ.get('CLOUDFLARE_ALL_MAINTENANCES', 'https://yh6f0r4529hb.statuspage.io/api/v2/scheduled-maintenances.json')
# impact env variables
STATUS_IMPACT_NONE_GAUGE_VAULE = float(os.environ.get('STATUS_IMPACT_NONE_GAUGE_VAULE', 1.0))
STATUS_IMPACT_MINOR_GAUGE_VAULE = float(os.environ.get('STATUS_IMPACT_MINOR_GAUGE_VAULE', 0.66))
STATUS_IMPACT_MAJOR_GAUGE_VAULE = float(os.environ.get('STATUS_IMPACT_MAJOR_GAUGE_VAULE', 0.33))
STATUS_IMPACT_CRITICAL_GAUGE_VAULE = float(os.environ.get('STATUS_IMPACT_CRITICAL_GAUGE_VAULE', 0.0))
# components env variables
STATUS_COMPONENTS_OPERATIONAL_GAUGE_VAULE = float(os.environ.get('STATUS_COMPONENTS_OPERATIONAL_GAUGE_VAULE', 1.0))
STATUS_COMPONENTS_DEGRADED_PERFORMANCE_GAUGE_VAULE = float(os.environ.get('STATUS_COMPONENTS_DEGRADED_PERFORMANCE_GAUGE_VAULE', 0.66))
STATUS_COMPONENTS_PARTIAL_OUTAGE_GAUGE_VAULE = float(os.environ.get('STATUS_COMPONENTS_PARTIAL_OUTAGE_GAUGE_VAULE', 0.33))
STATUS_COMPONENTS_MAJOR_OUTAGE_GAUGE_VAULE = float(os.environ.get('STATUS_COMPONENTS_MAJOR_OUTAGE_GAUGE_VAULE', 0.0))
# incidents env variables
STATUS_INCIDENTS_INVESTIGATING_GAUGE_VAULE = float(os.environ.get('STATUS_INCIDENTS_INVESTIGATING_GAUGE_VAULE', 1.0))
STATUS_INCIDENTS_IDENTIFIED_GAUGE_VAULE = float(os.environ.get('STATUS_INCIDENTS_IDENTIFIED_GAUGE_VAULE', 1.0))
STATUS_INCIDENTS_MONITORING_GAUGE_VAULE = float(os.environ.get('STATUS_INCIDENTS_MONITORING_GAUGE_VAULE', 1.0))
STATUS_INCIDENTS_RESOLVED_GAUGE_VAULE = float(os.environ.get('STATUS_INCIDENTS_RESOLVED_GAUGE_VAULE', 0.0))
STATUS_INCIDENTS_POSTMORTEM_GAUGE_VAULE = float(os.environ.get('STATUS_INCIDENTS_POSTMORTEM_GAUGE_VAULE', 0.0))
# maintenance env variables
STATUS_MAINTENANCE_SCHEDULED_GAUGE_VAULE = float(os.environ.get('STATUS_MAINTENANCE_SCHEDULED_GAUGE_VAULE', 1.0))
STATUS_MAINTENANCE_IN_PROGRESS_GAUGE_VAULE = float(os.environ.get('STATUS_MAINTENANCE_IN_PROGRESS_GAUGE_VAULE', 1.0))
STATUS_MAINTENANCE_VERIFYING_GAUGE_VAULE = float(os.environ.get('STATUS_MAINTENANCE_VERIFYING_GAUGE_VAULE', 1.0))
STATUS_MAINTENANCE_COMPLETED_GAUGE_VAULE = float(os.environ.get('STATUS_MAINTENANCE_COMPLETED_GAUGE_VAULE', 0.0))

# Which status endpoints you would like to export to the metrics endpoint in a comma seperated list
# For example:
# CLOUDFLARE_STATUS_OUTPUT = 'status,unresolved_incidents'
# Available options: summary, status, components, unresolved_incidents, all_incidents, schedualed_maintenance, active_maintenance, all_maintenance
CLOUDFLARE_STATUS_OUTPUT = os.environ.get('CLOUDFLARE_STATUS_OUTPUT', 'status')

status_endpoints = []

page_status = Info('cloudflare_status_info','contains various information about the summary endpoint')
main_status = Enum('cloudflare_status_current','main status endpoint for at a glance uptime', states=['none', 'minor', 'major', 'critical'])
component_status = Gauge(u'cloudflare_status_component','status of indavidual components', ['name','status'])
incident_status = Gauge(u'cloudflare_status_incidents', 'status of incidents', ['name', 'impact', 'status'])
schedualed_maintenance = Gauge(u'cloudflare_schedualed_maintenance', 'list of maintenance events', ['name', 'impact', 'status'])

@app.before_first_request
def initiate_parser():
    '''
    ingests CLOUDFLARE_STATUS_OUTPUT and sets which endpoints should be hit
    '''

    app.logger.info('initiating parser')
    status_targets = set(CLOUDFLARE_STATUS_OUTPUT.split(','))
    app.logger.info(status_targets)

    if len(status_targets) == 0:
        return

    # if all data is needed or a combination of options that would need summary set main endpoint and exit
    if set(['summary']).issubset(status_targets) or \
        set(['status', 'components']).issubset(status_targets) and \
        (set(['unresolved_incidents']).issubset(status_targets) or set(['all_incidents']).issubset(status_targets) ) and \
        (set(['schedualed_maintenance', 'active_maintenance']).issubset(status_targets) or set(['all_maintenance']).issubset(status_targets) ):
        print('INFO: using summary endpoint')
        app.logger.info('added summary endpoint')
        status_endpoints.append(CLOUDFLARE_SUMMARY)
        return

    if set(['status']).issubset(status_targets) :
        app.logger.info('added status endpoint')
        status_endpoints.append(CLOUDFLARE_STATUS)

    if set(['components']).issubset(status_targets):
        app.logger.info('added components endpoint')
        status_endpoints.append(CLOUDFLARE_COMPONENTS)

    if set(['unresolved_incidents']).issubset(status_targets):
        app.logger.info('added unresolved_incidents endpoint')
        status_endpoints.append(CLOUDFLARE_UNRESOLVED_INCIDENTS)

    if set(['all_incidents']).issubset(status_targets):
        app.logger.info('added all_incidents endpoint')
        status_endpoints.append(CLOUDFLARE_ALL_INCIDENTS)

    if set(['schedualed_maintenance', 'active_maintenance']).issubset(status_targets) or set(['all_maintenance']).issubset(status_targets):
        app.logger.info('added all_maintenance endpoint')
        status_endpoints.append(CLOUDFLARE_ALL_MAINTENANCES)

    if set(['schedualed_maintenance']).issubset(status_targets) and not set(['active_maintenance']).issubset(status_targets) :
        app.logger.info('added schedualed_maintenance endpoint')
        status_endpoints.append(CLOUDFLARE_SCHEDUALED_MAINTENANCES)

    if set(['active_maintenance']).issubset(status_targets) and not set(['schedualed_maintenance']).issubset(status_targets):
        app.logger.info('added active_maintenance endpoint')
        status_endpoints.append(CLOUDFLARE_ALL_MAINTENANCES)

@app.route('/')
def homepage():
    return '<a href="/metrics">Metrics</a>'

def generate_metrics():
    status = {}
    for target in status_endpoints:
        status.update(requests.get(target).json())

    for key, value in status.items():
        print(key)
        if key == 'page':
            page_status.info({'id': value['id'], 'name': value['name'], 'url': value['url'],'time_zone': value['time_zone']})
        if key == 'status':
            main_status.state(str(value['indicator']))
        if key == 'components':
            for item in value:
                component_status.labels(item['name'], item['status']).set(get_status_value(item['status']))
        if key == 'incidents':
            for item in value:
                incident_status.labels(item['name'], item['impact'], item['status']).set(get_status_value(item['status']))
        if key == 'scheduled_maintenances':
            for item in value:
                schedualed_maintenance.labels(item['name'], item['impact'], item['status']).set(get_status_value(item['status']))

def get_status_value(status):
    return {
        #impact
        'none' : STATUS_IMPACT_NONE_GAUGE_VAULE,
        'minor' : STATUS_IMPACT_MINOR_GAUGE_VAULE,
        'major' : STATUS_IMPACT_MAJOR_GAUGE_VAULE,
        'critical' : STATUS_IMPACT_CRITICAL_GAUGE_VAULE,
        #components
        'operational': STATUS_COMPONENTS_OPERATIONAL_GAUGE_VAULE,
        'degraded_performance': STATUS_COMPONENTS_DEGRADED_PERFORMANCE_GAUGE_VAULE,
        'partial_outage': STATUS_COMPONENTS_PARTIAL_OUTAGE_GAUGE_VAULE,
        'major_outage': STATUS_COMPONENTS_MAJOR_OUTAGE_GAUGE_VAULE,
        #incidents
        'investigating' : STATUS_INCIDENTS_INVESTIGATING_GAUGE_VAULE,
        'identified' : STATUS_INCIDENTS_IDENTIFIED_GAUGE_VAULE,
        'monitoring' : STATUS_INCIDENTS_MONITORING_GAUGE_VAULE,
        'resolved' : STATUS_INCIDENTS_RESOLVED_GAUGE_VAULE,
        'postmortem' : STATUS_INCIDENTS_POSTMORTEM_GAUGE_VAULE,
        #maintenance
        'scheduled' : STATUS_MAINTENANCE_SCHEDULED_GAUGE_VAULE,
        'in_progress' : STATUS_MAINTENANCE_IN_PROGRESS_GAUGE_VAULE,
        'verifying' : STATUS_MAINTENANCE_VERIFYING_GAUGE_VAULE,
        'completed' : STATUS_MAINTENANCE_COMPLETED_GAUGE_VAULE,
    }.get(status)
