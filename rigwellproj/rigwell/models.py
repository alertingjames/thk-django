from django.db import models

# Create your models here.

class RWMember(models.Model):
    name = models.CharField(max_length=50)
    email = models.CharField(max_length=80)
    password = models.CharField(max_length=30)
    role = models.CharField(max_length=100)
    status = models.CharField(max_length=20)


class Rig(models.Model):
    member_id = models.CharField(max_length=11)
    name = models.CharField(max_length=200)
    type = models.CharField(max_length=100)
    contractor = models.CharField(max_length=200)
    picture_url = models.CharField(max_length=1000)
    created_time = models.CharField(max_length=50)
    status = models.CharField(max_length=20)


class Well(models.Model):
    rig_id = models.CharField(max_length=11)
    name = models.CharField(max_length=200)
    field = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    well_start_time = models.CharField(max_length=50)
    well_end_time = models.CharField(max_length=50)
    status = models.CharField(max_length=20)


class Activity(models.Model):
    rig_id = models.CharField(max_length=11)
    well_id = models.CharField(max_length=11)
    name = models.CharField(max_length=200)
    number = models.CharField(max_length=20)
    hole = models.CharField(max_length=200)
    time_start = models.CharField(max_length=50)
    time_end = models.CharField(max_length=50)
    depth_start = models.CharField(max_length=50)
    depth_end = models.CharField(max_length=50)
    total_rows = models.CharField(max_length=11)
    saved_rows = models.CharField(max_length=11)
    status = models.CharField(max_length=20)


class TimeSDLField(models.Model):
    field_name = models.CharField(max_length=100)

class TDExtendedField(models.Model):
    field_name = models.CharField(max_length=100)

class TDTIHField(models.Model):
    field_name = models.CharField(max_length=100)

class TDDrlgField(models.Model):
    field_name = models.CharField(max_length=100)

class TDPOHField(models.Model):
    field_name = models.CharField(max_length=100)



class TimeSDL(models.Model):
    rig_id = models.CharField(max_length=11)
    well_id = models.CharField(max_length=11)
    act_id = models.CharField(max_length=11)
    a = models.CharField(max_length=100)
    b = models.CharField(max_length=100)
    c = models.CharField(max_length=100)
    d = models.CharField(max_length=100)
    e = models.CharField(max_length=100)
    f = models.CharField(max_length=100)
    g = models.CharField(max_length=100)
    h = models.CharField(max_length=100)
    i = models.CharField(max_length=100)
    status = models.CharField(max_length=100)


class TDExtended(models.Model):
    rig_id = models.CharField(max_length=11)
    well_id = models.CharField(max_length=11)
    act_id = models.CharField(max_length=11)

    a = models.CharField(max_length=100)
    b = models.CharField(max_length=100)
    c = models.CharField(max_length=100)
    d = models.CharField(max_length=100)
    e = models.CharField(max_length=100)
    f = models.CharField(max_length=100)
    g = models.CharField(max_length=100)
    h = models.CharField(max_length=100)
    i = models.CharField(max_length=100)
    j = models.CharField(max_length=100)

    k = models.CharField(max_length=100)
    l = models.CharField(max_length=100)
    m = models.CharField(max_length=100)
    n = models.CharField(max_length=100)
    o = models.CharField(max_length=100)
    p = models.CharField(max_length=100)
    q = models.CharField(max_length=100)
    r = models.CharField(max_length=100)
    s = models.CharField(max_length=100)
    t = models.CharField(max_length=100)

    u = models.CharField(max_length=100)
    v = models.CharField(max_length=100)
    w = models.CharField(max_length=100)
    x = models.CharField(max_length=100)
    y = models.CharField(max_length=100)
    z = models.CharField(max_length=100)

    aa = models.CharField(max_length=100)
    ab = models.CharField(max_length=100)
    ac = models.CharField(max_length=100)
    ad = models.CharField(max_length=100)
    ae = models.CharField(max_length=100)
    af = models.CharField(max_length=100)
    ag = models.CharField(max_length=100)
    ah = models.CharField(max_length=100)
    ai = models.CharField(max_length=100)
    aj = models.CharField(max_length=100)

    ak = models.CharField(max_length=100)
    al = models.CharField(max_length=100)
    am = models.CharField(max_length=100)
    an = models.CharField(max_length=100)
    ao = models.CharField(max_length=100)
    ap = models.CharField(max_length=100)
    aq = models.CharField(max_length=100)
    ar = models.CharField(max_length=100)
    a_s = models.CharField(max_length=100)
    at = models.CharField(max_length=100)

    au = models.CharField(max_length=100)
    av = models.CharField(max_length=100)
    aw = models.CharField(max_length=100)
    ax = models.CharField(max_length=100)
    ay = models.CharField(max_length=100)
    az = models.CharField(max_length=100)

    ba = models.CharField(max_length=100)
    bb = models.CharField(max_length=100)
    bc = models.CharField(max_length=100)
    bd = models.CharField(max_length=100)
    be = models.CharField(max_length=100)
    bf = models.CharField(max_length=100)
    bg = models.CharField(max_length=100)
    bh = models.CharField(max_length=100)
    bi = models.CharField(max_length=100)
    bj = models.CharField(max_length=100)

    bk = models.CharField(max_length=100)
    bl = models.CharField(max_length=100)
    bm = models.CharField(max_length=100)
    bn = models.CharField(max_length=100)
    bo = models.CharField(max_length=100)
    bp = models.CharField(max_length=100)
    bq = models.CharField(max_length=100)
    br = models.CharField(max_length=100)
    bs = models.CharField(max_length=100)
    bt = models.CharField(max_length=100)

    bu = models.CharField(max_length=100)
    bv = models.CharField(max_length=100)
    bw = models.CharField(max_length=100)
    bx = models.CharField(max_length=100)
    by = models.CharField(max_length=100)
    bz = models.CharField(max_length=100)

    ca = models.CharField(max_length=100)
    cb = models.CharField(max_length=100)
    cc = models.CharField(max_length=100)
    cd = models.CharField(max_length=100)
    ce = models.CharField(max_length=100)
    cf = models.CharField(max_length=100)
    cg = models.CharField(max_length=100)
    ch = models.CharField(max_length=100)
    ci = models.CharField(max_length=100)
    cj = models.CharField(max_length=100)

    ck = models.CharField(max_length=100)
    cl = models.CharField(max_length=100)
    cm = models.CharField(max_length=100)
    cn = models.CharField(max_length=100)
    co = models.CharField(max_length=100)
    cp = models.CharField(max_length=100)
    cq = models.CharField(max_length=100)
    cr = models.CharField(max_length=100)
    cs = models.CharField(max_length=100)
    ct = models.CharField(max_length=100)

    cu = models.CharField(max_length=100)
    cv = models.CharField(max_length=100)
    cw = models.CharField(max_length=100)
    cx = models.CharField(max_length=100)
    cy = models.CharField(max_length=100)
    cz = models.CharField(max_length=100)

    da = models.CharField(max_length=100)
    db = models.CharField(max_length=100)
    dc = models.CharField(max_length=100)
    dd = models.CharField(max_length=100)
    de = models.CharField(max_length=100)
    df = models.CharField(max_length=100)
    dg = models.CharField(max_length=100)
    dh = models.CharField(max_length=100)
    di = models.CharField(max_length=100)
    dj = models.CharField(max_length=100)

    dk = models.CharField(max_length=100)
    dl = models.CharField(max_length=100)


    status = models.CharField(max_length=100)



