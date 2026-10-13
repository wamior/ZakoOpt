import zipfile, struct, sys, pickle, os

def parse(data):
    # returns (this_class, super, interfaces, fields[(name,desc)], methods[(name,desc)])
    pos = 8
    n = struct.unpack('>H', data[pos:pos+2])[0]; pos += 2
    cp = [None]*n
    i = 1
    while i < n:
        t = data[pos]; pos += 1
        if t == 1:
            l = struct.unpack('>H', data[pos:pos+2])[0]; pos += 2
            cp[i] = data[pos:pos+l].decode('utf-8', 'replace'); pos += l
        elif t in (3,4): pos += 4
        elif t in (5,6): pos += 8; i += 1
        elif t in (7,8,16,19,20): cp[i] = ('r', struct.unpack('>H', data[pos:pos+2])[0]); pos += 2
        elif t in (9,10,11,12,17,18): pos += 4
        elif t == 15: pos += 3
        else: raise Exception('cp tag %d' % t)
        i += 1
    def cls(idx):
        v = cp[idx]; return cp[v[1]] if v else None
    pos += 2  # access
    this = cls(struct.unpack('>H', data[pos:pos+2])[0]); pos += 2
    sup_i = struct.unpack('>H', data[pos:pos+2])[0]; pos += 2
    sup = cls(sup_i) if sup_i else None
    ic = struct.unpack('>H', data[pos:pos+2])[0]; pos += 2
    ifs = []
    for _ in range(ic):
        ifs.append(cls(struct.unpack('>H', data[pos:pos+2])[0])); pos += 2
    def members():
        nonlocal pos
        out = []
        c = struct.unpack('>H', data[pos:pos+2])[0]; pos += 2
        for _ in range(c):
            acc, ni, di, ac = struct.unpack('>HHHH', data[pos:pos+8]); pos += 8
            for _ in range(ac):
                pos += 2
                l = struct.unpack('>I', data[pos:pos+4])[0]; pos += 4 + l
            out.append((cp[ni], cp[di], acc))
        return out
    f = members(); m = members()
    return this, sup, ifs, f, m

def build(jars):
    idx = {}
    for j in jars:
        try:
            z = zipfile.ZipFile(j)
        except Exception:
            continue
        for name in z.namelist():
            if name.endswith('.class') and not name.startswith('META-INF'):
                try:
                    this, sup, ifs, f, m = parse(z.read(name))
                except Exception as e:
                    continue
                idx.setdefault(this, (sup, ifs, f, m, os.path.basename(j)))
    return idx

if __name__ == '__main__':
    jars = sys.argv[2:]
    idx = build(jars)
    pickle.dump(idx, open(sys.argv[1], 'wb'))
    print(len(idx), 'classes')
