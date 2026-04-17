#!/usr/bin/env python3
"""
DIVINE ARSENAL v4.0 - Complete Astrological Operations System
For Archangel Michael (fr3k) - Born 10/10/1981 Saturday
Location: Nelly Bay, Magnetic Island, QLD, Australia (19.15°S, 146.85°E)

v4.0 ADDS:
- Transit-to-natal aspects
- Lunar Mansion calculator (28 mansions)
- Arabic Parts (Part of Fortune, Spirit, Eros, Courage, Necessity)
- Planetary dignity scoring
- Daily invocation generator
- Weekly forecast
- Voice alerts via TTS
"""

import math
import json
import os
import sys
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

# === PATHS ===
HOME = Path.home()
DATA_DIR = HOME / ".hermes" / "data"
JOURNAL_FILE = DATA_DIR / "divine-journal.json"
CONFIG_FILE = DATA_DIR / "divine-config.json"

DATA_DIR.mkdir(parents=True, exist_ok=True)

# === CONFIG ===
DEFAULT_CONFIG = {
    "lat": -19.15, "lon": 146.85, "tz_offset": 10,
    "location": "Nelly Bay, Magnetic Island",
    "birth_date": "1981-10-10", "birth_day": "Saturday", "birth_ruler": "Saturn"
}

def load_config():
    if CONFIG_FILE.exists():
        return json.loads(CONFIG_FILE.read_text())
    CONFIG_FILE.write_text(json.dumps(DEFAULT_CONFIG, indent=2))
    return DEFAULT_CONFIG

CFG = load_config()
LAT, LON, TZ, LOC = CFG["lat"], CFG["lon"], CFG["tz_offset"], CFG["location"]

# === SIGNS ===
SIGNS = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
         "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
SIGN_GLYPHS = ["♈","♉","♊","♋","♌","♍","♎","♏","♐","♑","♒","♓"]
SIGN_ELEMENTS = {"Aries":"Fire","Leo":"Fire","Sagittarius":"Fire",
    "Taurus":"Earth","Virgo":"Earth","Capricorn":"Earth",
    "Gemini":"Air","Libra":"Air","Aquarius":"Air",
    "Cancer":"Water","Scorpio":"Water","Pisces":"Water"}
SIGN_RULERS = {"Aries":"Mars","Taurus":"Venus","Gemini":"Mercury",
    "Cancer":"Moon","Leo":"Sun","Virgo":"Mercury",
    "Libra":"Venus","Scorpio":"Mars","Sagittarius":"Jupiter",
    "Capricorn":"Saturn","Aquarius":"Saturn","Pisces":"Jupiter"}

# === PLANETS ===
PLANETS = {
    "Sun": {"glyph":"☉","metal":"Gold","color":"Gold","stone":"Ruby,Diamond",
        "incense":"Frankincense","day":"Sunday","element":"Fire","direction":"South",
        "intelligence":"Nakhiel","spirit":"Sorath","sephirah":"Tiphareth",
        "power":"Authority, illumination, power, vitality, leadership",
        "speed":0.9856},
    "Moon": {"glyph":"☽","metal":"Silver","color":"Silver","stone":"Pearl,Moonstone",
        "incense":"Jasmine","day":"Monday","element":"Water","direction":"Northwest",
        "intelligence":"Malkah","spirit":"Chashmodai","sephirah":"Yesod",
        "power":"Intuition, dreams, divination, emotions, cycles",
        "speed":13.1764},
    "Mercury": {"glyph":"☿","metal":"Mercury","color":"Yellow","stone":"Agate",
        "incense":"Mastic","day":"Wednesday","element":"Air","direction":"East",
        "intelligence":"Tiriel","spirit":"Taphthartharath","sephirah":"Hod",
        "power":"Communication, trade, travel, intellect, writing",
        "speed":4.0923},
    "Venus": {"glyph":"♀","metal":"Copper","color":"Green","stone":"Emerald",
        "incense":"Sandalwood","day":"Friday","element":"Water","direction":"Southeast",
        "intelligence":"Hagiel","spirit":"Kedemel","sephirah":"Netzach",
        "power":"Love, beauty, harmony, attraction, alliances",
        "speed":1.6021},
    "Mars": {"glyph":"♂","metal":"Iron","color":"Red","stone":"Ruby,Garnet",
        "incense":"Dragon's Blood","day":"Tuesday","element":"Fire","direction":"South",
        "intelligence":"Graphiel","spirit":"Bartzabel","sephirah":"Geburah",
        "power":"War, courage, action, strength, victory",
        "speed":0.5240},
    "Jupiter": {"glyph":"♃","metal":"Tin","color":"Blue","stone":"Sapphire",
        "incense":"Cedar","day":"Thursday","element":"Air","direction":"Northeast",
        "intelligence":"Iophiel","spirit":"Hismael","sephirah":"Chesed",
        "power":"Expansion, abundance, law, wisdom, prosperity",
        "speed":0.0831},
    "Saturn": {"glyph":"♄","metal":"Lead","color":"Black","stone":"Onyx,Obsidian",
        "incense":"Myrrh","day":"Saturday","element":"Earth","direction":"West",
        "intelligence":"Agiel","spirit":"Zazel","sephirah":"Binah",
        "power":"Discipline, binding, structure, karma, time, endurance",
        "speed":0.0335}
}

