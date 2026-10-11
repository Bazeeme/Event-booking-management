import os, re, jwt
from functools import wraps
from decimal import Decimal
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from db import connect, wait_db

load_dotenv()
app=Flask(__name__)
CORS(app)
SECRET=os.getenv("JWT_SECRET_KEY","local-only-change-me")

def clean(row):
    if row is None: return None
    return {k:(float(v) if isinstance(v,Decimal) else v.isoformat() if hasattr(v,"isoformat") else v) for k,v in dict(row).items()}
def query(sql, params=(), many=False, commit=False):
    with connect() as c:
        with c.cursor() as cur:
            cur.execute(sql,params)
            result=cur.fetchall() if many else (cur.fetchone() if cur.description else None)
        if commit: c.commit()
        if many: return [clean(x) for x in result]
        return clean(result) if result else None
def token(uid,email,admin=False):
    return jwt.encode({"user_id":uid,"email":email,"is_admin":admin},SECRET,algorithm="HS256")
def auth(admin=False):
    def deco(fn):
        @wraps(fn)
        def wrapped(*a,**kw):
            h=request.headers.get("Authorization","")
            if not h.startswith("Bearer "): return jsonify(error="Please log in"),401
            try: data=jwt.decode(h[7:],SECRET,algorithms=["HS256"])
            except jwt.InvalidTokenError: return jsonify(error="Invalid token"),401
            if admin and not data.get("is_admin"): return jsonify(error="Admin access required"),403
            request.identity=data
            return fn(*a,**kw)
        return wrapped
    return deco

@app.get("/api/health")
def health():
    try: query("SELECT 1 AS ok"); return jsonify(status="ok",database="connected")
    except Exception: return jsonify(status="error",database="unavailable"),503

@app.post("/api/register")
def register():
    d=request.get_json(silent=True) or {}; name=str(d.get("name","")).strip(); email=str(d.get("email","")).strip().lower(); pw=str(d.get("password",""))
    if not name or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+",email) or len(pw)<8:
        return jsonify(error="Enter name, valid email, and password of at least 8 characters"),400
    try:
        u=query("INSERT INTO users(name,email,password_hash) VALUES(%s,%s,%s) RETURNING id,name,email",(name,email,generate_password_hash(pw)),commit=True)
        return jsonify(message="Registered successfully",user=u),201
    except Exception as e:
        if "duplicate key" in str(e).lower(): return jsonify(error="Email already registered"),409
        app.logger.exception("Registration error"); return jsonify(error="Registration failed"),500

@app.post("/api/login")
def login():
    d=request.get_json(silent=True) or {}; email=str(d.get("email","")).strip().lower(); pw=str(d.get("password",""))
    if email==os.getenv("ADMIN_EMAIL","admin@gmail.com").lower() and pw==os.getenv("ADMIN_PASSWORD","admin123"):
        return jsonify(token=token(0,email,True),user={"id":0,"name":"Admin","email":email,"is_admin":True})
    u=query("SELECT id,name,email,password_hash FROM users WHERE email=%s",(email,))
    if not u or not check_password_hash(u["password_hash"],pw): return jsonify(error="Invalid email or password"),401
    return jsonify(token=token(u["id"],u["email"]),user={"id":u["id"],"name":u["name"],"email":u["email"],"is_admin":False})

@app.get("/api/events")
def events():
    return jsonify(query("SELECT id,title,description,venue,event_date,price FROM events ORDER BY event_date",many=True))

@app.post("/api/bookings")
@auth()
def create_booking():
    if request.identity.get("is_admin"): return jsonify(error="Admin cannot book tickets"),403
    d=request.get_json(silent=True) or {}
    try: age=int(d.get("age",0)); eid=int(d.get("event_id",0))
    except (TypeError,ValueError): return jsonify(error="Age and event are required"),400
    name=str(d.get("attendee_name","")).strip(); email=str(d.get("email","")).strip().lower(); phone=str(d.get("phone","")).strip(); slot=str(d.get("slot","")).strip()
    if not name or not (1<=age<=120) or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+",email) or not re.fullmatch(r"[0-9+() .-]{7,20}",phone) or slot not in ("Morning","Afternoon","Evening"):
        return jsonify(error="Check all booking details and choose a valid slot"),400
    if not query("SELECT id FROM events WHERE id=%s",(eid,)): return jsonify(error="Event not found"),404
    b=query("INSERT INTO bookings(user_id,event_id,attendee_name,age,email,phone,slot) VALUES(%s,%s,%s,%s,%s,%s,%s) RETURNING id,event_id,attendee_name,age,email,phone,slot,booked_at",(request.identity["user_id"],eid,name,age,email,phone,slot),commit=True)
    return jsonify(message="Ticket booked",booking=b),201

@app.get("/api/my-bookings")
@auth()
def my_bookings():
    if request.identity.get("is_admin"): return jsonify([])
    return jsonify(query("SELECT b.id,b.attendee_name,b.age,b.email,b.phone,b.slot,b.booked_at,e.title AS event_name,e.venue,e.event_date FROM bookings b JOIN events e ON e.id=b.event_id WHERE b.user_id=%s ORDER BY b.booked_at DESC",(request.identity["user_id"],),many=True))

@app.get("/api/admin/bookings")
@auth(admin=True)
def all_bookings():
    return jsonify(query("SELECT b.id,b.attendee_name,b.age,b.email,b.phone,b.slot,b.booked_at,e.title AS event_name,u.name AS account_name FROM bookings b JOIN events e ON e.id=b.event_id JOIN users u ON u.id=b.user_id ORDER BY b.booked_at DESC",many=True))

@app.get("/api/admin/stats")
@auth(admin=True)
def stats():
    by_event=query("SELECT e.title AS event_name,COUNT(b.id)::int AS bookings FROM events e LEFT JOIN bookings b ON b.event_id=e.id GROUP BY e.id,e.title ORDER BY bookings DESC,e.title",many=True)
    by_slot=query("SELECT slot,COUNT(*)::int AS bookings FROM bookings GROUP BY slot ORDER BY bookings DESC",many=True)
    totals=query("SELECT COUNT(*)::int AS total_bookings,COUNT(DISTINCT user_id)::int AS unique_users FROM bookings")
    return jsonify(by_event=by_event,by_slot=by_slot,totals=totals)

if __name__=="__main__":
    wait_db()
    app.run(host="0.0.0.0",port=5000,debug=os.getenv("FLASK_DEBUG","0")=="1")
