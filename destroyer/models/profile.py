"""
Target Reconnaissance Profile Model
===================================
Data structure and serialization model for target demographic, associate,
and organizational parameters collected during security assessments.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List


def parse_date_components(date_str: str) -> Dict[str, str]:
    """
    Parse date representation into constituent substrings.
    Supports DDMMYYYY, YYYYMMDD, delimited dates (DD-MM-YYYY, YYYY-MM-DD),
    and 4-digit years.

    Args:
        date_str: Raw calendar date string.

    Returns:
        Dictionary mapping component keys to numeric strings.
    """
    clean = re.sub(r"[^\d]", "", date_str.strip())
    components: Dict[str, str] = {}

    if len(clean) == 8:
        if 1900 < int(clean[:4]) < 2035:
            yyyy = clean[:4]
            mm = clean[4:6]
            dd = clean[6:8]
        else:
            dd = clean[:2]
            mm = clean[2:4]
            yyyy = clean[4:]

        yy = yyyy[-2:]
        components["yyyy"] = yyyy
        components["yy"] = yy
        components["dd"] = dd
        components["mm"] = mm
        components["ddmm"] = dd + mm
        components["mmdd"] = mm + dd
        components["ddmmyyyy"] = dd + mm + yyyy
        components["yyyymmdd"] = yyyy + mm + dd
        components["ddmmyy"] = dd + mm + yy
    elif len(clean) == 4:
        components["yyyy"] = clean
        components["yy"] = clean[-2:]

    return components


class TargetProfile:
    """
    Target reconnaissance profile container.
    Stores normalized lowercased tokens and extracted numeric components.
    """

    def __init__(self) -> None:
        self.name: str = ""
        self.surname: str = ""
        self.nick: str = ""
        self.handles: List[str] = []
        self.email: str = ""
        self.birthdate: str = ""
        self.birth_components: Dict[str, str] = {}

        # Relations
        self.partner_name: str = ""
        self.partner_nick: str = ""
        self.partner_birthdate: str = ""
        self.partner_birth_components: Dict[str, str] = {}

        self.guardian_name: str = ""
        self.guardian_nick: str = ""
        self.guardian_birthdate: str = ""
        self.guardian_birth_components: Dict[str, str] = {}

        self.children_names: List[str] = []
        self.pet_names: List[str] = []

        # Corporate / Enterprise context
        self.company: str = ""
        self.company_acronym: str = ""
        self.department: str = ""
        self.domain: str = ""
        self.project_names: List[str] = []
        self.target_url: str = ""

        # Lifestyle & Context
        self.mobile: str = ""
        self.city: str = ""
        self.sports_team: str = ""
        self.keywords: List[str] = []

    def to_dict(self) -> Dict[str, Any]:
        """Serialize profile parameters to JSON dictionary."""
        return {
            "name": self.name,
            "surname": self.surname,
            "nick": self.nick,
            "handles": self.handles,
            "email": self.email,
            "birthdate": self.birthdate,
            "partner_name": self.partner_name,
            "partner_nick": self.partner_nick,
            "partner_birthdate": self.partner_birthdate,
            "guardian_name": self.guardian_name,
            "guardian_nick": self.guardian_nick,
            "guardian_birthdate": self.guardian_birthdate,
            "children_names": self.children_names,
            "pet_names": self.pet_names,
            "company": self.company,
            "company_acronym": self.company_acronym,
            "department": self.department,
            "domain": self.domain,
            "project_names": self.project_names,
            "target_url": self.target_url,
            "mobile": self.mobile,
            "city": self.city,
            "sports_team": self.sports_team,
            "keywords": self.keywords,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> TargetProfile:
        """Instantiate TargetProfile from dictionary data."""
        p = cls()
        p.name = data.get("name", "").strip().lower()
        p.surname = data.get("surname", "").strip().lower()
        p.nick = data.get("nick", "").strip().lower()
        p.handles = [h.strip().lower() for h in data.get("handles", []) if h.strip()]
        p.email = data.get("email", "").strip().lower()
        p.birthdate = data.get("birthdate", "").strip()
        p.birth_components = parse_date_components(p.birthdate)

        p.partner_name = data.get("partner_name", "").strip().lower()
        p.partner_nick = data.get("partner_nick", "").strip().lower()
        p.partner_birthdate = data.get("partner_birthdate", "").strip()
        p.partner_birth_components = parse_date_components(p.partner_birthdate)

        p.guardian_name = data.get("guardian_name", "").strip().lower()
        p.guardian_nick = data.get("guardian_nick", "").strip().lower()
        p.guardian_birthdate = data.get("guardian_birthdate", "").strip()
        p.guardian_birth_components = parse_date_components(p.guardian_birthdate)

        p.children_names = [c.strip().lower() for c in data.get("children_names", []) if c.strip()]
        p.pet_names = [pet.strip().lower() for pet in data.get("pet_names", []) if pet.strip()]

        p.company = data.get("company", "").strip().lower()
        p.company_acronym = data.get("company_acronym", "").strip().lower()
        p.department = data.get("department", "").strip().lower()
        p.domain = data.get("domain", "").strip().lower()
        p.project_names = [pr.strip().lower() for pr in data.get("project_names", []) if pr.strip()]
        p.target_url = data.get("target_url", "").strip()

        p.mobile = re.sub(r"[^\d]", "", data.get("mobile", ""))
        p.city = data.get("city", "").strip().lower()
        p.sports_team = data.get("sports_team", "").strip().lower()
        p.keywords = [kw.strip().lower() for kw in data.get("keywords", []) if kw.strip()]
        return p
