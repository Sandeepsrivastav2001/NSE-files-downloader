# ── CONFIG ───────────────────────────────────────────────────────────
USERID = "VIPINENIT11893"
MEMBERCODE = "11893"
PASSWORD = "Cnbfinwiz@9876"
EMAIL_ID = "dme@cnbfinwiz.com"
APP_PASSWORD = "wgum xrke wxqm xdzv"
DOWNLOAD_PATH = r"G:\My Drive\NSE Files"
SLEEP_SHORT = 1
MASTER_KEY = "mySecure@2025"

# ── IMPORTS ───────────────────────────────────────────────────────────
import os, time, traceback
from datetime import datetime as _dt
from tkinter import Tk, Label, Entry, Button, simpledialog, messagebox
from PIL import Image, ImageTk
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ── SECURITY: Master Key Prompt ──────────────────────────────────────
def verify_master_key():
    root = Tk()
    root.withdraw()
    for _ in range(3):
        input_key = simpledialog.askstring("🔐 Master Key Required", "Enter Master Key as Password to Start:", show='*')
        if input_key == MASTER_KEY:
            root.destroy()
            print("✅ Master key accepted. Starting automation...")
            return True
        messagebox.showerror("❌ Invalid Key", "Wrong Master Key. Please Try again.")
    root.destroy()
    print("🔒 Access denied. Exiting.")
    return False

# ── GUI for CAPTCHA ──────────────────────────────────────────────────
def show_captcha_popup_and_get_input(driver, base_path):
    user_input = {}
    folder = os.path.join(base_path, "screenshots", _dt.today().strftime("%Y-%m-%d"))
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, f"captcha_{_dt.now().strftime('%H-%M-%S')}.png")
    driver.save_screenshot(path)
    print(f"📸 CAPTCHA Screenshot saved at: {path}")

    def on_submit():
        user_input['captcha'] = entry.get()
        root.destroy()

    root = Tk()
    root.title("🔐 CAPTCHA Required")
    img = Image.open(path)
    img = img.crop((1040, 440, 1300, 580))
    img = img.resize((230, 70))
    img_tk = ImageTk.PhotoImage(img)
    Label(root, text="Please enter the CAPTCHA:").pack(pady=5)
    Label(root, image=img_tk).pack()
    entry = Entry(root, font=('Arial', 14))
    entry.pack(pady=5)
    Button(root, text="Submit", command=on_submit).pack(pady=5)
    root.mainloop()
    return user_input.get("captcha", "")

# ── UTILITIES ────────────────────────────────────────────────────────
def is_today_date(txt):
    today = _dt.today().date()
    for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y%m%d", "%d%m%Y"):
        try:
            if _dt.strptime(txt.strip(), fmt).date() == today:
                return True
        except:
            pass
    return False

def try_all_clicks(driver, element):
    for attempt in [
        lambda el: el.click(),
        lambda el: ActionChains(driver).move_to_element(el).click().perform(),
        lambda el: driver.execute_script("arguments[0].click();", el),
        lambda el: el.send_keys("\n"),
        lambda el: (driver.execute_script("arguments[0].scrollIntoView(true);", el), time.sleep(0.5), driver.execute_script("arguments[0].click();", el)),
        lambda el: (ActionChains(driver).move_by_offset(1, 1).click(el).perform()),
        lambda el: driver.execute_script("el.click();", el),
        lambda el: driver.execute_script("arguments[0].dispatchEvent(new MouseEvent('click', { bubbles: true }));", el),
        lambda el: driver.execute_script("arguments[0].dispatchEvent(new Event('mousedown'));", el),
        lambda el: driver.execute_script("arguments[0].dispatchEvent(new Event('mouseup'));", el),
        lambda el: driver.execute_script("arguments[0].dispatchEvent(new Event('click'));", el),
    ]:
        try:
            attempt(element)
            return True
        except:
            continue
    return False

