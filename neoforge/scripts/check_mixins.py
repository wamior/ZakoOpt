#!/usr/bin/env python3
"""Static check of Mixin targets against a class index (see classindex.py).

usage: check_mixins.py INDEX.pkl SRC_DIR [--only-list]
Prints one line per broken reference:  <file>: <what>
Exit code 0 even when problems are found; read the output.
"""
import os, pickle, re, sys

idx = pickle.load(open(sys.argv[1], 'rb'))
src = sys.argv[2]


def supers(cls):
    seen = []
    todo = [cls]
    while todo:
        c = todo.pop()
        if c in seen or c not in idx:
            continue
        seen.append(c)
        sup, ifs, *_ = idx[c]
        if sup:
            todo.append(sup)
        todo.extend(ifs)
    return seen


def has_method(cls, name, desc=None):
    for c in supers(cls):
        for n, d, _ in idx[c][3]:
            if n == name and (desc is None or d == desc or d.startswith(desc.split(')')[0] + ')') and desc.endswith(')') ):
                return True
    return False


def has_field(cls, name):
    for c in supers(cls):
        for n, d, _ in idx[c][2]:
            if n == name:
                return True
    return False


def resolve(simple, imports, pkg, text):
    """simple/nested name -> internal name or None"""
    parts = simple.split('.')
    head = parts[0]
    base = None
    if head in imports:
        base = imports[head]
    else:
        for cand in (pkg + '/' + head, 'java/lang/' + head):
            if cand in idx:
                base = cand
                break
        if base is None:
            for imp in imports.get('*', []):
                if imp + '/' + head in idx:
                    base = imp + '/' + head
                    break
    if base is None:
        return None
    return base + ''.join('$' + p for p in parts[1:])


def split_method_ref(s):
    # "name", "name(Lx;)V", "Lowner;name(desc)ret" ,"owner.name"
    s = s.strip()
    m = re.match(r'^(?:L([^;]+);)?([A-Za-z0-9_$<>]+)(\(.*)?$', s)
    if not m:
        return None, s, None
    return m.group(1), m.group(2), m.group(3)


problems = []
checked = 0

