
#!/usr/bin/env python3
"""
HX Infrastructure - Dashboard Generator
Phase 3.4 - Production Operations Automation

Generates operational dashboards from monitoring data
"""

import json
import os
import sys
import argparse
import datetime
from pathlib import Path
from typing import Dict, List, Any
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DashboardGenerator:
    def __init__(self, data_dir: str = "/var/log/hx-infrastructure", 
                 output_dir: str = "/var/www/html"):
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def load_latest_data(self, pattern: str) -> Dict[str, Any]:
        """Load the latest data file matching the pattern"""
        try:
            files = list(self.data_dir.glob(pattern))
            if not files:
                logger.warning(f"No files found matching pattern: {pattern}")
                return {}
            
            latest_file = max(files, key=os.path.getctime)
            with open(latest_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading data from {pattern}: {e}")
            return {}
    
    def load_multiple_data(self, pattern: str, limit: int = 24) -> List[Dict[str, Any]]:
        """Load multiple data files for trend analysis"""
        try:
            files = list(self.data_dir.glob(pattern))
            files.sort(key=os.path.getctime, reverse=True)
            
            data = []
            for file in files[:limit]:
                try:
                    with open(file, 'r') as f:
                        data.append(json.load(f))
                except Exception as e:
                    logger.warning(f"Error loading {file}: {e}")
                    continue
            
            return data
        except Exception as e:
            logger.error(f"Error loading multiple data from {pattern}: {e}")
            return []
    
    def generate_system_health_dashboard(self) -> Dict[str, Any]:
        """Generate system health dashboard data"""
        logger.info("Generating system health dashboard")
        
        # Load latest health data
        health_data = self.load_latest_data("health-*.json")
        
        # Load historical data for trends
        historical_health = self.load_multiple_data("health-*.json", 24)
        
        dashboard = {
            "title": "HX Infrastructure - System Health Dashboard",
            "generated_at": datetime.datetime.now().isoformat(),
            "current_status": health_data,
            "trends": {
                "cpu_usage": [h.get("cpu_usage", 0) for h in historical_health],
                "memory_usage": [h.get("memory_usage", 0) for h in historical_health],
                "disk_usage": [h.get("disk_usage", 0) for h in historical_health],
                "timestamps": [h.get("timestamp", "") for h in historical_health]
            },
            "alerts": self._generate_health_alerts(health_data),
            "summary": self._generate_health_summary(health_data, historical_health)
        }
        
        return dashboard
    
    def generate_incident_dashboard(self) -> Dict[str, Any]:
        """Generate incident response dashboard data"""
        logger.info("Generating incident dashboard")
        
        # Load incident database
        incident_db_file = self.data_dir / "incident_database.json"
        incident_db = {}
        if incident_db_file.exists():
            with open(incident_db_file, 'r') as f:
                incident_db = json.load(f)
        
        # Load recent incidents
        recent_incidents = self.load_multiple_data("incidents/detected-*.json", 10)
        
        # Load active incidents from dashboard
        active_incidents_file = self.output_dir / "incident_dashboard.json"
        active_incidents = {}
        if active_incidents_file.exists():
            with open(active_incidents_file, 'r') as f:
                active_incidents = json.load(f)
        
        dashboard = {
            "title": "HX Infrastructure - Incident Response Dashboard",
            "generated_at": datetime.datetime.now().isoformat(),
            "statistics": incident_db.get("statistics", {}),
            "active_incidents": active_incidents.get("active_incidents", []),
            "recent_incidents": recent_incidents,
            "incident_trends": self._generate_incident_trends(incident_db),
            "response_metrics": self._generate_response_metrics(incident_db)
        }
        
        return dashboard
    
    def generate_maintenance_dashboard(self) -> Dict[str, Any]:
        """Generate maintenance dashboard data"""
        logger.info("Generating maintenance dashboard")
        
        # Load maintenance reports
        maintenance_reports = self.load_multiple_data("maintenance-report-*.json", 10)
        
        # Load maintenance summary CSV data
        maintenance_summary = self._load_maintenance_summary()
        
        dashboard = {
            "title": "HX Infrastructure - Maintenance Dashboard",
            "generated_at": datetime.datetime.now().isoformat(),
            "recent_maintenance": maintenance_reports,
            "maintenance_summary": maintenance_summary,
            "upcoming_maintenance": self._generate_upcoming_maintenance(),
            "maintenance_metrics": self._generate_maintenance_metrics(maintenance_reports)
        }
        
        return dashboard
    
    def generate_sla_dashboard(self) -> Dict[str, Any]:
        """Generate SLA monitoring dashboard data"""
        logger.info("Generating SLA dashboard")
        
        # Load SLA metrics
        sla_metrics = self.load_multiple_data("sla-metrics-*.json", 24)
        
        dashboard = {
            "title": "HX Infrastructure - SLA Dashboard",
            "generated_at": datetime.datetime.now().isoformat(),
            "current_sla": sla_metrics[0] if sla_metrics else {},
            "sla_trends": self._generate_sla_trends(sla_metrics),
            "sla_violations": self._identify_sla_violations(sla_metrics),
            "sla_summary": self._generate_sla_summary(sla_metrics)
        }
        
        return dashboard
    
    def generate_operational_overview(self) -> Dict[str, Any]:
        """Generate comprehensive operational overview dashboard"""
        logger.info("Generating operational overview dashboard")
        
        # Collect data from all sources
        health_data = self.load_latest_data("health-*.json")
        apm_data = self.load_latest_data("apm-metrics-*.json")
        infrastructure_data = self.load_latest_data("infrastructure-metrics-*.json")
        
        # Load incident statistics
        incident_db_file = self.data_dir / "incident_database.json"
        incident_stats = {}
        if incident_db_file.exists():
            with open(incident_db_file, 'r') as f:
                incident_stats = json.load(f).get("statistics", {})
        
        dashboard = {
            "title": "HX Infrastructure - Operational Overview",
            "generated_at": datetime.datetime.now().isoformat(),
            "system_health": {
                "overall_status": self._determine_overall_status(health_data),
                "cpu_usage": health_data.get("cpu_usage", 0),
                "memory_usage": health_data.get("memory_usage", 0),
                "disk_usage": health_data.get("disk_usage", 0)
            },
            "application_performance": {
                "response_time": apm_data.get("response_time", {}).get("average", 0),
                "error_rate": apm_data.get("error_rate", {}).get("current", 0),
                "throughput": apm_data.get("throughput", 0)
            },
            "infrastructure": {
                "network_status": infrastructure_data.get("network", {}).get("connectivity_status", "unknown"),
                "storage_status": infrastructure_data.get("storage", {}).get("io_status", "unknown")
            },
            "incidents": {
                "total": incident_stats.get("total", 0),
                "resolved": incident_stats.get("resolved", 0),
                "escalated": incident_stats.get("escalated", 0)
            },
            "alerts": self._generate_operational_alerts(health_data, apm_data, infrastructure_data)
        }
        
        return dashboard
    
    def _generate_health_alerts(self, health_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate health-based alerts"""
        alerts = []
        
        if health_data.get("cpu_usage", 0) > 80:
            alerts.append({
                "type": "warning",
                "message": f"High CPU usage: {health_data.get('cpu_usage', 0)}%",
                "severity": "high" if health_data.get("cpu_usage", 0) > 90 else "medium"
            })
        
        if health_data.get("memory_usage", 0) > 85:
            alerts.append({
                "type": "warning",
                "message": f"High memory usage: {health_data.get('memory_usage', 0)}%",
                "severity": "high" if health_data.get("memory_usage", 0) > 95 else "medium"
            })
        
        if health_data.get("disk_usage", 0) > 90:
            alerts.append({
                "type": "critical",
                "message": f"Critical disk usage: {health_data.get('disk_usage', 0)}%",
                "severity": "critical"
            })
        
        return alerts
    
    def _generate_health_summary(self, current: Dict[str, Any], historical: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate health summary statistics"""
        if not historical:
            return {"status": "no_data"}
        
        cpu_values = [h.get("cpu_usage", 0) for h in historical if h.get("cpu_usage")]
        memory_values = [h.get("memory_usage", 0) for h in historical if h.get("memory_usage")]
        
        return {
            "avg_cpu_24h": sum(cpu_values) / len(cpu_values) if cpu_values else 0,
            "avg_memory_24h": sum(memory_values) / len(memory_values) if memory_values else 0,
            "peak_cpu_24h": max(cpu_values) if cpu_values else 0,
            "peak_memory_24h": max(memory_values) if memory_values else 0,
            "data_points": len(historical)
        }
    
    def _generate_incident_trends(self, incident_db: Dict[str, Any]) -> Dict[str, Any]:
        """Generate incident trend analysis"""
        incidents = incident_db.get("incidents", [])
        
        # Group incidents by date
        daily_counts = {}
        for incident in incidents:
            date = incident.get("incident_metadata", {}).get("created_at", "")[:10]
            daily_counts[date] = daily_counts.get(date, 0) + 1
        
        return {
            "daily_incidents": daily_counts,
            "total_incidents": len(incidents),
            "avg_daily": sum(daily_counts.values()) / len(daily_counts) if daily_counts else 0
        }
    
    def _generate_response_metrics(self, incident_db: Dict[str, Any]) -> Dict[str, Any]:
        """Generate incident response metrics"""
        incidents = incident_db.get("incidents", [])
        
        resolved_incidents = [i for i in incidents if i.get("remediation", {}).get("successful")]
        escalated_incidents = [i for i in incidents if i.get("escalation", {}).get("escalated")]
        
        return {
            "resolution_rate": len(resolved_incidents) / len(incidents) * 100 if incidents else 0,
            "escalation_rate": len(escalated_incidents) / len(incidents) * 100 if incidents else 0,
            "auto_resolution_rate": len([i for i in resolved_incidents if i.get("remediation", {}).get("attempted")]) / len(incidents) * 100 if incidents else 0
        }
    
    def _load_maintenance_summary(self) -> List[Dict[str, Any]]:
        """Load maintenance summary from CSV"""
        csv_file = self.data_dir / "maintenance-summary.csv"
        if not csv_file.exists():
            return []
        
        try:
            import csv
            with open(csv_file, 'r') as f:
                reader = csv.DictReader(f)
                return list(reader)
        except Exception as e:
            logger.error(f"Error loading maintenance summary: {e}")
            return []
    
    def _generate_upcoming_maintenance(self) -> List[Dict[str, Any]]:
        """Generate upcoming maintenance schedule"""
        # This would typically integrate with a maintenance scheduling system
        # For now, return a placeholder
        return [
            {
                "date": (datetime.datetime.now() + datetime.timedelta(days=7)).isoformat()[:10],
                "type": "scheduled",
                "description": "Weekly maintenance window"
            }
        ]
    
    def _generate_maintenance_metrics(self, reports: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate maintenance metrics"""
        if not reports:
            return {}
        
        successful_maintenance = len([r for r in reports if r.get("execution_summary", {}).get("post_verification", {}).get("verified")])
        
        return {
            "total_maintenance": len(reports),
            "success_rate": successful_maintenance / len(reports) * 100,
            "avg_duration": sum([r.get("maintenance_window", {}).get("actual_duration", 0) for r in reports]) / len(reports)
        }
    
    def _generate_sla_trends(self, sla_metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate SLA trend analysis"""
        if not sla_metrics:
            return {}
        
        availability_values = [s.get("availability", {}).get("current", 0) for s in sla_metrics]
        response_time_values = [s.get("response_time", {}).get("current", 0) for s in sla_metrics]
        
        return {
            "availability_trend": availability_values,
            "response_time_trend": response_time_values,
            "timestamps": [s.get("timestamp", "") for s in sla_metrics]
        }
    
    def _identify_sla_violations(self, sla_metrics: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify SLA violations"""
        violations = []
        
        for metric in sla_metrics:
            if metric.get("overall_status") == "violated":
                violations.append({
                    "timestamp": metric.get("timestamp"),
                    "violated_slas": [
                        sla for sla in ["availability", "response_time", "error_rate"]
                        if metric.get(sla, {}).get("status") == "violated"
                    ]
                })
        
        return violations
    
    def _generate_sla_summary(self, sla_metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate SLA summary statistics"""
        if not sla_metrics:
            return {}
        
        violations = len([s for s in sla_metrics if s.get("overall_status") == "violated"])
        
        return {
            "sla_compliance_rate": (len(sla_metrics) - violations) / len(sla_metrics) * 100,
            "total_violations": violations,
            "data_points": len(sla_metrics)
        }
    
    def _determine_overall_status(self, health_data: Dict[str, Any]) -> str:
        """Determine overall system status"""
        if not health_data:
            return "unknown"
        
        cpu = health_data.get("cpu_usage", 0)
        memory = health_data.get("memory_usage", 0)
        disk = health_data.get("disk_usage", 0)
        
        if cpu > 90 or memory > 95 or disk > 95:
            return "critical"
        elif cpu > 80 or memory > 85 or disk > 90:
            return "warning"
        else:
            return "healthy"
    
    def _generate_operational_alerts(self, health_data: Dict[str, Any], 
                                   apm_data: Dict[str, Any], 
                                   infrastructure_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate operational alerts from all data sources"""
        alerts = []
        
        # Health alerts
        alerts.extend(self._generate_health_alerts(health_data))
        
        # APM alerts
        if apm_data.get("response_time", {}).get("status") == "critical":
            alerts.append({
                "type": "warning",
                "message": f"High response time: {apm_data.get('response_time', {}).get('average', 0)}ms",
                "severity": "high"
            })
        
        if apm_data.get("error_rate", {}).get("status") == "critical":
            alerts.append({
                "type": "critical",
                "message": f"High error rate: {apm_data.get('error_rate', {}).get('current', 0)}%",
                "severity": "critical"
            })
        
        # Infrastructure alerts
        if infrastructure_data.get("network", {}).get("connectivity_status") == "critical":
            alerts.append({
                "type": "critical",
                "message": "Network connectivity issues detected",
                "severity": "critical"
            })
        
        return alerts
    
    def generate_html_dashboard(self, dashboard_data: Dict[str, Any], template_name: str) -> str:
        """Generate HTML dashboard from data"""
        html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{dashboard_data.get('title', 'HX Infrastructure Dashboard')}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .dashboard {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
        .card {{ background: white; padding: 20px; margin: 10px 0; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .status-healthy {{ color: #27ae60; }}
        .status-warning {{ color: #f39c12; }}
        .status-critical {{ color: #e74c3c; }}
        .metric {{ display: inline-block; margin: 10px 20px 10px 0; }}
        .metric-value {{ font-size: 2em; font-weight: bold; }}
        .metric-label {{ font-size: 0.9em; color: #666; }}
        .alert {{ padding: 10px; margin: 5px 0; border-radius: 3px; }}
        .alert-warning {{ background: #fff3cd; border-left: 4px solid #ffc107; }}
        .alert-critical {{ background: #f8d7da; border-left: 4px solid #dc3545; }}
        .timestamp {{ font-size: 0.8em; color: #666; }}
    </style>
</head>
<body>
    <div class="dashboard">
        <div class="header">
            <h1>{dashboard_data.get('title', 'HX Infrastructure Dashboard')}</h1>
            <p class="timestamp">Generated: {dashboard_data.get('generated_at', '')}</p>
        </div>
        
        <div class="content">
            {self._generate_dashboard_content(dashboard_data, template_name)}
        </div>
    </div>
    
    <script>
        // Auto-refresh every 5 minutes
        setTimeout(function(){{ location.reload(); }}, 300000);
    </script>
</body>
</html>
        """
        
        return html_template
    
    def _generate_dashboard_content(self, data: Dict[str, Any], template_name: str) -> str:
        """Generate dashboard-specific content"""
        if template_name == "system_health":
            return self._generate_health_content(data)
        elif template_name == "incident":
            return self._generate_incident_content(data)
        elif template_name == "maintenance":
            return self._generate_maintenance_content(data)
        elif template_name == "sla":
            return self._generate_sla_content(data)
        elif template_name == "operational":
            return self._generate_operational_content(data)
        else:
            return "<div class='card'><h2>Dashboard content not available</h2></div>"
    
    def _generate_health_content(self, data: Dict[str, Any]) -> str:
        """Generate system health dashboard content"""
        current = data.get("current_status", {})
        alerts = data.get("alerts", [])
        
        content = f"""
        <div class="card">
            <h2>Current System Status</h2>
            <div class="metric">
                <div class="metric-value status-{'critical' if current.get('cpu_usage', 0) > 90 else 'warning' if current.get('cpu_usage', 0) > 80 else 'healthy'}">{current.get('cpu_usage', 0):.1f}%</div>
                <div class="metric-label">CPU Usage</div>
            </div>
            <div class="metric">
                <div class="metric-value status-{'critical' if current.get('memory_usage', 0) > 95 else 'warning' if current.get('memory_usage', 0) > 85 else 'healthy'}">{current.get('memory_usage', 0):.1f}%</div>
                <div class="metric-label">Memory Usage</div>
            </div>
            <div class="metric">
                <div class="metric-value status-{'critical' if current.get('disk_usage', 0) > 95 else 'warning' if current.get('disk_usage', 0) > 90 else 'healthy'}">{current.get('disk_usage', 0)}%</div>
                <div class="metric-label">Disk Usage</div>
            </div>
        </div>
        """
        
        if alerts:
            content += "<div class='card'><h2>Active Alerts</h2>"
            for alert in alerts:
                content += f"<div class='alert alert-{alert.get('type', 'warning')}'>{alert.get('message', '')}</div>"
            content += "</div>"
        
        return content
    
    def _generate_incident_content(self, data: Dict[str, Any]) -> str:
        """Generate incident dashboard content"""
        stats = data.get("statistics", {})
        active = data.get("active_incidents", [])
        
        content = f"""
        <div class="card">
            <h2>Incident Statistics</h2>
            <div class="metric">
                <div class="metric-value">{stats.get('total', 0)}</div>
                <div class="metric-label">Total Incidents</div>
            </div>
            <div class="metric">
                <div class="metric-value status-healthy">{stats.get('resolved', 0)}</div>
                <div class="metric-label">Resolved</div>
            </div>
            <div class="metric">
                <div class="metric-value status-warning">{stats.get('escalated', 0)}</div>
                <div class="metric-label">Escalated</div>
            </div>
        </div>
        """
        
        if active:
            content += "<div class='card'><h2>Active Incidents</h2>"
            for incident in active:
                content += f"""
                <div class="alert alert-{incident.get('severity', 'warning')}">
                    <strong>{incident.get('incident_id', 'Unknown')}</strong> - {incident.get('status', 'Unknown')}
                    <br><small>{incident.get('timestamp', '')}</small>
                </div>
                """
            content += "</div>"
        
        return content
    
    def _generate_maintenance_content(self, data: Dict[str, Any]) -> str:
        """Generate maintenance dashboard content"""
        recent = data.get("recent_maintenance", [])
        metrics = data.get("maintenance_metrics", {})
        
        content = f"""
        <div class="card">
            <h2>Maintenance Metrics</h2>
            <div class="metric">
                <div class="metric-value">{metrics.get('total_maintenance', 0)}</div>
                <div class="metric-label">Total Maintenance</div>
            </div>
            <div class="metric">
                <div class="metric-value status-healthy">{metrics.get('success_rate', 0):.1f}%</div>
                <div class="metric-label">Success Rate</div>
            </div>
        </div>
        """
        
        if recent:
            content += "<div class='card'><h2>Recent Maintenance</h2>"
            for maintenance in recent[:5]:
                status = maintenance.get("execution_summary", {}).get("post_verification", {}).get("verified", False)
                content += f"""
                <div class="alert alert-{'warning' if not status else 'info'}">
                    <strong>{maintenance.get('report_metadata', {}).get('maintenance_type', 'Unknown')}</strong> - 
                    {'Success' if status else 'Failed'}
                    <br><small>{maintenance.get('report_metadata', {}).get('generated_at', '')}</small>
                </div>
                """
            content += "</div>"
        
        return content
    
    def _generate_sla_content(self, data: Dict[str, Any]) -> str:
        """Generate SLA dashboard content"""
        current = data.get("current_sla", {})
        summary = data.get("sla_summary", {})
        
        content = f"""
        <div class="card">
            <h2>Current SLA Status</h2>
            <div class="metric">
                <div class="metric-value status-{'critical' if current.get('availability', {}).get('status') == 'violated' else 'healthy'}">{current.get('availability', {}).get('current', 0):.2f}%</div>
                <div class="metric-label">Availability</div>
            </div>
            <div class="metric">
                <div class="metric-value status-{'critical' if current.get('response_time', {}).get('status') == 'violated' else 'healthy'}">{current.get('response_time', {}).get('current', 0):.0f}ms</div>
                <div class="metric-label">Response Time</div>
            </div>
            <div class="metric">
                <div class="metric-value status-{'critical' if current.get('error_rate', {}).get('status') == 'violated' else 'healthy'}">{current.get('error_rate', {}).get('current', 0):.2f}%</div>
                <div class="metric-label">Error Rate</div>
            </div>
        </div>
        
        <div class="card">
            <h2>SLA Compliance</h2>
            <div class="metric">
                <div class="metric-value status-healthy">{summary.get('sla_compliance_rate', 0):.1f}%</div>
                <div class="metric-label">Compliance Rate</div>
            </div>
            <div class="metric">
                <div class="metric-value status-warning">{summary.get('total_violations', 0)}</div>
                <div class="metric-label">Total Violations</div>
            </div>
        </div>
        """
        
        return content
    
    def _generate_operational_content(self, data: Dict[str, Any]) -> str:
        """Generate operational overview content"""
        system = data.get("system_health", {})
        app = data.get("application_performance", {})
        incidents = data.get("incidents", {})
        alerts = data.get("alerts", [])
        
        content = f"""
        <div class="card">
            <h2>System Overview</h2>
            <div class="metric">
                <div class="metric-value status-{system.get('overall_status', 'unknown')}">{system.get('overall_status', 'Unknown').title()}</div>
                <div class="metric-label">Overall Status</div>
            </div>
            <div class="metric">
                <div class="metric-value">{system.get('cpu_usage', 0):.1f}%</div>
                <div class="metric-label">CPU</div>
            </div>
            <div class="metric">
                <div class="metric-value">{system.get('memory_usage', 0):.1f}%</div>
                <div class="metric-label">Memory</div>
            </div>
            <div class="metric">
                <div class="metric-value">{system.get('disk_usage', 0)}%</div>
                <div class="metric-label">Disk</div>
            </div>
        </div>
        
        <div class="card">
            <h2>Application Performance</h2>
            <div class="metric">
                <div class="metric-value">{app.get('response_time', 0):.0f}ms</div>
                <div class="metric-label">Response Time</div>
            </div>
            <div class="metric">
                <div class="metric-value">{app.get('error_rate', 0):.2f}%</div>
                <div class="metric-label">Error Rate</div>
            </div>
        </div>
        
        <div class="card">
            <h2>Incident Summary</h2>
            <div class="metric">
                <div class="metric-value">{incidents.get('total', 0)}</div>
                <div class="metric-label">Total</div>
            </div>
            <div class="metric">
                <div class="metric-value status-healthy">{incidents.get('resolved', 0)}</div>
                <div class="metric-label">Resolved</div>
            </div>
            <div class="metric">
                <div class="metric-value status-warning">{incidents.get('escalated', 0)}</div>
                <div class="metric-label">Escalated</div>
            </div>
        </div>
        """
        
        if alerts:
            content += "<div class='card'><h2>Active Alerts</h2>"
            for alert in alerts[:10]:  # Show top 10 alerts
                content += f"<div class='alert alert-{alert.get('type', 'warning')}'>{alert.get('message', '')}</div>"
            content += "</div>"
        
        return content
    
    def generate_all_dashboards(self):
        """Generate all dashboard types"""
        dashboards = {
            "system_health": self.generate_system_health_dashboard(),
            "incident": self.generate_incident_dashboard(),
            "maintenance": self.generate_maintenance_dashboard(),
            "sla": self.generate_sla_dashboard(),
            "operational": self.generate_operational_overview()
        }
        
        for name, data in dashboards.items():
            # Save JSON data
            json_file = self.output_dir / f"{name}_dashboard.json"
            with open(json_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            # Generate HTML dashboard
            html_content = self.generate_html_dashboard(data, name)
            html_file = self.output_dir / f"{name}_dashboard.html"
            with open(html_file, 'w') as f:
                f.write(html_content)
            
            logger.info(f"Generated {name} dashboard: {json_file} and {html_file}")

def main():
    parser = argparse.ArgumentParser(description="HX Infrastructure Dashboard Generator")
    parser.add_argument("--data-dir", default="/var/log/hx-infrastructure",
                       help="Directory containing monitoring data")
    parser.add_argument("--output-dir", default="/var/www/html",
                       help="Directory to output dashboards")
    parser.add_argument("--dashboard", choices=["system_health", "incident", "maintenance", "sla", "operational", "all"],
                       default="all", help="Dashboard type to generate")
    
    args = parser.parse_args()
    
    generator = DashboardGenerator(args.data_dir, args.output_dir)
    
    if args.dashboard == "all":
        generator.generate_all_dashboards()
    else:
        # Generate specific dashboard
        if args.dashboard == "system_health":
            data = generator.generate_system_health_dashboard()
        elif args.dashboard == "incident":
            data = generator.generate_incident_dashboard()
        elif args.dashboard == "maintenance":
            data = generator.generate_maintenance_dashboard()
        elif args.dashboard == "sla":
            data = generator.generate_sla_dashboard()
        elif args.dashboard == "operational":
            data = generator.generate_operational_overview()
        
        # Save JSON and HTML
        json_file = Path(args.output_dir) / f"{args.dashboard}_dashboard.json"
        html_file = Path(args.output_dir) / f"{args.dashboard}_dashboard.html"
        
        with open(json_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        html_content = generator.generate_html_dashboard(data, args.dashboard)
        with open(html_file, 'w') as f:
            f.write(html_content)
        
        logger.info(f"Generated {args.dashboard} dashboard: {json_file} and {html_file}")

if __name__ == "__main__":
    main()
