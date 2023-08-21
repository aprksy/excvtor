from datetime import date

def to_month_year(ym):
    if ym == "":
        return "present"
    d = ym.split("-")
    month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    return month[int(d[1])-1] + " " + d[0]

def to_duration(start, end):
    d1 = get_date(start)
    d2 = get_date(end)
    delta = d2 - d1
    ycount = int(delta.days / 365)
    dayRemainder = delta.days % 365
    mcount = int(dayRemainder / 30)
    dayRemainder = dayRemainder % 30
    if dayRemainder >= 15:
        mcount += 1
    ystr = ""
    mstr = ""
    if ycount == 1:
        ystr = "1 year"
    else:
        ystr = str(ycount) + " years"
    if mcount == 0:
        mstr = ""
    elif mcount == 1:
        mstr = "1 month"
    else:
        mstr = str(mcount) + " months"
    return ystr + " " + mstr

def get_date(value):
    d = value.split("-")
    if len(d) > 1:
        y, m = d[0], d[1]
        if y != "" and m != "":
            return date(int(y), int(m), 1)
    else:
        return date.today()