class TDTIH(models.Model):
    rig_id = models.CharField(max_length=11)
    well_id = models.CharField(max_length=11)
    act_id = models.CharField(max_length=11)

    a = models.CharField(max_length=100)
    b = models.CharField(max_length=100)
    c = models.CharField(max_length=100)
    d = models.CharField(max_length=100)
    e = models.CharField(max_length=100)
    f = models.CharField(max_length=100)
    g = models.CharField(max_length=100)
    h = models.CharField(max_length=100)
    i = models.CharField(max_length=100)
    j = models.CharField(max_length=100)

    k = models.CharField(max_length=100)
    l = models.CharField(max_length=100)
    m = models.CharField(max_length=100)
    n = models.CharField(max_length=100)
    o = models.CharField(max_length=100)
    p = models.CharField(max_length=100)
    q = models.CharField(max_length=100)
    r = models.CharField(max_length=100)
    s = models.CharField(max_length=100)
    t = models.CharField(max_length=100)

    u = models.CharField(max_length=100)
    v = models.CharField(max_length=100)
    w = models.CharField(max_length=100)
    x = models.CharField(max_length=100)
    y = models.CharField(max_length=100)
    z = models.CharField(max_length=100)

    aa = models.CharField(max_length=100)
    ab = models.CharField(max_length=100)
    ac = models.CharField(max_length=100)
    ad = models.CharField(max_length=100)
    ae = models.CharField(max_length=100)
    af = models.CharField(max_length=100)
    ag = models.CharField(max_length=100)
    ah = models.CharField(max_length=100)
    ai = models.CharField(max_length=100)
    aj = models.CharField(max_length=100)

    ak = models.CharField(max_length=100)
    al = models.CharField(max_length=100)
    am = models.CharField(max_length=100)
    an = models.CharField(max_length=100)
    ao = models.CharField(max_length=100)
    ap = models.CharField(max_length=100)
    aq = models.CharField(max_length=100)
    ar = models.CharField(max_length=100)
    a_s = models.CharField(max_length=100)
    at = models.CharField(max_length=100)

    au = models.CharField(max_length=100)

    status = models.CharField(max_length=100)



