from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, date

router = APIRouter()

class CalendarItem(BaseModel):
    type: str  # daf_yomi, parsha, haftara, rambam, fast, holiday
    title: str
    ref: str
    description: Optional[str] = None
    url: Optional[str] = None

class DaySchedule(BaseModel):
    date: str
    jewish_date: str
    items: List[CalendarItem]

# Sample calendar mappings (in production, use Hebrew calendar library)
CALENDAR_DATA = {
    "2024-01-01": {
        "date": "2024-01-01",
        "jewish_date": "19 Tevet 5784",
        "items": [
            {
                "type": "daf_yomi",
                "title": "Daf Yomi",
                "ref": "Bava Kamma 14a",
                "description": "Today's Talmud page in the Daf Yomi cycle",
                "url": "/texts/Talmud/Bava_Kamma/14a"
            },
            {
                "type": "rambam",
                "title": "Daily Rambam",
                "ref": "Mishneh Torah, Hilchot Shabbat 1-3",
                "description": "Three chapters per day cycle",
                "url": "/texts/Rambam/Shabbat/1-3"
            }
        ]
    },
    "2024-12-25": {
        "date": "2024-12-25",
        "jewish_date": "24 Kislev 5785",
        "items": [
            {
                "type": "holiday",
                "title": "Chanukah - Day 1",
                "ref": "Numbers 7:12-17",
                "description": "Torah reading for first day of Chanukah",
                "url": "/texts/Torah/Numbers/7"
            },
            {
                "type": "daf_yomi",
                "title": "Daf Yomi",
                "ref": "Bava Batra 45b",
                "description": "Today's Talmud page",
                "url": "/texts/Talmud/Bava_Batra/45b"
            }
        ]
    }
}

def get_parsha_for_date(date_str: str) -> Optional[str]:
    """Get Torah portion for a given date (simplified)."""
    # In production, use proper Hebrew calendar library
    parshiyot = ["Bereshit", "Noach", "Lech Lecha", "Vayera", "Chayei Sarah"]
    # Simplified logic - would use real calendar in production
    return parshiyot[0]

@router.get("/calendar/{date_str}", response_model=DaySchedule)
def get_calendar_for_date(date_str: str):
    """
    Get all relevant Torah texts and learning for a specific date.
    Includes: Daf Yomi, Parsha, Haftara, daily Rambam, holidays, fast days, etc.
    """
    # Check if we have data for this specific date
    if date_str in CALENDAR_DATA:
        return CALENDAR_DATA[date_str]
    
    # Generate dynamic data for dates not in cache
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    # Generate dynamic schedule
    items = [
        {
            "type": "daf_yomi",
            "title": "Daf Yomi",
            "ref": "Berakhot 2a",  # Would calculate actual daf
            "description": "Today's Talmud page in the Daf Yomi cycle"
        },
        {
            "type": "rambam",
            "title": "Daily Rambam",
            "ref": "Mishneh Torah, De'ot 1-3",
            "description": "Three chapters per day"
        }
    ]
    
    # Add parsha if it's Shabbat (Saturday)
    if date_obj.weekday() == 5:  # Saturday
        parsha = get_parsha_for_date(date_str)
        items.append({
            "type": "parsha",
            "title": f"Parashat {parsha}",
            "ref": f"Torah/{parsha}",
            "description": "Weekly Torah portion"
        })
    
    return {
        "date": date_str,
        "jewish_date": "Hebrew date calculation needed",  # Would use proper library
        "items": items
    }

@router.get("/calendar/today/", response_model=DaySchedule)
def get_todays_calendar():
    """Get today's learning schedule and relevant texts."""
    today = date.today().strftime("%Y-%m-%d")
    return get_calendar_for_date(today)

@router.get("/calendar/range/")
def get_calendar_range(start_date: str, end_date: str):
    """Get calendar data for a date range."""
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    if (end - start).days > 365:
        raise HTTPException(status_code=400, detail="Date range too large (max 365 days)")
    
    # Generate data for each day
    results = []
    current = start
    while current <= end:
        date_str = current.strftime("%Y-%m-%d")
        try:
            day_data = get_calendar_for_date(date_str)
            results.append(day_data)
        except:
            pass
        current = current.replace(day=current.day + 1)
    
    return {"range": {"start": start_date, "end": end_date}, "days": results}

@router.get("/calendar/cycle/{cycle_type}")
def get_cycle_info(cycle_type: str):
    """
    Get information about a learning cycle.
    Types: daf_yomi, mishna_yomit, rambam_daily, etc.
    """
    cycles = {
        "daf_yomi": {
            "name": "Daf Yomi",
            "description": "Daily page of Talmud, completing Shas in ~7.5 years",
            "duration_days": 2711,
            "current_cycle_start": "2020-01-05",
            "current_cycle_end": "2027-06-09"
        },
        "rambam_daily": {
            "name": "Daily Rambam",
            "description": "3 chapters per day, completing Mishneh Torah in ~1 year",
            "duration_days": 365,
            "current_cycle_start": "2024-01-01"
        }
    }
    
    if cycle_type in cycles:
        return cycles[cycle_type]
    
    raise HTTPException(status_code=404, detail=f"Cycle type '{cycle_type}' not found")

