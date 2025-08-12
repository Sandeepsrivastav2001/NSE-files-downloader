import os, time, imaplib, email, re
from datetime import datetime as _dt
from tkinter import Tk, Label, Entry, Button, simpledialog, messagebox
from PIL import Image, ImageTk
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ===== CONFIG =====
USERID = "VIPINENIT11893"
MEMBERCODE = "11893"
PASSWORD = "Cnbfinwiz@9876"
EMAIL_ID = "dme@cnbfinwiz.com"
APP_PASSWORD = "nsfv wafu ycol yoeg"
MASTER_KEY = ""  # Your master key here

# ── Master Key ────────────────────────────
def verify_master_key():
    root = Tk(); root.withdraw()
    for _ in range(3):
        input_key = simpledialog.askstring("🔐 Master Key Required",
                                           "Enter MasterKey as Password to Start:",
                                           show='*')
        if input_key == MASTER_KEY:
            root.destroy()
            print("✅ Master key accepted. Please wait for Browser to open")
            return True
        messagebox.showerror("❌ Invalid Key", "Wrong Master Key.")
    root.destroy()
    print("🔒 Access denied.")
    return False

# ── Browser ───────────────────────────────
def create_driver():
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.set_page_load_timeout(60)
    return driver

# ── OTP Fetch (Latest & Fresh Only) ─────────────────────────────
def get_otp_from_gmail():
    """Fetch the latest unread OTP from Gmail (within last 3 minutes)."""
    MAX_AGE_SECONDS = 180  # Only accept OTP emails newer than this
    for _ in range(10):  # retry up to 10 times
        try:
            mail = imaplib.IMAP4_SSL("imap.gmail.com")
            mail.login(EMAIL_ID, APP_PASSWORD)
            mail.select("inbox")

            # Search for unread OTP emails
            status, data = mail.search(None, '(UNSEEN SUBJECT "OTP")')

            if data[0]:
                latest_id = data[0].split()[-1]
                status, msg_data = mail.fetch(latest_id, "(RFC822)")
                msg = email.message_from_bytes(msg_data[0][1])

                # Check email date
                email_date = email.utils.parsedate_to_datetime(msg["Date"])
                if (_dt.now(email_date.tzinfo) - email_date).total_seconds() > MAX_AGE_SECONDS:
                    print("⚠ OTP email is too old, waiting for a new one...")
                    time.sleep(5)
                    continue

                # Extract OTP from body
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() in ("text/plain", "text/html"):
                            try:
                                body = part.get_payload(decode=True).decode(errors='ignore')
                            except:
                                body = ""
                            if body:
                                break
                else:
                    try:
                        body = msg.get_payload(decode=True).decode(errors='ignore')
                    except:
                        body = ""

                otp_match = re.search(r"\b\d{6}\b", body)
                if otp_match:
                    return otp_match.group(0)
                else:
                    print("⚠ No OTP found in latest email.")
            else:
                print("⏳ Waiting for new OTP email...")

            time.sleep(5)

        except Exception as e:
            print("OTP fetch error:", e)
            time.sleep(5)

    return None

# ── CAPTCHA Popup ─────────────────────────
def get_captcha_and_login(driver):
    path = os.path.join(os.getcwd(), f"captcha_{_dt.now().strftime('%H-%M-%S')}.png")
    driver.save_screenshot(path)

    try:
        img_full = Image.open(path)
        w, h = img_full.size
        crop_width = int(w * 0.30)
        crop_height = int(h * 0.40)
        left = max(w - crop_width, 0)
        top = max(h - crop_height, 0)
        img = img_full.crop((left, top, w, h))
    except:
        img = Image.open(path)

    root = Tk()
    root.title("🔐 CAPTCHA Required")
    root.attributes('-topmost', True)

    img_tk = ImageTk.PhotoImage(img)
    Label(root, text="Please enter the CAPTCHA:").pack(pady=5)
    Label(root, image=img_tk).pack()
    entry = Entry(root, font=('Arial', 14))
    entry.pack(pady=5)

    def on_submit():
        captcha_text = entry.get()
        if not captcha_text:
            messagebox.showerror("Error", "Please enter CAPTCHA")
            return

        driver.find_element(By.ID, "userid").clear()
        driver.find_element(By.ID, "userid").send_keys(USERID)
        driver.find_element(By.ID, "memberCode").clear()
        driver.find_element(By.ID, "memberCode").send_keys(MEMBERCODE)
        driver.find_element(By.ID, "password1").clear()
        driver.find_element(By.ID, "password1").send_keys(PASSWORD)
        driver.find_element(By.ID, "UserCaptchaCode").clear()
        driver.find_element(By.ID, "UserCaptchaCode").send_keys(captcha_text)

        try:
            login_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Login')]"))
            )
            driver.execute_script("arguments[0].click();", login_btn)
        except Exception as e:
            print("⚠ Could not click login button:", e)

        root.destroy()

    Button(root, text="Submit & Login", command=on_submit).pack(pady=5)
    root.mainloop()

# ── Handle OTP Page ───────────────────────
def handle_otp_page(driver):
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//h1[contains(text(),'One Time Password')]"))
        )
        print("📩 OTP page detected. Fetching OTP from Gmail...")
        otp = get_otp_from_gmail()
        if otp:
            print(f"✅ OTP fetched: {otp}")
            otp_box = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='One Time Password']"))
            )
            otp_box.clear()
            otp_box.send_keys(otp)

            # Click the Submit button
            submit_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//input[@value='Submit' or contains(text(),'Submit')]"))
            )
            driver.execute_script("arguments[0].click();", submit_btn)
            print("🔓 OTP submitted successfully.")
        else:
            print("❌ Failed to fetch OTP automatically.")
    except Exception as e:
        print("⚠ OTP page handling error:", e)

# ── Main ──────────────────────────────────
if not verify_master_key():
    exit()

driver = create_driver()
driver.get("https://ims.connect2nsccl.com/MemberPortal/")

time.sleep(3)
get_captcha_and_login(driver)
handle_otp_page(driver)

print("✅ Process complete. Browser will remain open.")
while True:
    time.sleep(1)
