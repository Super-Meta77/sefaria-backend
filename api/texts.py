from fastapi import APIRouter, HTTPException
from models import Text
import requests

router = APIRouter()

@router.get("/texts/{ref}", response_model=Text)
def get_text(ref: str, lang: str = "he"):
    try:
        # Demo: fetch from Sefaria public API if available
        sefaria_url = f"https://www.sefaria.org/api/texts/{ref}?lang={lang}"
        resp = requests.get(sefaria_url)
        if resp.status_code == 200:
            j = resp.json()
            content = j.get("he") if lang == "he" else j.get("text", "")
            content = "\n".join(content) if isinstance(content, list) else str(content)
            return Text(ref=ref, lang=lang, content=content, versions=[j.get("versionTitle","")])
        else:
            raise HTTPException(status_code=404, detail="Not found via Sefaria API")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