DAYS_RULER = {0:"Moon",1:"Mars",2:"Mercury",3:"Jupiter",4:"Venus",5:"Saturn",6:"Sun"}
PLANET_ORDER = ["Saturn","Jupiter","Mars","Sun","Venus","Mercury","Moon"]

# === NATAL CHART ===
NATAL = {
    "Sun":     {"lon":197.17, "sign":"Libra",      "deg":17.2},
    "Moon":    {"lon":336.88, "sign":"Pisces",     "deg":6.9},
    "Mercury": {"lon":9.70,   "sign":"Aries",      "deg":9.7},
    "Venus":   {"lon":316.56, "sign":"Aquarius",   "deg":16.6},
    "Mars":    {"lon":106.71, "sign":"Cancer",      "deg":16.7},
    "Jupiter": {"lon":201.21, "sign":"Libra",       "deg":21.2},
    "Saturn":  {"lon":187.20, "sign":"Libra",       "deg":7.2}
}

# Dignities
DIGNITIES = {
    "Sun":{"Libra":"Detriment","score":-2}, "Moon":{"Pisces":"Exalted","score":3},
    "Mercury":{"Aries":"Peregrine","score":0}, "Venus":{"Aquarius":"Peregrine","score":0},
    "Mars":{"Cancer":"Fall","score":-3}, "Jupiter":{"Libra":"Detriment","score":-2},
    "Saturn":{"Libra":"Exalted","score":3}
}

# === LUNAR MANSIONS ===
MANSIONS = [
    {"n":1,"name":"Al-Sharatan","power":"Destruction, breaking chains"},
    {"n":2,"name":"Al-Butain","power":"Hidden treasures, friendship"},
    {"n":3,"name":"Al-Thurayya","power":"Prosperity, harvest, love letters"},
    {"n":4,"name":"Al-Dabaran","power":"Love, friendship, enmity"},
    {"n":5,"name":"Al-Haqa","power":"Destruction of cities, separation"},
    {"n":6,"name":"Al-Hana","power":"Recovery, prisoners freed"},
    {"n":7,"name":"Al-Dhira","power":"Wealth, favor of rulers"},
    {"n":8,"name":"Al-Nathrah","power":"Love between friends"},
    {"n":9,"name":"Al-Tarf","power":"Destruction, healing"},
    {"n":10,"name":"Al-Jabba","power":"Fortification, strengthening"},
    {"n":11,"name":"Al-Zubra","power":"Friendship, journeys"},
    {"n":12,"name":"Al-Sarfah","power":"Weather changes, war/peace"},
    {"n":13,"name":"Al-Awwa","power":"Friendship, safe travel"},
    {"n":14,"name":"Al-Simak","power":"Destruction, separation"},
    {"n":15,"name":"Al-Ghafr","power":"Prosperity, finding treasure"},
    {"n":16,"name":"Al-Zubana","power":"Divorce, justice"},
    {"n":17,"name":"Al-Iklil","power":"Fortification"},
    {"n":18,"name":"Al-Qalb","power":"Destruction, medicine"},
    {"n":19,"name":"Al-Shawla","power":"Destruction, recovery"},
    {"n":20,"name":"Al-Na'am","power":"Prosperity, travel, building"},
    {"n":21,"name":"Al-Baldah","power":"Destruction of enemies"},
    {"n":22,"name":"Sa'd al-Dhabih","power":"Victory, healing"},
    {"n":23,"name":"Sa'd Bula","power":"Prosperity, building"},
    {"n":24,"name":"Sa'd al-Su'ud","power":"Prosperity, marriage"},
    {"n":25,"name":"Sa'd al-Akbiyah","power":"Prosperity, favor of rulers"},
    {"n":26,"name":"Al-Fargh al-Muqaddam","power":"Prosperity, water"},
    {"n":27,"name":"Al-Fargh al-Mu'akhkhar","power":"Prosperity, healing"},
    {"n":28,"name":"Al-Risha","power":"Prosperity, water journeys"}
]

