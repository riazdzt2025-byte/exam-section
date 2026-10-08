"""ছোট সহায়ক ফাংশন — বাংলা সংখ্যা, ঢাকা টাইমজোন ইত্যাদি।"""

from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

DHAKA = ZoneInfo("Asia/Dhaka")

BN_DIGITS = "০১২৩৪৫৬৭৮৯"
_BN_TABLE = str.maketrans("0123456789", BN_DIGITS)


def to_bn(value):
    """ইংরেজি অঙ্ককে বাংলা অঙ্কে বদলায় (অন্য অক্ষর অপরিবর্তিত থাকে)।"""
    return str(value).translate(_BN_TABLE)


def local_today():
    """ঢাকা টাইমজোন অনুযায়ী আজকের তারিখ।"""
    return datetime.now(DHAKA).date()


def day_bounds(day: date):
    """কোনো তারিখের শুরু ও শেষ (ঢাকা সময়, aware datetime)।"""
    start = datetime(day.year, day.month, day.day, tzinfo=DHAKA)
    return start, start + timedelta(days=1)


def parse_iso_date(text, fallback=None):
    """YYYY-MM-DD স্ট্রিং থেকে date; ভুল হলে fallback (না দিলে আজ)।"""
    if text:
        try:
            return datetime.strptime(text.strip(), "%Y-%m-%d").date()
        except ValueError:
            pass
    return fallback or local_today()