for dp, _, fs in os.walk(src):
    for f in fs:
        if not f.endswith('.java'):
            continue
        path = os.path.join(dp, f)
        text = open(path, encoding='utf-8').read()
        if '@Mixin' not in text:
            continue
        rel = os.path.relpath(path, src)
        pkg = re.search(r'^package ([\w.]+);', text, re.M).group(1).replace('.', '/')
        imports = {}
        for m in re.finditer(r'^import (static )?([\w.]+)(\.\*)?;', text, re.M):
            if m.group(1):
                continue
            if m.group(3):
                imports.setdefault('*', []).append(m.group(2).replace('.', '/'))
            else:
                fq = m.group(2).replace('.', '/')
                imports[fq.split('/')[-1]] = fq
        mm = re.search(r'@Mixin\s*\((.*?)\)\s*\n\s*(?:@\w+(?:\([^)]*\))?\s*)*(?:public\s+|abstract\s+)*(?:class|interface)\s+(\w+)', text, re.S)
        if not mm:
            problems.append((rel, 'cannot parse @Mixin'))
            continue
        arg = mm.group(1)
        targets = []
        for c in re.findall(r'([\w.]+)\.class', arg):
            r = resolve(c, imports, pkg, text)
            if r is None or r not in idx:
                problems.append((rel, 'target class missing: %s' % c))
            else:
                targets.append(r)
        for t in re.findall(r'"([\w./$]+)"', arg.split('targets')[-1] if 'targets' in arg else ''):
            t = t.replace('.', '/')
            if t not in idx:
                problems.append((rel, 'target class missing: %s' % t))
            else:
                targets.append(t)
        checked += 1
        if not targets:
            continue

        def any_target(pred):
            return any(pred(t) for t in targets)


        # @Inject handler arity: (target args..., CallbackInfo) or just (CallbackInfo)
        for im in re.finditer(r'@Inject\s*\((.*?)\)\s*\n\s*(?:@\w+(?:\([^)]*\))?\s*)*(?:public\s+|private\s+|protected\s+|static\s+)*void\s+([\w$]+)\s*\(([^)]*)\)', text, re.S):
            mm3 = re.search(r'method\s*=\s*"([^"(]+)"', im.group(1))
            if not mm3:
                continue
            params = [x for x in re.split(r',\s*(?![^<]*>)', im.group(3).strip()) if x.strip()]
            params = [x for x in params if '@Local' not in x and '@Share' not in x]
            if len(params) <= 1:
                continue
            n = len(params) - 1
            counts = set()
            for t in targets:
                own = [m for m in idx.get(t, (0, 0, 0, []))[3] if m[0] == mm3.group(1)]
                for c in ([t] if own else supers(t)):
                    for nm, d, _ in idx[c][3]:
                        if nm == mm3.group(1):
                            counts.add(len(re.findall(r'\[*(?:L[^;]+;|[BCDFIJSZ])', d.split(')')[0][1:])))
            if counts and n not in counts:
                problems.append((rel, '@Inject %s handler has %d args, target has %s' % (im.group(2), n, sorted(counts))))
        # handler methods' method="..." lists
        for ann in re.finditer(r'@(Inject|Redirect|ModifyArg|ModifyArgs|ModifyVariable|ModifyConstant|WrapOperation|WrapWithCondition|ModifyExpressionValue|WrapMethod|ModifyReturnValue|ModifyReceiver|Overwrite)\s*\((.*?)\)\s*\n\s*(?:@\w+(?:\([^)]*\))?\s*)*(?:public|private|protected|static|\w)', text, re.S):
            body = ann.group(2)
            mm2 = re.search(r'method\s*=\s*(\{[^}]*\}|"[^"]*")', body, re.S)
            if mm2:
                for s in re.findall(r'"([^"]*)"', mm2.group(1)):
                    owner, name, desc = split_method_ref(s)
                    if '*' in s:
                        continue
                    if name in ('<init>', '<clinit>'):
                        ok = any_target(lambda t: has_method(t, name, desc))
                    else:
                        ok = any_target(lambda t: has_method(t, name, desc))
                    if not ok:
                        problems.append((rel, '@%s method not found: %s' % (ann.group(1), s)))
            for at in re.finditer(r'target\s*=\s*"([^"]*)"', body):
                tgt = at.group(1)
                m3 = re.match(r'^L([^;]+);([\w$<>]+)(\(.*)?$', tgt)
                if m3:
                    owner, name, desc = m3.groups()
                    if owner.startswith(('java/','javax/')):
                        continue
                    if owner not in idx:
                        problems.append((rel, 'INVOKE owner class missing: %s' % owner))
                    elif desc and not has_method(owner, name, desc) :
                        problems.append((rel, 'INVOKE target method not found: %s' % tgt))
                    elif not desc and not (has_method(owner, name) or has_field(owner, name)):
                        problems.append((rel, 'FIELD/INVOKE target not found: %s' % tgt))
        for sh in re.finditer(r'@Shadow(?:\s*\([^)]*\))?\s*(?:@\w+(?:\([^)]*\))?\s*)*((?:public|private|protected|static|final|abstract|\s)+)([\w<>\[\],.? ]+?)\s+(\w+)\s*(\(|;|=)', text):
            name, kind = sh.group(3), sh.group(4)
            if name.startswith('zakoopt$'):
                continue
            if kind == '(':
                if not any_target(lambda t: has_method(t, name)):
                    problems.append((rel, '@Shadow method not found: %s' % name))
            elif not any_target(lambda t: has_field(t, name)):
                problems.append((rel, '@Shadow field not found: %s' % name))
        for ac in re.finditer(r'@(Accessor|Invoker)\s*(?:\(\s*(?:value\s*=\s*)?"([^"]*)"\s*\))?\s*(?:@\w+(?:\([^)]*\))?\s*)*(?:static\s+)?[\w<>\[\],.? ]+?\s+(\w+)\s*\(', text):
            kind, val, mname = ac.groups()
            name = val
            if not name:
                m4 = re.match(r'^(get|set|is|call|invoke)([A-Z]\w*)$', mname)
                name = (m4.group(2)[0].lower() + m4.group(2)[1:]) if m4 else mname
            if kind == 'Accessor':
                if not any_target(lambda t: has_field(t, name)):
                    problems.append((rel, '@Accessor field not found: %s' % name))
            else:
                if not any_target(lambda t: has_method(t, name)):
                    problems.append((rel, '@Invoker method not found: %s' % name))

for rel, msg in sorted(problems):
    print('%s: %s' % (rel, msg))
print('-- checked %d mixin classes, %d problems' % (checked, len(problems)), file=sys.stderr)
