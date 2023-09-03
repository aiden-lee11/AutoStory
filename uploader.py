from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium_stealth import stealth
import random, requests, time, os, csv
import undetected_chromedriver as uc
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager as CM
import pyautogui



def sleeper():
    timers = [
            "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"
            ]
    time.sleep(float("0." + random.choice(timers[0:3]) + random.choice(timers[0:4]) + random.choice(timers[0:9])))

def uploader(video_paths, titles, authors, video_durs):
    options = webdriver.ChromeOptions()

    options.add_argument(r'--user-data-dir=C:\Users\Villa\AppData\Local\Google\Chrome\User Data')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    driver = uc.Chrome(use_subprocess=True, headless=False)
    driver.maximize_window()
    script_directory = os.path.dirname(os.path.abspath(__file__))

    
    variables = [
        "https://www.tiktok.com/login/phone-or-email/email", '//*[@id="loginContainer"]/div[1]/form/div[1]/input',
        '//*[@id="loginContainer"]/div[1]/form/div[2]/div/input', "//button[@type='submit']",
        "//div[@class='tiktok-txpjn9-DivIconContainer']//i/svg"
    ]

    with open(os.path.join(script_directory, 'user.txt')) as f:
        line = f.readlines()
    username = line[0][10:-1]
    password = line[1][10:-1 ]

    stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
            )
    driver.get(variables[0])
    
    sign_in(driver=driver, variables=variables, username=username, password=password, video_path=video_paths, title=titles, author=authors, video_dur=video_durs)
    time.sleep(5)
    
    for i in range(len(video_paths)):
        upload_screen(video_path=video_paths[i],title=titles[i], author=authors[i], video_dur=video_durs[i])
        time.sleep(5)  
        if os.path.exists(video_paths[i]):
            os.remove(video_paths[i])
            with open('complete_uploads.csv', mode='a', newline='') as csv_file: 
                csv_writer = csv.writer(csv_file) #keep track of what videos get uploaded
                csv_writer.writerow([titles[i]])
        driver.refresh()
    
    driver.quit()
    return "Video Uploaded Successfully"

def sign_in(driver, variables, username, password, video_path, title, author, video_dur): 
    success = False  
    while not success:
        try: #Not signed in so keep trying
                WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, variables[1])))
                fieldForm = driver.find_element("xpath", variables[1])
        except:
                driver.quit()
                uploader(video_paths=video_path, titles=title, authors=author, video_durs=video_dur)
        else:
            for i in username:
                    fieldForm.send_keys(i)
                    sleeper()
            fieldForm = driver.find_element("xpath", variables[2])
            
            for char in password:
                    fieldForm.send_keys(char)
                    sleeper()
                            
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, variables[3])))
            hidden = driver.find_element(By.CSS_SELECTOR, "div.tiktok-txpjn9-DivIconContainer i svg")
            hidden.click()
            
            sleeper()
            
            button = driver.find_element("xpath", variables[3])
            sleeper()
            button.click()
            
            time.sleep(1.5)
            try:
                exit_puzzle = driver.find_element(By.XPATH, '//*[@id="verify-bar-close"]')
                exit_puzzle.click()
            except Exception: #button not found so successfully signed in first try no puzzle
                pass
            
            time.sleep(1)
            
            button.click()
            
            time.sleep(5)
            
            try: #check if successfully signed in
                if upload_button := driver.find_element(By.XPATH, '//*[@id="app-header"]/div/div[3]/div[1]/a/div'):
                    upload_button.click()
                    success = True
                    break
            except Exception:
                print('element not found')
                driver.refresh()
                pass
        
        
def upload_screen(video_path, title, author, video_dur):
    time.sleep(2)
    pyautogui.click(x=1675, y=106) # Get to upload page
    time.sleep(3)
    pyautogui.click(897,607) #click the file upload button
    time.sleep(2)
    file_uploader(file_path=video_path)
    time.sleep((video_dur / 2) + 1) # give site time to upload the file
    info_and_post(title=title,author=author)
        
def file_uploader(file_path):
    pyautogui.click(238,475) #moves to pt 320, 490 which is the file_write portion of the chrome file open
    sleeper()
    pyautogui.write(file_path)
    sleeper()
    pyautogui.press('enter')

def info_and_post(author,title):
    pyautogui.click(x=783,y=442, clicks=3)
    time.sleep(1)
    pyautogui.press('backspace')
    time.sleep(1)
    pyautogui.write(f'{title.capitalize()} by user: {author.capitalize()} #RedditStories #RedditDaily #Reddit #Stories #ask_reddit')
    time.sleep(2)
    pyautogui.scroll(-1000)
    time.sleep(2)
    pyautogui.click(x=1020, y=456)


#     return True
if __name__ == '__main__':
    uploader(r"C:\Users\Villa\OneDrive\desktop\CS\Reddit-TikTok\completed_videos\Good news - I'm back!.mp4", title='test title', author='aiden', video_dur= 28)
    while True:
        pass
    
    
    