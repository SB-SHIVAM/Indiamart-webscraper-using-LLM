import time, random, re
import pandas as pd
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

INPUT_FILE = "india_cement.xlsx"
OUTPUT_FILE = "results.txt"


# =========================
# UTILS
# =========================
def sleep(a=1.5, b=2.5):
    time.sleep(random.uniform(a, b))


def css_width_to_stars(style):
    if not style:
        return "N/A"
    m = re.search(r"(\d+)%", style)
    return str(round(int(m.group(1)) / 20)) if m else "N/A"


def extract_float(text):
    m = re.search(r"\b([1-4](\.\d+)?|5(\.0)?)\b", text)
    return m.group(1) if m else None


# =========================
# NAME MATCHING (STRICT)
# =========================
def normalize_name(name):
    stop = {
        "pvt", "ltd", "limited", "industries", "industry",
        "company", "co", "traders", "suppliers", "india", "ind"
    }
    return {
        w for w in re.sub(r"[^a-z0-9 ]", "", name.lower()).split()
        if w not in stop and len(w) > 2
    }


def is_name_match(input_name, matched_name):
    if not input_name or not matched_name or matched_name == "N/A":
        return False
    a = normalize_name(input_name)
    b = normalize_name(matched_name)
    return len(a & b) >= 2 or a.issubset(b)


# =========================
# COMPANY NAME
# =========================
def extract_company_name(soup):
    sup = soup.select_one("div.supplierInfoDiv a.cardlinks")
    if sup:
        return sup.get_text(strip=True)

    for sel in ["h1.FM_h1", "div.FM_ttl", "h1"]:
        el = soup.select_one(sel)
        if el and len(el.get_text(strip=True)) > 3:
            return el.get_text(strip=True)

    return "N/A"


# =========================
# OVERALL RATING (ALL KNOWN FORMATS)
# =========================
def extract_overall_rating(html, soup):
    out = {"rating": "N/A", "total": "N/A"}

    # 1️⃣ JS object (testimonial pages)
    m = re.search(
        r'"OVERALL_RATING"\s*:\s*"([\d.]+)".*?"TOTAL_RATINGS_COUNT"\s*:\s*"(\d+)"',
        html, re.S
    )
    if m:
        return {"rating": m.group(1), "total": m.group(2)}

    # 2️⃣ Ratings & Reviews – NEW FM format
    fm_new = soup.select_one("div.FM_s .FM_str .FM_bo")
    if fm_new:
        r = extract_float(fm_new.get_text())
        cnt = soup.select_one("div.FM_s p")
        c = re.search(r"\d+", cnt.get_text()) if cnt else None
        return {"rating": r or "N/A", "total": c.group() if c else "N/A"}

    # 3️⃣ OLD gradient rating block
    grad = soup.select_one("p.rtng-get span.fwb")
    if grad:
        r = extract_float(grad.get_text())
        cnt = soup.select_one("p.rtng-cont")
        c = re.search(r"\d+", cnt.get_text()) if cnt else None
        return {"rating": r or "N/A", "total": c.group() if c else "N/A"}

    # 4️⃣ Supplier card rating
    sup = soup.select_one("div.supplierInfoDiv span.bo.color")
    if sup:
        r = extract_float(sup.get_text())
        cnt = sup.find_next_sibling("span")
        c = re.search(r"\d+", cnt.get_text()) if cnt else None
        return {"rating": r or "N/A", "total": c.group() if c else "N/A"}

    # 5️⃣ FM old block
    fm_old = soup.select_one(".FM_str .FM_bo")
    if fm_old:
        r = extract_float(fm_old.get_text())
        return {"rating": r or "N/A", "total": "N/A"}

    # 6️⃣ VERY OLD testimonial
    old = soup.select_one("span.first-span")
    if old:
        r = extract_float(old.get_text())
        return {"rating": r or "N/A", "total": "N/A"}

    return out


