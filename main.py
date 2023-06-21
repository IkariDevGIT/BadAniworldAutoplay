import contextlib
import os
from datetime import datetime
import re
import sys
import threading
import time
import tkinter as tk

import wget
from selenium import webdriver
from selenium.webdriver.common.by import By


def login(passw, user):
    driver.get("https://aniworld.to/login")
    passw_box = driver.find_element(By.NAME, "password")
    passw_box.send_keys(passw)
    user_box = driver.find_element(By.NAME, "email")
    user_box.send_keys(user)
    driver.find_element(By.XPATH, '//input[@value="Einloggen"]').click()


terminate_flag = False
auto_next_episode = True
auto_fullscreen = True
auto_play = True


def gui():
    global auto_next_episode, auto_fullscreen, auto_play

    def auto_next_episode_d():
        global auto_next_episode
        auto_next_episode = auto_next_episode_v.get()
        print(f"auto_next_episode set to {auto_next_episode}!")

    def auto_fullscreen_d():
        global auto_fullscreen
        auto_fullscreen = auto_fullscreen_v.get()
        print(f"auto_fullscreen set to {auto_fullscreen}!")

    def auto_play_d():
        global auto_play
        auto_play = auto_play_v.get()
        print(f"auto_play set to {auto_play}!")

    def on_window_close():
        global terminate_flag
        root.destroy()
        terminate_flag = True

    # Create the main window
    root = tk.Tk()
    root.title("GUI")
    root.protocol("WM_DELETE_WINDOW", on_window_close)

    version = tk.Label(root,
                       text='by IkariDev - v0.1-prototype')
    Label_middle = tk.Label(root,
                            text='If you want anything of this to work, do NOT select another hoster than doodstream! Also dont close the browser, to close the program right, close this window OR the console window!')

    Label_middle.pack(pady=10)
    version.pack(pady=10)
    # Create the checkbox

    auto_next_episode_v = tk.BooleanVar()
    checkbox = tk.Checkbutton(root, text="Auto-load next episode", variable=auto_next_episode_v, command=auto_next_episode_d)
    checkbox.pack(pady=10)
    checkbox.select()

    auto_fullscreen_v = tk.BooleanVar()
    checkbox2 = tk.Checkbutton(root, text="Auto fullscreen", variable=auto_fullscreen_v, command=auto_fullscreen_d)
    checkbox2.pack(pady=10)
    checkbox2.select()

    auto_play_v = tk.BooleanVar()
    checkbox3 = tk.Checkbutton(root, text="Auto play", variable=auto_play_v, command=auto_play_d)
    checkbox3.pack(pady=10)
    checkbox3.select()

    auto_fullscreen_d()
    auto_next_episode_d()
    auto_play_d()

    # Run the GUI event loop
    root.mainloop()


tmpvar = True


