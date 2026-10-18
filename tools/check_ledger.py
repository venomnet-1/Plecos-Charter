#!/usr/bin/env python3
"""Check recorded workflow consistency. Never execute recorded commands."""
import argparse
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path

class LedgerError(ValueError):
    pass

KINDS = {
    'charter_adopted', 'scope_proposed', 'scope_approved', 'decision',
    'implementation_completed', 'candidate_created', 'verification_recorded',
    'acceptance_recorded', 'publication_authorized', 'release_recorded',
    'scope_closed', 'authorization_revoked', 'issue_opened', 'issue_resolved',
    'correction',
}
OWNER_KINDS = {'charter_adopted', 'scope_approved', 'acceptance_recorded',
               'publication_authorized', 'authorization_revoked'}
ROLES = {'owner', 'maintainer', 'assistant', 'reviewer'}

def require(condition, message):
    if not condition:
        raise LedgerError(message)

def text(obj, key):
    value = obj.get(key)
    require(isinstance(value, str) and bool(value.strip()), f'{key} must be nonempty text')
    return value

def file_hash(root, reference):
    require(isinstance(reference, dict), 'file reference must be an object')
    raw = text(reference, 'path')
    path = Path(raw)
    require(not path.is_absolute() and '..' not in path.parts,
            'file paths must be relative and cannot traverse parents')
    resolved = (root / path).resolve()
    require(resolved.is_relative_to(root), 'file path escapes project root')
    require(resolved.is_file(), f'referenced file is missing: {raw}')
    expected = text(reference, 'sha256')
    require(re.fullmatch(r'[0-9a-f]{64}', expected) is not None,
            'sha256 must be 64 lowercase hexadecimal characters')
    with resolved.open('rb') as stream:
        digest = hashlib.sha256()
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    require(digest.hexdigest() == expected, f'file hash mismatch: {raw}')
    return raw

def strict_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'duplicate JSON field')
        result[key] = value
    return result

def reject_constant(value):
    raise LedgerError('non-finite JSON constants are not allowed')

def read_events(path):
    require(path.is_file(), 'docs/ledger.jsonl is missing')
    require(path.stat().st_size <= 20 * 1024 * 1024, 'ledger exceeds starter limit of 20 MiB')
    events = []
    try:
        for line_no, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
            require(bool(line.strip()), f'blank line at {line_no}')
            try:
                event = json.loads(line, object_pairs_hook=strict_object, parse_constant=reject_constant)
            except json.JSONDecodeError:
                raise LedgerError(f'invalid JSON at line {line_no}') from None
            require(isinstance(event, dict), f'line {line_no} must be a JSON object')
            events.append(event)
    except UnicodeError:
        raise LedgerError('ledger must be UTF-8') from None
    require(events, 'ledger is empty; no authority has been recorded')
    return events

