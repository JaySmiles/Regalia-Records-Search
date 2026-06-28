#!/usr/bin/env python3
"""Apply duplicate-record fixes to the Regular App index.html (binary-safe)."""
import sys

path = r"B:\Attendance Apps\Regalia-Records-Search\www\index.html"
with open(path, "rb") as f:
    html = f.read().decode("utf-8")  # binary read

changes = []
N = "\r\n"

def sub(old, new, label):
    global html, changes
    if old in html:
        html = html.replace(old, new, 1)
        changes.append(label)
    else:
        print(f"WARN: {label} not found")

# ── FIX 1: getMergedEntries — remove _skippedQueueIds from remote filter ──
sub(
    f"    const remote = _sharedEntries{N}"
    f"      .filter(e => e && e.id && e.timestamp && !localIds.has(e.id) && !_skippedQueueIds.has(e.id)){N}"
    f"      .map(e => ({{ ...e, _remote: true }}));{N}"
    f"    return [...local, ...remote];",

    f"    // Remote entries are authoritative Firebase records — always show them.{N}"
    f"    // _skippedQueueIds only suppresses locally-queued pending writes, not confirmed Firebase entries.{N}"
    f"    const remote = _sharedEntries{N}"
    f"      .filter(e => e && e.id && e.timestamp && !localIds.has(e.id)){N}"
    f"      .map(e => ({{ ...e, _remote: true }}));{N}"
    f"    return [...local, ...remote];",

    "FIX 1: getMergedEntries remote filter"
)

# ── FIX 2: resolveTknDuplicate — try/catch, drop _skippedQueueIds.add ──
sub(
    f"    for (const dup of toDelete) {{{N}"
    f"      await zoneRef.child(dup.id).remove();{N}"
    f"      const log = getLog();{N}"
    f"      log.entries = log.entries.filter(e => e.id !== dup.id);{N}"
    f"      saveLog(log);{N}"
    f"      _sharedEntries = _sharedEntries.filter(e => e.id !== dup.id);{N}"
    f"      _skippedQueueIds.add(dup.id);{N}"
    f"    }}{N}"
    f"    if (toDelete.length > 0 && typeof renderLog === 'function') renderLog();",

    f"    for (const dup of toDelete) {{{N}"
    f"      try {{{N}"
    f"        await zoneRef.child(dup.id).remove();{N}"
    f"        // Only clean local state after confirmed Firebase delete{N}"
    f"        const log = getLog();{N}"
    f"        log.entries = log.entries.filter(e => e.id !== dup.id);{N}"
    f"        saveLog(log);{N}"
    f"        _sharedEntries = _sharedEntries.filter(e => e.id !== dup.id);{N}"
    f"      }} catch(removeErr) {{{N}"
    f"        console.warn('resolveTknDuplicate: failed to remove dup', dup.id, removeErr);{N}"
    f"      }}{N}"
    f"    }}{N}"
    f"    if (toDelete.length > 0 && typeof renderLog === 'function') renderLog();",

    "FIX 2: resolveTknDuplicate try/catch"
)

# ── FIX 3: pushToSharedLog — fix wrong ID added to _skippedQueueIds ──
sub(
    f"      console.log('pushToSharedLog: TKN already in Firebase, skipping write for', entry.name);{N}"
    f"      const log = getLog();{N}"
    f"      log.entries = log.entries.filter(e => e.id !== entry.id);{N}"
    f"      saveLog(log);{N}"
    f"      saveQueue(getQueue().filter(q => q.id !== entry.id));{N}"
    f"      _skippedQueueIds.add(existing.id);{N}"
    f"      return;",

    f"      console.log('pushToSharedLog: TKN already in Firebase, skipping write for', entry.name);{N}"
    f"      const log = getLog();{N}"
    f"      log.entries = log.entries.filter(e => e.id !== entry.id);{N}"
    f"      saveLog(log);{N}"
    f"      saveQueue(getQueue().filter(q => q.id !== entry.id));{N}"
    f"      // Suppress our OWN pending write - NOT the existing valid Firebase entry{N}"
    f"      _skippedQueueIds.add(entry.id);{N}"
    f"      return;",

    "FIX 3: pushToSharedLog wrong ID"
)

# ── FIX 4a: submitCheckin lock start ──
sub(
    f"  // \u2500\u2500 Check-in Submit \u2500\u2500{N}"
    f"  async function submitCheckin(mode) {{{N}"
    f"    let name, tkn = '', cls = '', phone = '', invitedBy = '', fields;",

    f"  // \u2500\u2500 Check-in Submit \u2500\u2500{N}"
    f"  let _isSubmitting = false;{N}"
    f"  async function submitCheckin(mode) {{{N}"
    f"    if (_isSubmitting) return; // prevent triple-tap race{N}"
    f"    _isSubmitting = true;{N}"
    f"    try {{{N}"
    f"    let name, tkn = '', cls = '', phone = '', invitedBy = '', fields;",

    "FIX 4a: submitCheckin lock start"
)

# ── FIX 4b: submitCheckin lock end ──
sub(
    f"    doCheckinSubmit(mode, name, tkn, cls, phone, invitedBy, fields, timestamp, id);{N}"
    f"  }}{N}"
    f"{N}"
    f"  async function doCheckinSubmit(",

    f"    doCheckinSubmit(mode, name, tkn, cls, phone, invitedBy, fields, timestamp, id);{N}"
    f"    }} finally {{{N}"
    f"      _isSubmitting = false;{N}"
    f"    }}{N}"
    f"  }}{N}"
    f"{N}"
    f"  async function doCheckinSubmit(",

    "FIX 4b: submitCheckin lock end"
)

print(f"\nApplied {len(changes)} changes:")
for c in changes:
    print(f"  OK: {c}")

with open(path, "wb") as f:
    f.write(html.encode("utf-8"))
print("\nDone.")
