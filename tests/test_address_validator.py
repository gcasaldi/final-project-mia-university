from src.address_validator import analyze_email_address


def test_legitimate_common_domains():
    assert analyze_email_address("gcasaldi@gmail.com")["risk"] == "NO_OBVIOUS_ADDRESS_ANOMALY"
    assert analyze_email_address("test@outlook.com")["risk"] == "NO_OBVIOUS_ADDRESS_ANOMALY"


def test_leetspeak_provider_impersonation():
    r = analyze_email_address("microsoft@m1crosoft.com")
    assert r["risk"] == "INVALID_OR_SUSPICIOUS"
    assert r["closest_provider"] == "microsoft.com"


def test_gmail_lookalikes():
    assert analyze_email_address("hot@gma1l.com")["risk"] == "INVALID_OR_SUSPICIOUS"
    assert analyze_email_address("security@gmial.com")["risk"] == "INVALID_OR_SUSPICIOUS"


def test_malformed_domain_separator():
    r = analyze_email_address("hot@gma1l,com")
    assert r["risk"] == "INVALID_OR_SUSPICIOUS"
    assert r["syntax_valid"] is False


def test_paypal_impersonation():
    r = analyze_email_address("support@paypa1.com")
    assert r["risk"] == "INVALID_OR_SUSPICIOUS"
    assert r["closest_provider"] == "paypal.com"