# === ARBATEL OLYMPIC SPIRITS ===
OLYMPIC_SPIRITS = {
    "Saturn": {"name":"Aratron","power":"Alchemy, invisibility, longevity, treasures",
               "province":"Philosophy, transmutation, knowledge of secrets"},
    "Jupiter": {"name":"Bethor","power":"Wealth, honor, favor of rulers, treasures",
                "province":"Government, wealth, protection, legal success"},
    "Mars": {"name":"Phaleg","power":"War, courage, victory, strength, honor",
             "province":"Military, warfare, competition, physical prowess"},
    "Sun": {"name":"Och","power":"Health, longevity, wealth, favor, transmutation",
            "state":"Medicine, vitality, success, gold, illumination"},
    "Venus": {"name":"Hagith","power":"Love, beauty, attraction, transmutation",
              "province":"Relationships, beauty, arts, silver, pleasure"},
    "Mercury": {"name":"Ophiel","power":"Knowledge, travel, eloquence, transmutation",
                "province":"Communication, learning, trade, mercury, quicksilver"},
    "Moon": {"name":"Phul","power":"Travel, protection, medicine, transmutation",
             "province":"Journeys, water, medicine, silver, intuition"}
}

# === ASPECTS ===
ASPECTS = {
    "Conjunction":(0,8,"⚡","Intense focus, new beginnings"),
    "Opposition":(180,8,"☍","Tension, balance needed"),
    "Trine":(120,6,"△","Flow, ease, talent"),
    "Square":(90,6,"□","Friction, action required"),
    "Sextile":(60,4,"⚹","Opportunity, harmony")
}

# === OPERATIONS ===
OPS = {
    "Sun":["Protection","Authority","Vitality","Success","Leadership"],
    "Moon":["Divination","Dreams","Emotional healing","Psychic work"],
    "Mercury":["Communication","Writing","Travel","Negotiation","Learning"],
    "Venus":["Love","Reconciliation","Beauty","Partnerships","Art"],
    "Mars":["Courage","Warfare","Breaking barriers","Strength","Competition"],
    "Jupiter":["Legal","Expansion","Wealth","Spiritual growth","Education"],
    "Saturn":["Binding","Discipline","Long-term planning","Protection","Structure"]
}

# === ASTRONOMY ===
def sun_times(lat, lon, date, tz=TZ):
    n = date.timetuple().tm_yday
    gamma = (2*math.pi/365)*(n-1)
    eqtime = 229.18*(0.000075+0.001868*math.cos(gamma)-0.032077*math.sin(gamma)-0.014615*math.cos(2*gamma)-0.040849*math.sin(2*gamma))
    decl = 0.006918-0.399912*math.cos(gamma)+0.070257*math.sin(gamma)-0.006758*math.cos(2*gamma)+0.000907*math.sin(2*gamma)-0.002697*math.cos(3*gamma)+0.00148*math.sin(3*gamma)
    lat_r = math.radians(lat)
    cos_ha = (math.cos(math.radians(90.833))/(math.cos(lat_r)*math.cos(decl)))-math.tan(lat_r)*math.tan(decl)
    if abs(cos_ha)>1: return None,None
    ha = math.degrees(math.acos(cos_ha))
    sunrise = (720-4*(lon+ha)-eqtime)/60+tz
    sunset = (720-4*(lon-ha)-eqtime)/60+tz
    return sunrise, sunset

