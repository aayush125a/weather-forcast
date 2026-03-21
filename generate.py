from datetime import datetime
import pytz

# ── Timezones ──────────────────────────────────────────────────────────────
ZONES = [
    ("🇳🇵 Nepal",       "Asia/Kathmandu"),
    ("🇮🇳 India",        "Asia/Kolkata"),
    ("🇦🇺 Australia",    "Australia/Sydney"),
    ("🇺🇸 United States","America/New_York"),
    ("🇵🇭 Philippines",  "Asia/Manila"),
    ("🇳🇬 Nigeria",      "Africa/Lagos"),
]

# ── Quotes (rotates daily) ─────────────────────────────────────────────────
QUOTES = [
    ("The secret of getting ahead is getting started.", "Mark Twain"),
    ("It always seems impossible until it's done.", "Nelson Mandela"),
    ("Don't watch the clock; do what it does. Keep going.", "Sam Levenson"),
    ("Time you enjoy wasting is not wasted time.", "Marthe Troly-Curtin"),
    ("The future depends on what you do today.", "Mahatma Gandhi"),
    ("Start where you are. Use what you have. Do what you can.", "Arthur Ashe"),
    ("Small steps every day lead to big changes over time.", "Anonymous"),
    ("Your time is limited, don't waste it living someone else's life.", "Steve Jobs"),
    ("Energy and persistence conquer all things.", "Benjamin Franklin"),
    ("Act as if what you do makes a difference. It does.", "William James"),
    ("Success is the sum of small efforts, repeated day in and day out.", "Robert Collier"),
    ("Well done is better than well said.", "Benjamin Franklin"),
    ("The only way to do great work is to love what you do.", "Steve Jobs"),
    ("In the middle of every difficulty lies opportunity.", "Albert Einstein"),
    ("Believe you can and you're halfway there.", "Theodore Roosevelt"),
    ("It does not matter how slowly you go as long as you do not stop.", "Confucius"),
    ("Life is what happens when you're busy making other plans.", "John Lennon"),
    ("Strive not to be a success, but rather to be of value.", "Albert Einstein"),
    ("The mind is everything. What you think you become.", "Buddha"),
    ("Happiness is not something ready-made. It comes from your own actions.", "Dalai Lama"),
    ("You miss 100% of the shots you don't take.", "Wayne Gretzky"),
    ("Whether you think you can or think you can't, you're right.", "Henry Ford"),
    ("The best time to plant a tree was 20 years ago. The second best time is now.", "Chinese Proverb"),
    ("An unexamined life is not worth living.", "Socrates"),
    ("Spread love everywhere you go.", "Mother Teresa"),
    ("When you reach the end of your rope, tie a knot in it and hang on.", "Franklin D. Roosevelt"),
    ("Always remember that you are absolutely unique.", "Margaret Mead"),
    ("Do not go where the path may lead; go instead where there is no path.", "Ralph Waldo Emerson"),
    ("You will face many defeats in life, but never let yourself be defeated.", "Maya Angelou"),
    ("The greatest glory in living lies not in never falling, but in rising every time we fall.", "Nelson Mandela"),
    ("In the end, it's not the years in your life that count. It's the life in your years.", "Abraham Lincoln"),
]

def main():
    utc_now = datetime.now(pytz.utc)
    quote_text, quote_author = QUOTES[utc_now.timetuple().tm_yday % len(QUOTES)]

    lines = []

    # ── Header ───────────────────────────────────────────────────────────────
    lines.append("# 🕐 World Time Dashboard\n")
    lines.append(f"> 🌐 **UTC Time:** `{utc_now.strftime('%Y-%m-%d %H:%M:%S')} UTC`\n")
    lines.append("---\n")

    # ── Time Table ───────────────────────────────────────────────────────────
    lines.append("## 🌍 Current Local Times\n")
    lines.append("| Country | Local Time | UTC Offset |")
    lines.append("|---------|-----------|------------|")

    for label, tz_name in ZONES:
        tz = pytz.timezone(tz_name)
        local_dt = utc_now.astimezone(tz)
        offset = local_dt.strftime("%z")
        offset_str = f"UTC{offset[:3]}:{offset[3:]}"
        lines.append(
            f"| {label} | **{local_dt.strftime('%A, %d %b %Y  %I:%M %p')}** | {offset_str} |"
        )

    lines.append("")
    lines.append("---\n")

    # ── Nepal vs UTC ─────────────────────────────────────────────────────────
    nepal_tz = pytz.timezone("Asia/Kathmandu")
    nepal_now = utc_now.astimezone(nepal_tz)
    diff_total_minutes = int(nepal_tz.utcoffset(utc_now.replace(tzinfo=None)).total_seconds() // 60)
    diff_hours = diff_total_minutes // 60
    diff_mins  = diff_total_minutes % 60

    lines.append("## 🇳🇵 Nepal vs UTC\n")
    lines.append("| | Time |")
    lines.append("|---|---|")
    lines.append(f"| 🌐 UTC | `{utc_now.strftime('%I:%M %p')}` |")
    lines.append(f"| 🇳🇵 Nepal (NPT) | `{nepal_now.strftime('%I:%M %p')}` |")
    lines.append(f"| ⏩ Difference | Nepal is **{diff_hours} hours {diff_mins} minutes ahead** of UTC |")
    lines.append("")
    lines.append(
        f"> 💡 **Fun fact:** Nepal is one of the few countries in the world with a "
        f"**+5:45 offset** — a rare 45-minute timezone that sets it apart from all its neighbours!"
    )
    lines.append("")
    lines.append("---\n")

    # ── Quote ────────────────────────────────────────────────────────────────
    lines.append("## 💬 Quote of the Day\n")
    lines.append(f"> *\"{quote_text}\"*")
    lines.append(f">")
    lines.append(f"> — **{quote_author}**\n")
    lines.append("---\n")

    # ── Footer ───────────────────────────────────────────────────────────────
    lines.append(
        f"<sub>⏰ Auto-updated every day at **9:00 AM IST** · "
        f"Last run: {utc_now.strftime('%d %b %Y, %H:%M UTC')}</sub>"
    )

    with open("README.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print("✅ README.md generated successfully.")

if __name__ == "__main__":
    main()
