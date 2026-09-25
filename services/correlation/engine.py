import hashlib
from typing import List, Dict, Any
from .rules import RULES, get_alert_users, get_alert_ips
from .scoring import calculate_priority_score
from datetime import datetime

class IncidentCandidate:
    def __init__(self, incident_key, title, description, severity, confidence_score, priority_score, alert_ids, affected_users, affected_ips, first_seen, last_seen, correlation_rule, evidence):
        self.incident_key = incident_key
        self.title = title
        self.description = description
        self.severity = severity
        self.confidence_score = confidence_score
        self.priority_score = priority_score
        self.alert_ids = alert_ids
        self.affected_users = affected_users
        self.affected_ips = affected_ips
        self.first_seen = first_seen
        self.last_seen = last_seen
        self.correlation_rule = correlation_rule
        self.evidence = evidence

def correlate_alerts(alerts_raw: List[Any]) -> List[IncidentCandidate]:
    alerts = []
    for a in alerts_raw:
        alerts.append({
            'id': a.id,
            'rule_id': a.rule_id,
            'severity': a.severity,
            'created_at': a.created_at,
            'evidence': a.evidence,
            'confidence_score': a.confidence_score
        })

    candidates = []
    used_alerts = set()
    
    for rule in RULES:
        matches = rule.evaluate(alerts)
        for match in matches:
            cluster = match['alerts']
            # skip if any alert is already used in higher priority rules
            if any(a['id'] in used_alerts for a in cluster):
                continue
                
            for a in cluster:
                used_alerts.add(a['id'])
                
            alert_ids = sorted([a['id'] for a in cluster])
            first_seen = min(a['created_at'] for a in cluster)
            last_seen = max(a['created_at'] for a in cluster)
            
            users = set()
            ips = set()
            for a in cluster:
                users.update(get_alert_users(a))
                ips.update(get_alert_ips(a))
            
            avg_confidence = sum(a['confidence_score'] or 0.0 for a in cluster) / len(cluster)
            priority = calculate_priority_score(rule.severity, len(cluster), avg_confidence, rule.rule_id)
            
            # Deterministic key: rule + entity + time bucket
            bucket_minutes = getattr(rule, 'time_window_minutes', 1440)
            if bucket_minutes >= 1440:
                time_bucket = first_seen.strftime('%Y-%m-%d')
            else:
                bucket_start = first_seen.replace(
                    minute=(first_seen.minute // bucket_minutes) * bucket_minutes,
                    second=0,
                    microsecond=0
                )
                time_bucket = bucket_start.isoformat()
            
            key_raw = f'{rule.rule_id}-{match["key_entity"]}-{time_bucket}'
            incident_key = hashlib.sha256(key_raw.encode()).hexdigest()[:16]
            
            candidates.append(IncidentCandidate(
                incident_key=incident_key,
                title=rule.name,
                description=f'Correlated {len(cluster)} alerts using {rule.rule_id}',
                severity=rule.severity,
                confidence_score=avg_confidence,
                priority_score=priority,
                alert_ids=alert_ids,
                affected_users=list(users),
                affected_ips=list(ips),
                first_seen=first_seen,
                last_seen=last_seen,
                correlation_rule=rule.rule_id,
                evidence={'key_entity': match['key_entity']}
            ))
            
    # CORR-005: Fallback for high/critical
    for a in alerts:
        if a['id'] not in used_alerts and a['severity'] in ('high', 'critical'):
            used_alerts.add(a['id'])
            users = list(get_alert_users(a))
            ips = list(get_alert_ips(a))
            
            key_raw = f'CORR-005-{a["id"]}'
            incident_key = hashlib.sha256(key_raw.encode()).hexdigest()[:16]
            
            priority = calculate_priority_score(a['severity'], 1, a['confidence_score'] or 0.0, 'CORR-005')
            
            candidates.append(IncidentCandidate(
                incident_key=incident_key,
                title='Standalone Critical/High Alert',
                description='Single un-correlated high or critical severity alert.',
                severity=a['severity'],
                confidence_score=a['confidence_score'] or 0.0,
                priority_score=priority,
                alert_ids=[a['id']],
                affected_users=users,
                affected_ips=ips,
                first_seen=a['created_at'],
                last_seen=a['created_at'],
                correlation_rule='CORR-005',
                evidence={'source_alert': a['id']}
            ))
            
    return candidates