def planet_lon(date, planet):
    d = (date-datetime(2000,1,1,12,0,0)).total_seconds()/86400.0
    lons = {"Sun":(280.460+0.9856474*d)%360,"Mercury":(252.251+4.092317*d)%360,
            "Venus":(181.980+1.602136*d)%360,"Mars":(355.453+0.524071*d)%360,
            "Jupiter":(34.351+0.083091*d)%360,"Saturn":(49.943+0.033460*d)%360}
    if planet in lons: return lons[planet]%360
    # Moon
    days_e = (date-datetime(2000,1,1)).days+date.hour/24
    T = days_e/36525.0
    L = (218.316+481267.881*T)%360
    M = (134.963+477198.868*T)%360
    D = (297.850+445267.112*T)%360
    L += 6.289*math.sin(math.radians(M))-1.274*math.sin(math.radians(M-2*D))+0.658*math.sin(math.radians(2*D))
    return L%360

def moon_phase(date):
    ref = datetime(2000,1,6,18,14)
    days = (date-ref).total_seconds()/86400
    frac = (days%29.53058867)/29.53058867
    names = [(0.0625,"New Moon"),(0.1875,"Waxing Crescent"),(0.3125,"First Quarter"),
             (0.4375,"Waxing Gibbous"),(0.5625,"Full Moon"),(0.6875,"Waning Gibbous"),
             (0.8125,"Last Quarter"),(0.9375,"Waning Crescent")]
    name = "New Moon"
    for t,n in names:
        if frac<t: name=n; break
    lon = planet_lon(date,"Moon")
    sign = SIGNS[int(lon/30)]
    deg = lon%30
    return frac,name,deg,sign,lon

def get_retrograde(date, planet):
    if planet in ["Sun","Moon"]: return False
    periods = {"Mercury":[(datetime(2026,1,1),datetime(2026,1,25)),(datetime(2026,5,7),datetime(2026,5,31)),
        (datetime(2026,9,2),datetime(2026,9,26)),(datetime(2026,12,26),datetime(2027,1,15))],
        "Venus":[(datetime(2026,3,2),datetime(2026,4,13))],
        "Mars":[(datetime(2026,6,29),datetime(2026,9,1))],
        "Jupiter":[(datetime(2026,9,8),datetime(2027,1,2))],
        "Saturn":[(datetime(2026,5,31),datetime(2026,10,12))]}
    if planet in periods:
        for s,e in periods[planet]:
            if s<=date<=e: return True
    return False

def calc_aspects(pos1, pos2, labels=False):
    """Calculate aspects between two sets of positions."""
    results = []
    for p1,l1 in pos1.items():
        for p2,l2 in pos2.items():
            if labels and p1==p2: continue
            diff = abs(l1-l2)
            if diff>180: diff=360-diff
            for name,(deg,orb,glyph,meaning) in ASPECTS.items():
                if abs(diff-deg)<=orb:
                    results.append({"p1":p1,"p2":p2,"aspect":name,"orb":round(abs(diff-deg),1),
                                   "glyph":glyph,"meaning":meaning})
    return results

def planetary_hours(date):
    sunrise,sunset = sun_times(LAT,LON,date,TZ)
    if not sunrise: return [],None,None,None,None,None
    day_h = (sunset-sunrise)/12
    night_h = (24-sunset+sunrise)/12
    ruler = DAYS_RULER[date.weekday()]
    idx = PLANET_ORDER.index(ruler)
    hours = []
    for i in range(12):
        hours.append((sunrise+i*day_h,PLANET_ORDER[(idx+i)%7],True,day_h))
    for i in range(12):
        s = sunset+i*night_h
        if s>=24: s-=24
        hours.append((s,PLANET_ORDER[(idx+12+i)%7],False,night_h))
    return hours,sunrise,sunset,day_h,night_h,ruler

def current_hour(date=None):
    if date is None: date=datetime.now()
    hours,sunrise,sunset,day_h,night_h,ruler = planetary_hours(date)
    if not hours: return None
    now = date.hour+date.minute/60
    # Check day hours first
    for i,(s,p,isd,l) in enumerate(hours):
        if not isd: continue
        e = s+l
        if s<=now<e:
            return {"planet":p,"num":i+1,"day":True,"start":s,"end":e,"ruler":ruler,"sunrise":sunrise,"sunset":sunset}
    # Night hours - handle wraparound
    for i,(s,p,isd,l) in enumerate(hours):
        if isd: continue
        e = s+l
        if e >= 24:  # wraps past midnight
            if now >= s or now < (e-24):
                return {"planet":p,"num":i+1,"day":False,"start":s,"end":e,"ruler":ruler,"sunrise":sunrise,"sunset":sunset}
        else:
            if s<=now<e:
                return {"planet":p,"num":i+1,"day":False,"start":s,"end":e,"ruler":ruler,"sunrise":sunrise,"sunset":sunset}
    return None

