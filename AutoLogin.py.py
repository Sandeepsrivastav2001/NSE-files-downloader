import os
import time
import re
import imaplib
import email
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from tkinter import Tk, Label, Entry, Button, simpledialog
from PIL import Image, ImageTk

# === CONFIG ===
USERID = "VIPINENIT11893"
MEMBERCODE = "11893"
PASSWORD = "Cnbfinwiz@9876"
DOWNLOAD_PATH = os.path.join(os.path.expanduser("~"), "Desktop", "NSE Files")

EMAIL_USER = "dme@cnbfinwiz.com"
EMAIL_PASS = "wgum xrke wxqm xdzv"

def show_captcha(driver):
    folder = os.path.join(DOWNLOAD_PATH, "captcha_screenshots")
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, "captcha.png")
    driver.save_screenshot(path)
    img = Image.open(path).crop((1040, 440, 1300, 580))
    img.save(path)

    captcha_value = {}
    def on_submit():
        captcha_value['text'] = entry.get()
        root.destroy()

    root = Tk()
    root.title("Enter CAPTCHA")
    img_tk = ImageTk.PhotoImage(img.resize((230, 70)))
    Label(root, image=img_tk).pack()
    entry = Entry(root, font=("Arial", 14))
    entry.pack()
    Button(root, text="Submit", command=on_submit).pack()
    root.mainloop()
    return captcha_value.get("text", "")

def fetch_otp(email_user, email_pass, timeout=120):
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login(email_user, email_pass)
    mail.select('inbox')

    start = time.time()
    while time.time() - start < timeout:
        status, data = mail.search(None, '(UNSEEN)')
        ids = data[0].split()
        for num in reversed(ids):
            status, msg_data = mail.fetch(num, '(RFC822)')
            msg = email.message_from_bytes(msg_data[0][1])
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode()
                        otp = re.search(r"\b(\d{4,6})\b", body)
                        if otp:
                            return otp.group(1)
            else:
                body = msg.get_payload(decode=True).decode()
                otp = re.search(r"\b(\d{4,6})\b", body)
                if otp:
                    return otp.group(1)
        time.sleep(5)
    return None

def fill_input(driver, elem, value):
    # Clear and send keys slowly with JS input event
    elem.clear()
    for ch in value:
        elem.send_keys(ch)
        time.sleep(0.1)
    # Trigger input event (sometimes required for validation)
    driver.execute_script("arguments[0].dispatchEvent(new Event('input'));", elem)
    driver.execute_script("arguments[0].dispatchEvent(new Event('change'));", elem)

def main():
    opts = Options()
    opts.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)

    try:
        driver.get("https://ims.connect2nsccl.com/MemberPortal/")
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "userid")))

        fill_input(driver, driver.find_element(By.ID, "userid"), USERID)
        fill_input(driver, driver.find_element(By.ID, "memberCode"), MEMBERCODE)
        fill_input(driver, driver.find_element(By.ID, "password1"), PASSWORD)

        captcha_text = show_captcha(driver)
        fill_input(driver, driver.find_element(By.ID, "UserCaptchaCode"), captcha_text)

        # Dismiss modal if any
        try:
            modal = driver.find_element(By.ID, "myModal")
            if modal.is_displayed():
                driver.execute_script("arguments[0].style.display='none';", modal)
        except:
            pass

        login_btn = driver.find_element(By.XPATH, "//button[contains(translate(text(), 'LOGIN', 'login'), 'login')]")
        driver.execute_script("arguments[0].click();", login_btn)

        # Wait for OTP page or mainMenu page
        WebDriverWait(driver, 60).until(
            lambda d: "validateOtp" in d.current_url or "mainMenu" in d.current_url
        )

        if "validateOtp" in driver.current_url:
            otp_input = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.ID, "otp")))
            otp_code = fetch_otp(EMAIL_USER, EMAIL_PASS)
            if not otp_code:
                print("Failed to fetch OTP automatically.")
                return

            fill_input(driver, otp_input, otp_code)

            submit_btn = driver.find_element(By.XPATH, "//button[contains(text(),'Submit') or contains(text(),'Verify')]")
            driver.execute_script("arguments[0].click();", submit_btn)

            WebDriverWait(driver, 60).until(lambda d: "mainMenu" in d.current_url)
            print("✅ Logged in successfully with OTP!")

        else:
            print("✅ Logged in successfully without OTP!")

    except Exception as e:
        print("Error during login:", e)

    finally:
        input("Press Enter to exit...")
        driver.quit()

if __name__ == "__main__":
    main()