def main(driver):
    while True:
        global terminate_flag, urlold, tmpvar, new_url_s, auto_next_episode, auto_fullscreen, auto_play, episodes
        if "/anime/stream" in str(driver.current_url) and "/episode-" in str(driver.current_url):
            if tmpvar or driver.current_url != urlold:
                time.sleep(0.5)
                try:
                    button = driver.find_element(By.XPATH,
                                                 '//h4[text()="Doodstream"]/parent::a')
                except:
                    pass
                else:
                    driver.execute_script("arguments[0].click();", button)
                    tmpvar = False

                time.sleep(1.2)
                try:
                    driver.executeScript("return document.getElementsByID('checkresume_div')[0].remove();");
                    #bahh = driver.find_element(By.ID, 'checkresume_div')
                except Exception as E:
                    pass

                try:
                    # Find the outer iframe element
                    iframe = driver.find_element(By.CSS_SELECTOR, 'div.inSiteWebStream iframe')

                    # Switch to the inner iframe
                    driver.switch_to.frame(iframe)
                    button2 = driver.find_element(By.XPATH, '//button[@title="Play Video"]')
                except Exception as E:
                    print(E)
                else:
                    if auto_play:
                        button2.click()
                    if auto_fullscreen:
                        time.sleep(0.4)
                        #driver.find_element(By.XPATH, '//button[@title="Fullscreen"]').click()
                        #driver.find_element(By.CLASS_NAME, 'vjs-fullscreen-control vjs-control vjs-button').click()
                        driver.find_element(By.CSS_SELECTOR, '.vjs-fullscreen-control').click()
                        time.sleep(0.2)
                    driver.switch_to.default_content()
                    time.sleep(1)

                # Find all the <ul> elements within the <div>
                ul_elements = driver.find_elements(By.XPATH, "//div[@id='stream']/ul")
                # Find the <ul> element with the most <li> elements
                max_ul_element = max(ul_elements, key=lambda ul: len(ul.find_elements(By.TAG_NAME, 'li')))
                # Get the count of <li> elements within the <ul> with the most elements
                episodes = len(max_ul_element.find_elements(By.TAG_NAME, 'li')) - 1

            try:
                # iframe = driver.find_element(By.CSS_SELECTOR, 'div.inSiteWebStream iframe')
                # iframe = driver.find_element(By.CSS_SELECTOR, 'div.inSiteWebStream iframe')
                iframes = driver.find_elements(By.TAG_NAME, 'iframe')

                if len(iframes) > 0:
                    # Select the first iframe
                    first_iframe = iframes[0]
                    # Switch to the first iframe
                    driver.switch_to.frame(first_iframe)

                # Switch to the inner iframe
                # driver.switch_to.frame(iframe)

                video_player = driver.find_element(By.CLASS_NAME, 'vjs-remaining-time-display').get_attribute(
                    'innerHTML')

                # Get the total video length
                total_length = driver.execute_script("return arguments[0].duration;", video_player)

                # remaining_time = driver.execute_script(
                # "return arguments[0].duration - arguments[0].currentTime;",
                # video_player)
                # print(str(remaining_time))

                time_str = video_player

                time_obj = datetime.strptime(time_str, "%M:%S")
                total_seconds = time_obj.minute * 60 + time_obj.second

                print(f"Time in seconds: {total_seconds}")

                if int(round(total_seconds)) <= 3:
                    match = re.search(r'/episode-(\d+)', str(driver.current_url))
                    if match:
                        number = int(match.group(1))
                        modified_url = re.sub(r'/episode-\d+', '', str(driver.current_url)) + "/episode-"
                        if episodes < number+1:
                            new_url_s = modified_url + str(1)
                        else:
                            new_url_s = modified_url + str(number + 1)
                    else:
                        print("No number found in the URL.")
                driver.switch_to.default_content()
            except Exception as e:
                print("asas: " + str(e))

                # Click the button

                # terminate_flag = True
        # try:
        # WebDriverWait(driver, 1).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH,
        # "//iframe[@src='/redirect/*']")))
        # driver.find_element(By.XPATH, '//button[@aria-label="Play"]').click()
        # except Exception as err:
        # print(f"An error was handled {str(err)}")
        driver.switch_to.default_content()
        urlold = driver.current_url
        #print("thread is running!")
        with contextlib.suppress(NameError):
            if urlold != new_url_s and auto_next_episode:
                driver.get(new_url_s)
        time.sleep(0.1)
        if terminate_flag:
            driver.quit()
            sys.exit()


if __name__ == '__main__':
    if not os.path.exists("./config.txt"):
        with open("./config.txt", 'w') as file:
            print("it seems you are using this program the first time, please write your in your aniworld credentials into the new file called config.txt. Then restart this program!")
            print("""
            Please write them like this:
            Email
            Password
            """)
            file.write("Email here!\n")
            file.write("Password here!")
            file.close()
            input("(press enter to close...)")
            sys.exit()
    else:
        with open("./config.txt", 'r') as file:
            content = file.readlines()
            user = content[0]
            passw = content[1]
    driver = webdriver.Firefox()
    driver.get(
        "https://onelineplayer.com/player.html?autoplay=true&autopause=false&muted=true&loop=true&url=https%3A%2F%2Ffreefrontend.com%2Fassets%2Fimg%2Fcss-spinners%2F2023-leaky-preloader.mp4&poster=&time=false&progressBar=false&overlay=true&muteButton=false&fullscreenButton=false&style=light&quality=auto&playButton=false")
    url = "https://addons.mozilla.org/firefox/downloads/file/4121906/ublock_origin-1.50.0.xpi"
    wget.download(url, './ublock.xpi')
    driver.install_addon('./ublock.xpi', temporary=True)
    time.sleep(1)
    login(passw, user)
    main = threading.Thread(target=main, args=[driver])
    main.start()
    gui()