def validate(root):
    root = Path(root).resolve()
    ledger_path = (root / 'docs/ledger.jsonl').resolve()
    require(ledger_path.is_relative_to(root), 'ledger path escapes project root')
    events = read_events(ledger_path)
    seen = {}
    scopes = {}
    candidates = {}
    issues = {}
    charter = None
    previous_time = None
    simulation = None
    for index, event in enumerate(events, 1):
        try:
            event_id = text(event, 'id')
            require(event_id == f'E-{index:04d}', 'IDs must be consecutive E-0001, E-0002, ...')
            stamp = text(event, 'at')
            require(re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z', stamp) is not None, 'at must be a UTC timestamp ending in Z')
            try:
                moment = datetime.fromisoformat(stamp[:-1] + '+00:00')
            except ValueError:
                raise LedgerError('at is not a valid timestamp') from None
            require(previous_time is None or moment >= previous_time, 'timestamps must be nondecreasing')
            previous_time = moment
            kind = text(event, 'kind')
            require(kind in KINDS, 'unknown event kind')
            actor = event.get('actor')
            require(isinstance(actor, dict), 'actor must be an object')
            text(actor, 'name')
            require(isinstance(actor.get('role'), str) and actor['role'] in ROLES, 'unknown actor role')
            demo = event.get('simulation_only', False)
            require(isinstance(demo, bool), 'simulation_only must be boolean')
            if simulation is None:
                simulation = demo
            require(demo == simulation, 'cannot mix simulated and real events')
            text(event, 'summary')
            details = event.get('details')
            require(isinstance(details, dict), 'details must be an object')
            if kind in OWNER_KINDS:
                require(actor['role'] == 'owner', f'{kind} must be attributed to the owner')
                text(details, 'approval_ref')
            if kind == 'charter_adopted':
                require(charter is None and index == 1, 'one charter adoption must be the first event')
                charter = text(details, 'revision')
                file_hash(root, details.get('charter'))
            else:
                require(charter is not None, 'adopt charter before controlled work')
                if kind == 'scope_proposed':
                    sid = text(event, 'scope')
                    require(sid not in scopes, 'scope ID already exists; use a fresh ID')
                    checks = details.get('required_checks')
                    require(isinstance(checks, list) and len(checks) > 0 and
                            all(isinstance(x, str) and x.strip() for x in checks),
                            'required_checks must be a nonempty list of check names')
                    require(len(checks) == len(set(checks)), 'required check names must be unique')
                    for key in ['included', 'excluded', 'criteria']:
                        text(details, key)
                    scopes[sid] = {'proposal': event_id, 'version': text(event, 'version'),
                                   'checks': checks, 'approved': False, 'revoked': False,
                                   'implemented': False, 'candidate': None, 'closed': False}
                elif kind in {'correction', 'issue_opened', 'issue_resolved'}:
                    if kind == 'correction':
                        require(text(details, 'corrects') in seen, 'correction must reference an earlier event')
                        text(details, 'explanation')
                    elif kind == 'issue_opened':
                        iid = text(details, 'issue_id')
                        require(iid not in issues, 'issue ID already exists')
                        require(isinstance(details.get('state'), str) and details['state'] in {'OPEN', 'DEFERRED'}, 'issue state must be OPEN or DEFERRED')
                        issues[iid] = details['state']
                    else:
                        iid = text(details, 'issue_id')
                        require(iid in issues and issues[iid] != 'RESOLVED', 'issue is missing or already resolved')
                        file_hash(root, details.get('evidence'))
                        issues[iid] = 'RESOLVED'
                else:
                    sid = text(event, 'scope')
                    require(sid in scopes, 'scope must reference an earlier proposal')
                    scope = scopes[sid]
                    require(text(event, 'version') == scope['version'], 'scope version mismatch')
                    require(not scope['closed'], 'scope is already closed')
                    if kind == 'scope_approved':
                        require(not scope['approved'] and not scope['revoked'], 'scope approval already recorded or revoked')
                        require(details.get('proposal') == scope['proposal'], 'approval must reference exact proposal event')
                        require(details.get('charter_revision') == charter, 'approval charter revision mismatch')
                        scope['approved'] = True
                    else:
                        require(scope['approved'], 'scope has not been approved')
                        require(not scope['revoked'], 'scope authority has been revoked')
                        if kind == 'authorization_revoked':
                            scope['revoked'] = True
                        elif kind == 'decision':
                            text(details, 'reason')
                        elif kind == 'implementation_completed':
                            scope['implemented'] = True
                            scope['candidate'] = None
                        elif kind == 'candidate_created':
                            require(scope['implemented'], 'record implementation before creating a candidate')
                            cid = text(details, 'candidate')
                            require(cid not in candidates, 'candidate ID already exists')
                            artifact = details.get('artifact')
                            path = file_hash(root, artifact)
                            require(not any(c['path'] == path for c in candidates.values()),
                                    'candidates must use distinct artifact paths to preserve history')
                            candidates[cid] = {'scope': sid, 'path': path, 'sha256': artifact['sha256'],
                                               'checks': {}, 'accepted': False, 'destination': None,
                                               'released': False}
                            scope['candidate'] = cid
                        elif kind in {'verification_recorded', 'acceptance_recorded',
                                      'publication_authorized', 'release_recorded', 'scope_closed'}:
                            cid = text(details, 'candidate')
                            require(cid in candidates and cid == scope['candidate'],
                                    'event must reference latest candidate for the scope')
                            candidate = candidates[cid]
                            if kind == 'verification_recorded':
                                require(not candidate['released'], 'cannot change verification after release')
                                name = text(details, 'check')
                                require(name in scope['checks'], 'check is not named in the approved scope')
                                require(isinstance(details.get('result'), str) and details['result'] in {'PASS', 'FAIL', 'BLOCKED', 'NOT_TESTED'}, 'invalid verification result')
                                file_hash(root, details.get('evidence'))
                                candidate['checks'][name] = details['result']
                                # New verification changes the basis of acceptance/publication.
                                candidate['accepted'] = False
                                candidate['destination'] = None
                            elif kind == 'acceptance_recorded':
                                require(not candidate['released'], 'cannot alter acceptance after release')
                                require(isinstance(details.get('result'), str) and details['result'] in {'ACCEPTED', 'REJECTED'}, 'invalid acceptance result')
                                if details['result'] == 'ACCEPTED':
                                    require(all(candidate['checks'].get(x) == 'PASS' for x in scope['checks']),
                                            'every required check must PASS on this candidate')
                                candidate['accepted'] = details['result'] == 'ACCEPTED'
                                candidate['destination'] = None
                            elif kind == 'publication_authorized':
                                require(candidate['accepted'] and not candidate['released'],
                                        'publication requires an accepted, unreleased candidate')
                                candidate['destination'] = text(details, 'destination')
                            elif kind == 'release_recorded':
                                require(candidate['accepted'] and candidate['destination'] and not candidate['released'],
                                        'release requires acceptance and publication authorization')
                                require(details.get('destination') == candidate['destination'], 'release destination mismatch')
                                text(details, 'location')
                                file_hash(root, details.get('recovery_evidence'))
                                candidate['released'] = True
                            else:
                                require(candidate['accepted'], 'closeout requires acceptance')
                                require(not candidate['destination'] or candidate['released'],
                                        'authorized publication needs a release receipt before closeout')
                                scope['closed'] = True
            seen[event_id] = event
        except LedgerError as error:
            raise LedgerError(f'event {index}: {error}') from None
    return {'events': len(events), 'scopes': len(scopes), 'candidates': len(candidates),
            'releases': sum(c['released'] for c in candidates.values()),
            'open_issues': sum(state != 'RESOLVED' for state in issues.values()),
            'simulation_only': simulation}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('project', type=Path)
    args = parser.parse_args()
    try:
        report = validate(args.project)
    except (LedgerError, OSError) as error:
        print(f'FAIL: {error}')
        return 1
    mode = 'FICTIONAL SIMULATION' if report['simulation_only'] else 'RECORDED WORKFLOW'
    print(f"PASS ({mode}): {report['events']} events; {report['scopes']} scope(s); "
          f"{report['candidates']} candidate(s); {report['releases']} release receipt(s); "
          f"{report['open_issues']} unresolved issue(s).")
    print('Consistency check only; not proof of human consent, security, or deployment.')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
