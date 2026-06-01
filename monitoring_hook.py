import os, subprocess, json, datetime

MONITOR_PATH = r'C:\AI_WorkDir\GitHub\prospera-agent-orchestrator'
LOG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'execution_log.jsonl')

def trigger_monitoring(context=None):
    entry = {'timestamp': datetime.datetime.utcnow().isoformat(), 'repo': 'prospera-infra-compliance', 'context': context or {}}
    with open(LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    try:
        subprocess.Popen(['python', 'monitoring_agent.py'], cwd=MONITOR_PATH)
    except Exception:
        pass

def auto_remediate(error_context=None):
    entry = {'timestamp': datetime.datetime.utcnow().isoformat(), 'error': str((error_context or {}).get('error', '')), 'status': 'ATTEMPTED'}
    log = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'remediation_log.jsonl')
    with open(log, 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    return entry
