from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

class PsakNode(BaseModel):
    id: str
    source: str  # Torah, Mishnah, Talmud, Rambam, Shulchan Arukh, etc.
    text: str
    era: str
    year: int
    type: str  # source, interpretation, analysis, codification, final_ruling
    author: Optional[str] = None
    ref: Optional[str] = None

class PsakLineage(BaseModel):
    ruling_ref: str
    title: str
    chain: List[PsakNode]

# Sample psak lineage data
PSAK_DATA = {
    "OC_1:1": {
        "ruling_ref": "Shulchan Arukh, Orach Chaim 1:1",
        "title": "Time for Morning Shema",
        "chain": [
            {
                "id": "torah_1",
                "source": "Torah",
                "text": "וְדִבַּרְתָּ בָּם בְּשִׁבְתְּךָ בְּבֵיתֶךָ וּבְלֶכְתְּךָ בַדֶּרֶךְ וּבְשָׁכְבְּךָ וּבְקוּמֶךָ",
                "era": "Biblical",
                "year": -1200,
                "type": "source",
                "ref": "Deuteronomy 6:7"
            },
            {
                "id": "mishnah_1",
                "source": "Mishnah",
                "text": "מֵאֵימָתַי קוֹרִין אֶת שְׁמַע בְּעַרְבִית",
                "era": "Tannaitic",
                "year": 200,
                "type": "interpretation",
                "author": "Mishnah",
                "ref": "Berakhot 1:1"
            },
            {
                "id": "gemara_1",
                "source": "Talmud",
                "text": "עד חצות - discussion of when evening Shema must be recited",
                "era": "Amoraic",
                "year": 500,
                "type": "analysis",
                "author": "Talmud Bavli",
                "ref": "Berakhot 2a"
            },
            {
                "id": "rambam_1",
                "source": "Rambam",
                "text": "זְמַן קְרִיאַת שְׁמַע שֶׁל עַרְבִית מִצְּאֵת הַכּוֹכָבִים עַד חֲצוֹת הַלַּיְלָה",
                "era": "Rishonic",
                "year": 1180,
                "type": "codification",
                "author": "Maimonides",
                "ref": "Mishneh Torah, Kriat Shema 1:11"
            },
            {
                "id": "shulchan_arukh_1",
                "source": "Shulchan Arukh",
                "text": "יֵשׁ לוֹ לִקְרוֹת קְרִיאַת שְׁמַע מִתְּחִלַּת הַלַּיְלָה שֶׁהוּא מִשְּׁעַת צֵאת הַכּוֹכָבִים",
                "era": "Acharonic",
                "year": 1565,
                "type": "final_ruling",
                "author": "Rabbi Yosef Karo",
                "ref": "Orach Chaim 1:1"
            }
        ]
    }
}

@router.get("/psak/{ruling_ref}", response_model=PsakLineage)
def get_psak_lineage(ruling_ref: str):
    """
    Trace a halakhic ruling back through its sources.
    Returns the full chain from Torah -> Mishnah -> Gemara -> Rishonim -> Acharonim.
    """
    normalized_ref = ruling_ref.replace(" ", "_").replace(",", "").replace(":", "_")
    
    if normalized_ref in PSAK_DATA:
        return PSAK_DATA[normalized_ref]
    
    # Return a generic chain if specific one not found
    raise HTTPException(status_code=404, detail=f"Psak lineage not found for {ruling_ref}")

@router.get("/psak/search/")
def search_psak(query: str):
    """
    Search for halakhic rulings by keyword or topic.
    """
    results = []
    for key, value in PSAK_DATA.items():
        if query.lower() in value["title"].lower() or query.lower() in value["ruling_ref"].lower():
            results.append({
                "ref": value["ruling_ref"],
                "title": value["title"],
                "chain_length": len(value["chain"])
            })
    
    return {"query": query, "results": results}