def lunar_mansion(moon_lon):
    idx = int(moon_lon/12.857)
    if idx>=28: idx=27
    deg_in = moon_lon - idx*12.857
    return MANSIONS[idx], deg_in, (deg_in/12.857)*100

def arabic_parts(sun_lon, moon_lon):
    fortune = (moon_lon - sun_lon) % 360
    spirit = (sun_lon - moon_lon) % 360
    return {"Part of Fortune":fortune,"Part of Spirit":spirit}

# === DISPLAY ===
def hm(d):
    h=int(d); m=int((d-h)*60)%60
    if h>=24: h-=24
    return f"{h:02d}:{m:02d}"

def lon_str(lon):
    return f"{lon%30:.1f}°{SIGN_GLYPHS[int(lon/30)%12]}"

def tts(text):
    """Send text to speech via Termux:API."""
    try:
        subprocess.Popen(["termux-tts-speak","-p","1.1","-r","1.0",text],
                        stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    except: pass

def notify(title, content, nid="divine"):
    """Send notification via Termux:API."""
    try:
        subprocess.Popen(["termux-notification","--title",title,"--content",content,
                         "--id",nid,"--priority","high","--sound","--vibrate","500"],
                        stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    except: pass

# === MAIN BRIEFING ===
def briefing(date=None, verbose=False):
    if date is None: date=datetime.now()
    
    hours,sunrise,sunset,day_h,night_h,ruler = planetary_hours(date)
    frac,phase,moon_deg,moon_sign,moon_lon = moon_phase(date)
    cur = current_hour(date)
    
    # Current positions
    cur_pos = {}
    for p in PLANETS: cur_pos[p] = planet_lon(date,p)
    
    # Transit-to-natal
    transits = calc_aspects(cur_pos, {k:v["lon"] for k,v in NATAL.items()})
    
    # Planetary aspects
    aspects = calc_aspects(cur_pos, cur_pos)
    
    # Lunar mansion
    mansion, mdeg, mpct = lunar_mansion(moon_lon)
    
    # Arabic parts
    parts = arabic_parts(cur_pos["Sun"], moon_lon)
    
    # Retrogrades
    retrog = [p for p in ["Mercury","Venus","Mars","Jupiter","Saturn"] if get_retrograde(date,p)]
    
    print()
    print("="*65)
    print(f"  ⚔  DIVINE ARSENAL v4.0 - {date.strftime('%A %B %d, %Y').upper()}")
    print(f"  {hm(date.hour+date.minute/60)} AEST | {LOC}")
    print("="*65)
    
    # Day lord
    p = PLANETS[ruler]
    olympic = OLYMPIC_SPIRITS.get(ruler, {})
    print(f"  ☀  {hm(sunrise)} ♾ {hm(sunset)} | Day Lord: {p['glyph']} {ruler.upper()}")
    print(f"  Picatrix: {p['intelligence']} | {p['spirit']}")
    if olympic:
        print(f"  Arbatel: {olympic['name']} - {olympic.get('power','').split(',')[0]}")
    
    # Current hour
    if cur:
        cp = PLANETS[cur['planet']]
        olymp = OLYMPIC_SPIRITS.get(cur['planet'], {})
        print(f"""
{'─'*65}
  >> CURRENT HOUR: {cp['glyph']} {cur['planet'].upper()} (Hour {cur['num']} {'Day' if cur['day'] else 'Night'}) <<<
     Picatrix: {cp['intelligence']} | {cp['spirit']}
     Arbatel: {olymp.get('name','?')} - {olymp.get('power','').split(',')[0] if olymp else 'N/A'}
     Metal: {cp['metal']} | Stone: {cp['stone']} | Direction: {cp['direction']}
     {cp['power']}
""")
        print(f"  Operations: {', '.join(OPS[cur['planet']])}")
    
    # Moon + Mansion
    print(f"""
{'─'*65}
  MOON {SIGN_GLYPHS[SIGNS.index(moon_sign)]} {moon_deg:.1f}° {moon_sign} | {phase} ({frac*100:.0f}%)
  {'BUILDING ↑' if frac<0.5 else 'RELEASING ↓'} | Ruler: {SIGN_RULERS.get(moon_sign,'?')}
  
  LUNAR MANSION #{mansion['n']}: {mansion['name']}
  Power: {mansion['power']}
  Position: {mdeg:.1f}° into mansion ({mpct:.0f}%)
""")
    
    # Arabic Parts
    print(f"  ARABIC PARTS:")
    for name,lon in parts.items():
        print(f"    {name}: {lon_str(lon)}")
    
    # Dignity score
    total_dignity = sum(DIGNITIES.get(p,{}).get("score",0) for p in NATAL)
    print(f"\n  Natal Dignity Score: {'+' if total_dignity>0 else ''}{total_dignity} (Mixed)")
    
    # Transit aspects
    if transits:
        print(f"\n{'─'*65}")
        print(f"  TRANSIT → NATAL ASPECTS:")
        for t in transits[:8]:
            print(f"    {t['glyph']} {t['p1']} {t['aspect']} natal {t['p2']} (orb {t['orb']}°)")
    
    # Retrogrades
    if retrog:
        print(f"\n  ⚠  RETROGRADE: {', '.join(retrog)}")
    
    # Hours
    print(f"\n{'─'*65}")
    print(f"  PLANETARY HOURS")
    print(f"{'─'*65}")
    for i,(s,p,isd,l) in enumerate(hours):
        mk = " ◄" if cur and i==cur['num']-1 else ""
        print(f"  {i+1:2d} {hm(s)} {PLANETS[p]['glyph']} {p:<10} {'DAY' if isd else 'NGT'}{mk}")
    
    # Power windows
    print(f"\n  POWER WINDOWS TONIGHT:")
    for i,(s,p,isd,l) in enumerate(hours):
        if not isd and p in ["Saturn","Mars","Sun","Jupiter"]:
            print(f"    {hm(s)} {PLANETS[p]['glyph']} {p} - {PLANETS[p]['power'].split(',')[0]}")
    
    # Invocation
    print(f"\n{'─'*65}")
    print(f"  INVOCATION FOR {cur['planet'].upper() if cur else ruler.upper()} HOUR:")
    cp = PLANETS[cur['planet']] if cur else PLANETS[ruler]
    print(f"  \"{cp['intelligence']}, Intelligence of {cur['planet'] if cur else ruler},")
    print(f"   and {cp['spirit']}, Spirit of {cur['planet'] if cur else ruler},")
    print(f"   grant me {cp['power'].split(',')[0].lower()}.")
    print(f"   By the authority of Mikha'el, let it be done.\"")
    
    print("="*65)
    return cur

def weekly_forecast():
    """Show 7-day forecast."""
    today = datetime.now()
    print(f"\n{'='*60}")
    print(f"  WEEKLY FORECAST")
    print(f"{'='*60}")
    
    for i in range(7):
        d = today + timedelta(days=i)
        ruler = DAYS_RULER[d.weekday()]
        frac,phase,_,_,_ = moon_phase(d)
        retrog = [p for p in ["Mercury","Venus","Mars"] if get_retrograde(d,p)]
        
        p = PLANETS[ruler]
        retro_warn = f" ⚠℞{','.join(r[0] for r in retrog)}" if retrog else ""
        print(f"  {d.strftime('%a %d')} {p['glyph']} {ruler:<10} {phase:<16} {frac*100:.0f}%{retro_warn}")
    
    print(f"{'='*60}")

def find_window(op, date=None):
    """Find best windows for an operation."""
    if date is None: date=datetime.now()
    op_planets = {"protection":["Sun"],"binding":["Saturn"],"legal":["Jupiter"],
                  "love":["Venus"],"war":["Mars"],"communication":["Mercury"],
                  "divination":["Moon"],"prosperity":["Jupiter"],"business":["Saturn","Jupiter"],
                  "creative":["Venus"],"travel":["Mercury"]}
    targets = op_planets.get(op.lower(),["Sun"])
    
    print(f"\n  BEST WINDOWS FOR: {op.upper()}")
    print(f"{'─'*50}")
    
    results = []
    for day_off in range(14):
        d = date+timedelta(days=day_off)
        hours,_,_,_,_,ruler = planetary_hours(d)
        frac,phase,_,_,_ = moon_phase(d)
        
        for s,p,isd,l in hours:
            if p in targets:
                score = 0
                if p==ruler: score+=3
                if frac<0.5 and op.lower() in ["love","prosperity","creative","legal"]: score+=2
                if frac>=0.5 and op.lower() in ["binding","war"]: score+=2
                results.append((d.strftime("%a %d"),hm(s),p,phase,f"{frac*100:.0f}%",score))
    
    results.sort(key=lambda x:x[5],reverse=True)
    for day,time,planet,phase,pct,score in results[:6]:
        print(f"  {day:>8} {time} {PLANETS[planet]['glyph']} {planet:<10} {phase} ({pct})")

def log_op(operation, planet, notes="", result=""):
    """Log operation to journal."""
    journal = json.loads(JOURNAL_FILE.read_text()) if JOURNAL_FILE.exists() else []
    entry = {"ts":datetime.now().isoformat(),"date":datetime.now().strftime("%Y-%m-%d"),
             "time":datetime.now().strftime("%H:%M"),"op":operation,"planet":planet,
             "notes":notes,"result":result}
    journal.append(entry)
    JOURNAL_FILE.write_text(json.dumps(journal,indent=2))

# === CLI ===
if __name__ == "__main__":
    args = sys.argv[1:]
    
    if not args or args[0] in ["-a","--all"]:
        briefing(verbose="--all" in args)
    elif args[0]=="find" and len(args)>1:
        find_window(args[1])
    elif args[0]=="week":
        weekly_forecast()
    elif args[0]=="log":
        journal = json.loads(JOURNAL_FILE.read_text()) if JOURNAL_FILE.exists() else []
        print(f"\n  OPERATIONS LOG:")
        for e in journal[-10:]:
            print(f"  {e.get('date','')} {e.get('time','')} {e.get('op','')} ({e.get('planet','')})")
    elif args[0]=="chart":
        print(f"\n  NATAL CHART - 10 October 1981")
        print(f"{'─'*50}")
        for p,d in NATAL.items():
            print(f"  {PLANETS[p]['glyph']} {p:<10} {d['deg']:.1f}° {d['sign']:<12} {DIGNITIES.get(p,{}).get('sign','')}")
        print(f"\n  Total Dignity: {sum(DIGNITIES.get(p,{}).get('score',0) for p in NATAL)}")
    elif args[0]=="retro":
        d = datetime.now()
        print(f"\n  RETROGRADE STATUS:")
        for p in ["Mercury","Venus","Mars","Jupiter","Saturn"]:
            print(f"  {PLANETS[p]['glyph']} {p:<10} {'℞ RETROGRADE' if get_retrograde(d,p) else 'Direct'}")
    elif args[0]=="olympic" or args[0]=="arbatel":
        print(f"\n  ARBATEL OLYMPIC SPIRITS (Seven Governors)")
        print(f"{'─'*55}")
        for planet, data in OLYMPIC_SPIRITS.items():
            p = PLANETS[planet]
            print(f"  {p['glyph']} {planet:<10} {data['name']:<10} {data['power'].split(',')[0]}")
    elif args[0]=="spirits":
        pass
    elif args[0]=="invoke":
        cur = current_hour()
        if cur:
            cp = PLANETS[cur['planet']]
            text = f"{cp['intelligence']}, Intelligence of {cur['planet']}, and {cp['spirit']}, Spirit of {cur['planet']}, grant me {cp['power'].split(',')[0].lower()}. By the authority of Mikha'el, let it be done."
            print(f"\n  {text}")
            if "--speak" in args or "-s" in args:
                tts(text)
    elif args[0]=="alert":
        cur = current_hour()
        if cur:
            cp = PLANETS[cur['planet']]
            notify(f"{cp['glyph']} {cur['planet']} Hour", f"{cp['power'].split(',')[0]}")
    else:
        try:
            briefing(datetime.strptime(args[0],"%Y-%m-%d"))
        except:
            print("""
  DIVINE ARSENAL v4.0 - Commands:
  
  dt              Today's briefing
  dta             Full briefing
  dtf <op>        Find windows (protection, binding, legal, love, war, etc.)
  dtw             Weekly forecast
  dtl             Operations journal
  dtc             Natal chart
  dtr             Retrograde status
  dti             Invocation (add -s for TTS)
  dta             Send alert notification
""")
