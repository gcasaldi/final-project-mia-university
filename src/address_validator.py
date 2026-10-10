import re
from typing import Dict, List, Optional, Tuple

STRICT_EMAIL_RE = re.compile(
    r"^[A-Z0-9.!#$%&'*+/=?^_`{|}~-]+@(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,63}$",
    flags=re.IGNORECASE,
)

COMMON_PROVIDER_DOMAINS = {
    "gmail.com", "googlemail.com",
    "outlook.com", "hotmail.com", "live.com",
    "yahoo.com", "yahoo.it",
    "icloud.com", "me.com",
    "proton.me", "protonmail.com",
    "aol.com", "zoho.com", "gmx.com", "gmx.net",
    "libero.it", "virgilio.it", "alice.it", "tin.it",
    "tiscali.it", "tim.it", "fastwebnet.it", "aruba.it",
    "paypal.com", "amazon.com", "apple.com", "microsoft.com", "google.com",
    "poste.it", "intesasanpaolo.com", "unicredit.it",
}

LEET_OPTIONS = {
    "0": ("o",),
    "1": ("i", "l"),
    "3": ("e",),
    "4": ("a",),
    "5": ("s",),
    "7": ("t",),
    "8": ("b",),
    "9": ("g",),
}

ADDRESS_CANDIDATE_RE = re.compile(
    r"[A-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[^\s<>\"']+",
    flags=re.IGNORECASE,
)


def damerau_levenshtein(a: str, b: str) -> int:
    """Small-string Damerau-Levenshtein distance."""
    a, b = a.lower(), b.lower()
    d = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(len(a) + 1):
        d[i][0] = i
    for j in range(len(b) + 1):
        d[0][j] = j

    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            d[i][j] = min(
                d[i - 1][j] + 1,
                d[i][j - 1] + 1,
                d[i - 1][j - 1] + cost,
            )
            if i > 1 and j > 1 and a[i - 1] == b[j - 2] and a[i - 2] == b[j - 1]:
                d[i][j] = min(d[i][j], d[i - 2][j - 2] + 1)
    return d[-1][-1]


def leet_domain_variants(domain: str, max_variants: int = 64) -> set[str]:
    variants = {domain.lower()}
    for ch, replacements in LEET_OPTIONS.items():
        if ch not in domain:
            continue
        updated = set(variants)
        for item in variants:
            for repl in replacements:
                updated.add(item.replace(ch, repl))
                if len(updated) >= max_variants:
                    break
            if len(updated) >= max_variants:
                break
        variants = set(list(updated)[:max_variants])
    return variants


def nearest_common_provider(domain: str) -> Tuple[Optional[str], Optional[int], bool]:
    raw = domain.lower()
    if raw in COMMON_PROVIDER_DOMAINS:
        return raw, 0, False

    for variant in leet_domain_variants(raw):
        if variant != raw and variant in COMMON_PROVIDER_DOMAINS:
            return variant, 0, True

    best_provider = None
    best_distance = 999
    for provider in COMMON_PROVIDER_DOMAINS:
        dist = damerau_levenshtein(raw, provider)
        if dist < best_distance:
            best_provider, best_distance = provider, dist

    if best_distance <= 1:
        return best_provider, best_distance, False
    return None, None, False


def looks_like_address_only(raw: str) -> bool:
    raw = str(raw).strip()
    return (
        "@" in raw
        and "\n" not in raw
        and "\r" not in raw
        and not re.search(r"\s", raw)
        and len(raw) <= 320
    )


def analyze_email_address(address: str) -> Dict:
    original = str(address).strip().strip("<>")
    reasons: List[str] = []
    warnings_list: List[str] = []

    if not original:
        return {
            "address": original,
            "syntax_valid": False,
            "risk": "INVALID_OR_SUSPICIOUS",
            "reasons": ["Empty address."],
            "warnings": [],
            "closest_provider": None,
        }

    if original.count("@") != 1:
        return {
            "address": original,
            "syntax_valid": False,
            "risk": "INVALID_OR_SUSPICIOUS",
            "reasons": ["An email address must contain exactly one @ symbol."],
            "warnings": [],
            "closest_provider": None,
        }

    local, domain = original.rsplit("@", 1)
    domain_lower = domain.lower().rstrip(".")
    diagnostic_domain = domain_lower.replace(",", ".").replace(";", ".")

    if "," in domain or ";" in domain:
        reasons.append("The domain contains a comma/semicolon instead of a dot.")

    syntax_valid = bool(STRICT_EMAIL_RE.fullmatch(original))
    if not syntax_valid:
        reasons.append("The address does not match a valid standard email-domain format.")
    if not local:
        reasons.append("Missing local part before @.")
    if not domain:
        reasons.append("Missing domain after @.")

    if any(ord(ch) > 127 for ch in original):
        warnings_list.append("Non-ASCII characters detected; review for possible Unicode homoglyphs.")
    if domain_lower.startswith("xn--") or ".xn--" in domain_lower:
        warnings_list.append("Punycode/IDN domain detected; manual verification is recommended.")

    closest_provider = None
    candidate_domains = [domain_lower]
    if diagnostic_domain != domain_lower:
        candidate_domains.append(diagnostic_domain)

    for candidate in candidate_domains:
        provider, distance, via_leet = nearest_common_provider(candidate)
        if provider and candidate != provider:
            closest_provider = provider
            if via_leet:
                reasons.append(
                    f"Digit/letter substitution makes domain '{candidate}' look like '{provider}'."
                )
            else:
                reasons.append(
                    f"Domain '{candidate}' is only {distance} edit away from common provider '{provider}'."
                )
            break

    if any(ch.isdigit() for ch in domain_lower) and closest_provider:
        reasons.append("A digit is used inside a provider lookalike domain.")

    labels = diagnostic_domain.split(".") if diagnostic_domain else []
    if any(label == "" for label in labels):
        reasons.append("The domain contains an empty label / repeated separator.")

    for label in labels:
        if label.startswith("-") or label.endswith("-"):
            reasons.append("A domain label starts or ends with a hyphen.")
            break

    if reasons:
        risk = "INVALID_OR_SUSPICIOUS"
    elif warnings_list:
        risk = "REVIEW"
    else:
        risk = "NO_OBVIOUS_ADDRESS_ANOMALY"

    return {
        "address": original,
        "syntax_valid": syntax_valid,
        "risk": risk,
        "reasons": reasons,
        "warnings": warnings_list,
        "closest_provider": closest_provider,
    }


def extract_address_candidates(text: str) -> List[str]:
    candidates: List[str] = []
    for match in ADDRESS_CANDIDATE_RE.findall(str(text)):
        candidate = match.strip("()[]{}<>\"'")
        candidate = re.sub(r"[.!?:]+$", "", candidate)
        if candidate.endswith(",") or candidate.endswith(";"):
            candidate = candidate[:-1]
        if "@" in candidate:
            candidates.append(candidate)
    return list(dict.fromkeys(candidates))


def inspect_addresses_in_text(text: str) -> List[Dict]:
    findings = []
    for address in extract_address_candidates(text):
        result = analyze_email_address(address)
        if result["risk"] != "NO_OBVIOUS_ADDRESS_ANOMALY":
            findings.append(result)
    return findings