# =========================
# USER SATISFACTION
# =========================
def extract_user_satisfaction(soup):
    res = {"response": "N/A", "quality": "N/A", "delivery": "N/A"}

    for b in soup.select("div.mSR_w33"):
        lbl = b.select_one("p")
        val = b.select_one("span")
        if lbl and val:
            l = lbl.get_text(strip=True).lower()
            v = val.get_text(strip=True)
            if "response" in l:
                res["response"] = v
            elif "quality" in l:
                res["quality"] = v
            elif "delivery" in l:
                res["delivery"] = v

    for row in soup.select("p.FM_ds7"):
        lbl = row.select_one(".FM_pbarS")
        val = row.find("span", string=lambda x: x and "%" in x)
        if lbl and val:
            l = lbl.get_text(strip=True).lower()
            if "response" in l:
                res["response"] = val.get_text(strip=True)
            elif "quality" in l:
                res["quality"] = val.get_text(strip=True)
            elif "delivery" in l:
                res["delivery"] = val.get_text(strip=True)

    for li in soup.select("li.grph-item"):
        lbl = li.select_one(".stfn-area")
        val = li.select_one(".grph-count")
        if lbl and val:
            l = lbl.get_text(strip=True).lower()
            if "response" in l:
                res["response"] = val.get_text(strip=True)
            elif "quality" in l:
                res["quality"] = val.get_text(strip=True)
            elif "delivery" in l:
                res["delivery"] = val.get_text(strip=True)

    return res


# =========================
# REVIEWS (ALL FORMATS)
# =========================
def extract_reviews(soup):
    reviews = []

    # Old reviews
    for c in soup.select("div.revw-user"):
        reviews.append({
            "name": c.select_one(".revw-nme").get_text(strip=True) if c.select_one(".revw-nme") else "N/A",
            "stars": css_width_to_stars(c.select_one(".star-clr")["style"]) if c.select_one(".star-clr") else "N/A",
            "text": c.select_one(".revw-comntmr11").get_text(strip=True) if c.select_one(".revw-comntmr11") else "N/A"
        })

    # FM reviews (FM_rvwC + FM_rvw1)
    for c in soup.select("div.FM_rvwC"):
        star = c.select_one(".FM_flsRt")
        reviews.append({
            "name": (c.find("span") or "").get_text(strip=True),
            "stars": css_width_to_stars(star["style"]) if star else "N/A",
            "text": "N/A"
        })

    return reviews


# =========================
# MAIN
# =========================
def run():
    df = pd.read_excel(INPUT_FILE)

    with sync_playwright() as p, open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        for _, row in df.iterrows():
            input_company = str(row["Company"]).strip()
            if not input_company:
                continue

            page.goto("https://www.indiamart.com/")
            page.fill("#search_string", input_company)
            page.press("#search_string", "Enter")
            sleep()

            try:
                page.wait_for_selector("span.bo.color", timeout=8000)
            except:
                continue

            with page.context.expect_page() as pop:
                page.locator("span.bo.color").first.click()

            rp = pop.value
            rp.wait_for_load_state("domcontentloaded")

            html = rp.content()
            soup = BeautifulSoup(html, "html.parser")

            matched = extract_company_name(soup)

            # 🔒 HARD SKIP IF NAME DOES NOT MATCH
            if not is_name_match(input_company, matched):
                rp.close()
                continue

            rating = extract_overall_rating(html, soup)
            metrics = extract_user_satisfaction(soup)
            reviews = extract_reviews(soup)

            f.write("\n" + "=" * 60 + "\n")
            f.write(f"Input Company   : {input_company}\n")
            f.write(f"Matched Company : {matched}\n\n")
            f.write(f"Overall Rating  : {rating['rating']} / 5\n")

            f.write(f"Response : {metrics['response']}\n")
            f.write(f"Quality  : {metrics['quality']}\n")
            f.write(f"Delivery : {metrics['delivery']}\n\n")

            for r in reviews:
                f.write(f"- {r['name']} | {r['stars']} | {r['text']}\n")

            rp.close()

        browser.close()


if __name__ == "__main__":
    run()
