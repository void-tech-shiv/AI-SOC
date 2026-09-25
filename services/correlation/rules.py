from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta

def get_alert_users(alert: dict) -> set:
    users = set()
    if alert.get('evidence'):
        ev = alert['evidence']
        for key in ['username', 'user', 'database user']:
            if key in ev and ev[key]:
                users.add(str(ev[key]).strip().lower())
    return users

def get_alert_ips(alert: dict) -> set:
    ips = set()
    if alert.get('evidence'):
        ev = alert['evidence']
        for key in ['ip_address', 'src_ip', 'source_ip', 'ip']:
            if key in ev and ev[key]:
                ips.add(str(ev[key]).strip().lower())
    return ips

class CorrelationRule:
    rule_id: str
    name: str
    severity: str
    time_window_minutes: int = 1440

    def evaluate(self, alerts: List[dict]) -> List[dict]:
        raise NotImplementedError()

class Corr001(CorrelationRule):
    rule_id = 'CORR-001'
    name = 'Coordinated Authentication Attack'
    severity = 'high'
    time_window_minutes = 15

    def evaluate(self, alerts: List[dict]) -> List[dict]:
        candidates = []
        det001_alerts = [a for a in alerts if a['rule_id'] == 'DET-001']
        
        # Group by username and IP
        groups = {}
        for a in det001_alerts:
            users = get_alert_users(a)
            ips = get_alert_ips(a)
            keys = list(users) + list(ips)
            for k in keys:
                if k not in groups:
                    groups[k] = []
                groups[k].append(a)
        
        for k, group in groups.items():
            if len(group) > 1:
                # check time window 15 min
                group.sort(key=lambda x: x['created_at'])
                cluster = [group[0]]
                for a in group[1:]:
                    if (a['created_at'] - cluster[-1]['created_at']) <= timedelta(minutes=15):
                        cluster.append(a)
                if len(cluster) > 1:
                    candidates.append({
                        'rule': self,
                        'alerts': cluster,
                        'key_entity': k
                    })
        return candidates

class Corr002(CorrelationRule):
    rule_id = 'CORR-002'
    name = 'Potential Endpoint Compromise'
    severity = 'critical'
    time_window_minutes = 30

    def evaluate(self, alerts: List[dict]) -> List[dict]:
        candidates = []
        det002_alerts = [a for a in alerts if a['rule_id'] == 'DET-002']
        if not det002_alerts:
            return []
            
        for a2 in det002_alerts:
            users2 = get_alert_users(a2)
            ips2 = get_alert_ips(a2)
            keys2 = set(list(users2) + list(ips2))
            
            related = [a2]
            for a in alerts:
                if a['id'] == a2['id']: continue
                users = get_alert_users(a)
                ips = get_alert_ips(a)
                keys = set(list(users) + list(ips))
                
                if keys.intersection(keys2):
                    if abs((a['created_at'] - a2['created_at']).total_seconds()) <= 1800:
                        related.append(a)
            if len(related) > 1:
                candidates.append({
                    'rule': self,
                    'alerts': related,
                    'key_entity': list(keys2)[0] if keys2 else 'unknown'
                })
        return candidates

class Corr003(CorrelationRule):
    rule_id = 'CORR-003'
    name = 'Potential Data Exfiltration'
    severity = 'critical'
    time_window_minutes = 30

    def evaluate(self, alerts: List[dict]) -> List[dict]:
        candidates = []
        det003_alerts = [a for a in alerts if a['rule_id'] == 'DET-003']
        det004_alerts = [a for a in alerts if a['rule_id'] == 'DET-004']
        
        for a3 in det003_alerts:
            keys3 = set(list(get_alert_users(a3)) + list(get_alert_ips(a3)))
            for a4 in det004_alerts:
                keys4 = set(list(get_alert_users(a4)) + list(get_alert_ips(a4)))
                if keys3.intersection(keys4): # Removed empty context fallback
                    if abs((a3['created_at'] - a4['created_at']).total_seconds()) <= 1800:
                        candidates.append({
                            'rule': self,
                            'alerts': [a3, a4],
                            'key_entity': list(keys3.intersection(keys4))[0]
                        })
        return candidates

class Corr004(CorrelationRule):
    rule_id = 'CORR-004'
    name = 'Critical Event Escalation'
    severity = 'critical'
    time_window_minutes = 20

    def evaluate(self, alerts: List[dict]) -> List[dict]:
        candidates = []
        det005_alerts = [a for a in alerts if a['rule_id'] == 'DET-005']
        other_critical = [a for a in alerts if a['severity'] == 'critical' and a['rule_id'] != 'DET-005']
        
        for a5 in det005_alerts:
            keys5 = set(list(get_alert_users(a5)) + list(get_alert_ips(a5)))
            related = [a5]
            for ac in other_critical:
                keysc = set(list(get_alert_users(ac)) + list(get_alert_ips(ac)))
                if keys5.intersection(keysc):
                    if abs((a5['created_at'] - ac['created_at']).total_seconds()) <= 1200:
                        related.append(ac)
            if len(related) > 1:
                candidates.append({
                    'rule': self,
                    'alerts': related,
                    'key_entity': list(keys5)[0] if keys5 else 'unknown'
                })
        return candidates

RULES = [Corr001(), Corr002(), Corr003(), Corr004()]
