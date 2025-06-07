import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import sys
import os
from datetime import datetime, timedelta
import random
import string
import names
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import undetected_chromedriver as uc
from fake_useragent import UserAgent
import threading

class InstallDependencies:
    @staticmethod
    def check_and_install():
        required_packages = {
            'selenium': '4.0.0',
            'undetected-chromedriver': '3.5.0',
            'fake-useragent': '1.1.3',
            'names': '0.3.0'
        }
        
        installed_packages = {}
        try:
            from pip._internal.operations import freeze
            installed_packages = {p.split('==')[0].lower(): p.split('==')[1] if '==' in p else 'latest' 
                                for p in freeze.freeze()}
        except:
            pass
        
        missing = []
        outdated = []
        
        for pkg, version in required_packages.items():
            if pkg not in installed_packages:
                missing.append(f"{pkg}=={version}")
            elif installed_packages[pkg] != version:
                outdated.append(f"{pkg}=={version}")
        
        if missing or outdated:
            try:
                import pip
                if missing:
                    pip.main(['install'] + missing)
                if outdated:
                    pip.main(['install', '--upgrade'] + outdated)
                return True
            except:
                return False
        return True

class RobloxAccountGenerator:
    def __init__(self):
        self.user_agents = UserAgent()
        self.driver = None
        self.human_like_delays = (0.2, 0.8)
        self.last_generation = None
        self.cooldown_hours = 24

    def init_driver(self):
        if self.driver is None:
            options = uc.ChromeOptions()
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument(f'user-agent={self.user_agents.random}')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-popup-blocking')
            options.add_argument('--disable-notifications')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            self.driver = uc.Chrome(options=options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    def generate_credentials(self):
        username = f"{names.get_first_name()}{random.choice(['', '_', '.'])}{random.choice([names.get_last_name(), str(random.randint(100, 9999))])}".lower()
        
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        password = ''.join(random.sample(chars, 16))
        
        year = datetime.now().year - random.randint(13, 25)
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        birthdate = f"{month:02d}/{day:02d}/{year}"
        
        return username, password, birthdate

    def human_like_typing(self, element, text):
        actions = ActionChains(self.driver)
        for char in text:
            actions.send_keys_to_element(element, char)
            actions.perform()
            time.sleep(random.uniform(*self.human_like_delays))

    def create_account(self, callback):
        def generation_thread():
            try:
                if self.last_generation and (datetime.now() - self.last_generation) < timedelta(hours=self.cooldown_hours):
                    callback(None, "Debes esperar 24 horas entre generaciones")
                    return
                
                self.init_driver()
                username, password, birthdate = self.generate_credentials()
                month, day, year = birthdate.split('/')

                self.driver.get("https://www.roblox.com")
                time.sleep(random.uniform(3, 7))

                username_field = WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.ID, "signup-username"))
                )
                self.human_like_typing(username_field, username)

                password_field = self.driver.find_element(By.ID, "signup-password")
                self.human_like_typing(password_field, password)

                birth_fields = {
                    "MonthDropdown": month,
                    "DayDropdown": day,
                    "YearDropdown": year
                }

                for field_id, value in birth_fields.items():
                    dropdown = self.driver.find_element(By.ID, field_id)
                    self.driver.execute_script("arguments[0].scrollIntoView();", dropdown)
                    ActionChains(self.driver).move_to_element(dropdown).pause(
                        random.uniform(0.5, 1.5)).click().perform()
                    
                    option = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, f"//option[@value='{value}']"))
                    )
                    ActionChains(self.driver).move_to_element(option).pause(
                        random.uniform(0.3, 0.7)).click().perform()
                    time.sleep(random.uniform(0.5, 1.5))

                gender = random.choice(["Male", "Female"])
                try:
                    gender_field = self.driver.find_element(By.XPATH, f"//label[contains(text(), '{gender}')]")
                    ActionChains(self.driver).move_to_element(gender_field).pause(
                        random.uniform(0.5, 1.0)).click().perform()
                except:
                    pass

                time.sleep(random.uniform(5, 10))

                submit_button = self.driver.find_element(By.ID, "signup-button")
                self.driver.execute_script("arguments[0].scrollIntoView();", submit_button)
                ActionChains(self.driver).move_to_element(submit_button).pause(
                    random.uniform(0.5, 1.5)).click().perform()

                WebDriverWait(self.driver, 30).until(
                    EC.url_contains("www.roblox.com/home")
                )

                with open("accounts.txt", "a", encoding="utf-8") as f:
                    f.write(f"{datetime.now()}: {username}:{password}:{birthdate}\n")

                self.last_generation = datetime.now()
                callback({
                    "username": username,
                    "password": password,
                    "birthdate": birthdate,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }, None)
                
            except Exception as e:
                callback(None, str(e))
            finally:
                if self.driver:
                    try:
                        self.driver.quit()
                    except:
                        pass
                    self.driver = None

        threading.Thread(target=generation_thread, daemon=True).start()

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Roblox Account Generator")
        self.geometry("600x500")
        self.resizable(False, False)
        self.generator = RobloxAccountGenerator()
        
        self.check_dependencies()
        self.create_widgets()

    def check_dependencies(self):
        if not InstallDependencies.check_and_install():
            messagebox.showerror("Error", "No se pudieron instalar las dependencias requeridas")
            self.destroy()
            sys.exit()

    def create_widgets(self):
        # Header
        header_frame = ttk.Frame(self)
        header_frame.pack(pady=10)
        
        ttk.Label(header_frame, text="Roblox Account Generator", font=('Arial', 16, 'bold')).pack()
        ttk.Label(header_frame, text="Genera cuentas de Roblox automáticamente", font=('Arial', 10)).pack()
        
        # Status Frame
        status_frame = ttk.LabelFrame(self, text="Estado")
        status_frame.pack(pady=10, padx=20, fill='x')
        
        self.status_label = ttk.Label(status_frame, text="Listo para generar una nueva cuenta", foreground='green')
        self.status_label.pack(pady=5)
        
        # Account Info Frame
        info_frame = ttk.LabelFrame(self, text="Información de la Cuenta")
        info_frame.pack(pady=10, padx=20, fill='both', expand=True)
        
        self.account_text = scrolledtext.ScrolledText(info_frame, height=10, wrap=tk.WORD)
        self.account_text.pack(pady=5, padx=5, fill='both', expand=True)
        self.account_text.insert(tk.END, "Aquí aparecerán los datos de la cuenta generada...\n")
        self.account_text.config(state='disabled')
        
        # Button Frame
        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10)
        
        self.generate_btn = ttk.Button(button_frame, text="Generar Cuenta", command=self.generate_account)
        self.generate_btn.pack(side='left', padx=5)
        
        ttk.Button(button_frame, text="Guardar Datos", command=self.save_data).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Salir", command=self.destroy).pack(side='left', padx=5)
        
        # Footer
        footer_frame = ttk.Frame(self)
        footer_frame.pack(pady=10)
        
        ttk.Label(footer_frame, text="© 2023 Roblox Account Generator | Solo para fines educativos", font=('Arial', 8)).pack()

    def generate_account(self):
        self.generate_btn.config(state='disabled')
        self.status_label.config(text="Generando cuenta...", foreground='blue')
        self.update()
        
        def callback(account, error):
            if account:
                self.account_text.config(state='normal')
                self.account_text.delete(1.0, tk.END)
                self.account_text.insert(tk.END, f"✅ Cuenta generada exitosamente!\n\n")
                self.account_text.insert(tk.END, f"🔹 Usuario: {account['username']}\n")
                self.account_text.insert(tk.END, f"🔹 Contraseña: {account['password']}\n")
                self.account_text.insert(tk.END, f"🔹 Fecha de nacimiento: {account['birthdate']}\n")
                self.account_text.insert(tk.END, f"🔹 Generada el: {account['timestamp']}\n\n")
                self.account_text.insert(tk.END, "⚠️ Guarda esta información en un lugar seguro")
                self.account_text.config(state='disabled')
                
                self.status_label.config(text=f"Cuenta generada - Próxima generación disponible en 24 horas", foreground='green')
            else:
                messagebox.showerror("Error", f"No se pudo generar la cuenta:\n{error}")
                self.status_label.config(text="Error al generar cuenta", foreground='red')
            
            self.generate_btn.config(state='normal')
        
        self.generator.create_account(callback)

    def save_data(self):
        try:
            with open('accounts.txt', 'r') as f:
                data = f.read()
            
            with filedialog.asksaveasfile(mode='w', defaultextension=".txt", filetypes=[("Text files", "*.txt")]) as f:
                if f:
                    f.write(data)
                    messagebox.showinfo("Éxito", "Datos guardados correctamente")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron guardar los datos:\n{str(e)}")

if __name__ == "__main__":
    app = Application()
    app.mainloop()