# ── DOWNLOAD FILES ───────────────────────────────────────────────────
def download_today_files(driver, downloaded=set()):
    driver.get("https://ims.connect2nsccl.com/MemberPortal/extDownloads")
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, "//table//th[contains(text(),'Receive Date')]")))
    time.sleep(SLEEP_SHORT * 2)
    rows = driver.find_elements(By.XPATH, "//table//tbody/tr")
    print(f"📄 Found {len(rows)} rows in downloads table")
    new, fails = [], []
    for row in rows:
        cols = row.find_elements(By.TAG_NAME, "td")
        if len(cols) < 4:
            continue
        date_txt = cols[0].text.strip()
        fname = cols[2].text.strip()
        download_cell = cols[-1]
        if not is_today_date(date_txt) or fname in downloaded:
            continue
        try:
            link = download_cell.find_element(By.XPATH, ".//a|.//button")
            driver.execute_script("arguments[0].scrollIntoView(true);", link)
            time.sleep(0.5)
            success = try_all_clicks(driver, link)
            if success:
                new.append(fname)
                downloaded.add(fname)
                print(f"⬇️  Downloaded: {fname}")
            else:
                fails.append((fname, "All click attempts failed"))
        except Exception as e:
            fails.append((fname, f"Error: {e}"))
    return new, fails

# ── LOGIN AND DOWNLOAD ──────────────────────────────────────────────
def login_and_navigate_to_downloads(driver):
    driver.get("https://ims.connect2nsccl.com/MemberPortal/")
    WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.TAG_NAME, "input")))
    driver.find_element(By.ID, "userid").send_keys(USERID)
    driver.find_element(By.ID, "memberCode").send_keys(MEMBERCODE)
    driver.find_element(By.ID, "password1").send_keys(PASSWORD)
    print("🔍 Waiting for CAPTCHA input via GUI...")
    captcha_text = show_captcha_popup_and_get_input(driver, DOWNLOAD_PATH)
    driver.find_element(By.ID, "UserCaptchaCode").send_keys(captcha_text)
    print(f"✅ CAPTCHA filled using field ID 'UserCaptchaCode': {captcha_text}")
    try:
        modal = driver.find_element(By.ID, "myModal")
        if modal.is_displayed():
            driver.execute_script("arguments[0].style.display='none';", modal)
            print("⚠️ Modal popup was dismissed before clicking login")
    except:
        pass
    login_btn = driver.find_element(By.XPATH, "//button[contains(translate(text(), 'LOGIN', 'login'), 'login')]")
    login_btn.click()
    WebDriverWait(driver, 180).until(lambda d: "mainMenu" in d.current_url or "validateOtp" in d.current_url)
    if "validateOtp" in driver.current_url:
        raise NotImplementedError("🔐 OTP step needs to be implemented.")
    print("✅ Logged in successfully. Navigating to Downloads...")
    downloaded = set()
    while True:
        new, fails = download_today_files(driver, downloaded)
        if new:
            print("✅ New files downloaded:", new)
        if fails:
            print("❌ Failed:", fails)
        print("⏳ Waiting 5 minutes before refresh...")
        time.sleep(300)

# ── MAIN ────────────────────────────────────────────────────────────
def main():
    if not verify_master_key():
        return
    dated_folder = os.path.join(DOWNLOAD_PATH, _dt.today().strftime('%Y-%m-%d'))
    os.makedirs(dated_folder, exist_ok=True)
    opts = Options()
    prefs = {
        "download.default_directory": dated_folder,
        "download.prompt_for_download": False,
        "profile.default_content_settings.popups": 0,
    }
    opts.add_experimental_option("prefs", prefs)
    opts.add_argument("--start-maximized")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
    try:
        login_and_navigate_to_downloads(driver)
    except Exception as e:
        print("❌ Error:", e)
        traceback.print_exc()
    finally:
        input("⏹ Press ENTER to close browser...")
        driver.quit()

# ── RUN ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()