class TDDrlg(models.Model):
    rig_id = models.CharField(max_length=11)
    well_id = models.CharField(max_length=11)
    act_id = models.CharField(max_length=11)

    a = models.CharField(max_length=100)
    b = models.CharField(max_length=100)
    c = models.CharField(max_length=100)
    d = models.CharField(max_length=100)
    e = models.CharField(max_length=100)
    f = models.CharField(max_length=100)
    g = models.CharField(max_length=100)
    h = models.CharField(max_length=100)
    i = models.CharField(max_length=100)
    j = models.CharField(max_length=100)

    k = models.CharField(max_length=100)
    l = models.CharField(max_length=100)
    m = models.CharField(max_length=100)
    n = models.CharField(max_length=100)
    o = models.CharField(max_length=100)
    p = models.CharField(max_length=100)
    q = models.CharField(max_length=100)
    r = models.CharField(max_length=100)
    s = models.CharField(max_length=100)
    t = models.CharField(max_length=100)

    u = models.CharField(max_length=100)
    v = models.CharField(max_length=100)
    w = models.CharField(max_length=100)
    x = models.CharField(max_length=100)
    y = models.CharField(max_length=100)
    z = models.CharField(max_length=100)

    aa = models.CharField(max_length=100)
    ab = models.CharField(max_length=100)
    ac = models.CharField(max_length=100)
    ad = models.CharField(max_length=100)
    ae = models.CharField(max_length=100)
    af = models.CharField(max_length=100)
    ag = models.CharField(max_length=100)
    ah = models.CharField(max_length=100)
    ai = models.CharField(max_length=100)
    aj = models.CharField(max_length=100)

    ak = models.CharField(max_length=100)
    al = models.CharField(max_length=100)
    am = models.CharField(max_length=100)
    an = models.CharField(max_length=100)
    ao = models.CharField(max_length=100)
    ap = models.CharField(max_length=100)
    aq = models.CharField(max_length=100)
    ar = models.CharField(max_length=100)
    a_s = models.CharField(max_length=100)
    at = models.CharField(max_length=100)

    au = models.CharField(max_length=100)
    av = models.CharField(max_length=100)
    aw = models.CharField(max_length=100)
    ax = models.CharField(max_length=100)
    ay = models.CharField(max_length=100)
    az = models.CharField(max_length=100)

    ba = models.CharField(max_length=100)
    bb = models.CharField(max_length=100)
    bc = models.CharField(max_length=100)
    bd = models.CharField(max_length=100)
    be = models.CharField(max_length=100)
    bf = models.CharField(max_length=100)
    bg = models.CharField(max_length=100)
    bh = models.CharField(max_length=100)
    bi = models.CharField(max_length=100)
    bj = models.CharField(max_length=100)

    bk = models.CharField(max_length=100)
    bl = models.CharField(max_length=100)
    bm = models.CharField(max_length=100)
    bn = models.CharField(max_length=100)
    bo = models.CharField(max_length=100)
    bp = models.CharField(max_length=100)
    bq = models.CharField(max_length=100)
    br = models.CharField(max_length=100)
    bs = models.CharField(max_length=100)
    bt = models.CharField(max_length=100)

    bu = models.CharField(max_length=100)
    bv = models.CharField(max_length=100)
    bw = models.CharField(max_length=100)
    bx = models.CharField(max_length=100)
    by = models.CharField(max_length=100)
    bz = models.CharField(max_length=100)

    ca = models.CharField(max_length=100)

    status = models.CharField(max_length=100)



class TDPOH(models.Model):
    rig_id = models.CharField(max_length=11)
    well_id = models.CharField(max_length=11)
    act_id = models.CharField(max_length=11)

    a = models.CharField(max_length=100)
    b = models.CharField(max_length=100)
    c = models.CharField(max_length=100)
    d = models.CharField(max_length=100)
    e = models.CharField(max_length=100)
    f = models.CharField(max_length=100)
    g = models.CharField(max_length=100)
    h = models.CharField(max_length=100)
    i = models.CharField(max_length=100)
    j = models.CharField(max_length=100)

    k = models.CharField(max_length=100)
    l = models.CharField(max_length=100)
    m = models.CharField(max_length=100)
    n = models.CharField(max_length=100)
    o = models.CharField(max_length=100)
    p = models.CharField(max_length=100)
    q = models.CharField(max_length=100)
    r = models.CharField(max_length=100)
    s = models.CharField(max_length=100)
    t = models.CharField(max_length=100)

    u = models.CharField(max_length=100)
    v = models.CharField(max_length=100)
    w = models.CharField(max_length=100)
    x = models.CharField(max_length=100)
    y = models.CharField(max_length=100)
    z = models.CharField(max_length=100)

    aa = models.CharField(max_length=100)
    ab = models.CharField(max_length=100)
    ac = models.CharField(max_length=100)
    ad = models.CharField(max_length=100)
    ae = models.CharField(max_length=100)
    af = models.CharField(max_length=100)
    ag = models.CharField(max_length=100)
    ah = models.CharField(max_length=100)
    ai = models.CharField(max_length=100)
    aj = models.CharField(max_length=100)

    ak = models.CharField(max_length=100)
    al = models.CharField(max_length=100)
    am = models.CharField(max_length=100)
    an = models.CharField(max_length=100)
    ao = models.CharField(max_length=100)
    ap = models.CharField(max_length=100)
    aq = models.CharField(max_length=100)
    ar = models.CharField(max_length=100)
    a_s = models.CharField(max_length=100)
    at = models.CharField(max_length=100)

    au = models.CharField(max_length=100)

    status = models.CharField(max_length=100)






















