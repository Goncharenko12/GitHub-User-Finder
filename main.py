import tkinter as tk
from tkinter import messagebox
import json
import os

# Проверка и импорт requests
try:
    import requests
except ImportError:
    import sys
    import subprocess
    answer = messagebox.askyesno("Зависимость не установлена", "Модуль 'requests' не найден. Установить его сейчас?")
    if answer:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
        import requests
    else:
        messagebox.showerror("Ошибка", "Без модуля 'requests' программа не сможет работать. Установите его и попробуйте снова.")
        exit()

class GitHubUserFinder:
    def __init__(self, master):
        self.master = master
        self.master.title("GitHub User Finder")

        # Загрузка избранных
        self.favorites = []
        self.load_favorites()

        # Создаем интерфейс
        self.create_widgets()

        # Переменная для хранения текущего искомого пользователя
        self.current_user_data = None

    def create_widgets(self):
        # Поле поиска
        tk.Label(self.master, text="Введите логин GitHub:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.search_entry = tk.Entry(self.master, width=30)
        self.search_entry.grid(row=0, column=1, padx=5, pady=5)

        # Кнопка поиска
        self.search_button = tk.Button(self.master, text="Найти", command=self.search_user)
        self.search_button.grid(row=0, column=2, padx=5, pady=5)

        # Результаты поиска
        tk.Label(self.master, text="Результат:").grid(row=1, column=0, padx=5, pady=5, sticky='nw')
        self.results_text = tk.Text(self.master, height=7, width=50, state='disabled')
        self.results_text.grid(row=1, column=1, columnspan=2, padx=5, pady=5)

        # Кнопка добавить в избранное
        self.fav_button = tk.Button(self.master, text="Добавить в избранное", command=self.add_to_favorites)
        self.fav_button.grid(row=2, column=1, pady=5)
        self.fav_button.config(state='disabled')  # активируем по необходимости

        # Кнопка показать избранных
        self.show_fav_button = tk.Button(self.master, text="Показать избранных", command=self.show_favorites)
        self.show_fav_button.grid(row=2, column=2, pady=5)

    def load_favorites(self):
        if os.path.exists("favorites.json"):
            try:
                with open("favorites.json", "r", encoding="utf-8") as f:
                    self.favorites = json.load(f)
            except json.JSONDecodeError:
                self.favorites = []
        else:
            self.favorites = []

    def save_favorites(self):
        with open("favorites.json", "w", encoding="utf-8") as f:
            json.dump(self.favorites, f, ensure_ascii=False, indent=4)

    def search_user(self):
        username = self.search_entry.get().strip()
        if not username:
            messagebox.showerror("Ошибка", "Поле поиска не должно быть пустым.")
            return
        url = f"https://api.github.com/users/{username}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                self.current_user_data = response.json()
                self.display_user_info(self.current_user_data)
                self.fav_button.config(state='normal')
            elif response.status_code == 404:
                messagebox.showerror("Ошибка", "Пользователь не найден.")
                self.clear_results()
                self.fav_button.config(state='disabled')
            else:
                messagebox.showerror("Ошибка", f"Ошибка сервера: {response.status_code}")
                self.clear_results()
                self.fav_button.config(state='disabled')
        except requests.RequestException as e:
            messagebox.showerror("Ошибка", f"Ошибка соединения: {e}")
            self.clear_results()
            self.fav_button.config(state='disabled')

    def display_user_info(self, user_data):
        self.results_text.config(state='normal')
        self.results_text.delete(1.0, tk.END)
        info = (
            f"Имя: {user_data.get('name', 'N/A')}\n"
            f"Логин: {user_data.get('login', 'N/A')}\n"
            f"URL: {user_data.get('html_url', 'N/A')}\n"
            f"Количество репозиториев: {user_data.get('public_repos', 'N/A')}\n"
            f"Количество подписчиков: {user_data.get('followers', 'N/A')}\n"
        )
        self.results_text.insert(tk.END, info)
        self.results_text.config(state='disabled')

    def clear_results(self):
        self.results_text.config(state='normal')
        self.results_text.delete(1.0, tk.END)
        self.results_text.config(state='disabled')

    def add_to_favorites(self):
        if self.current_user_data:
            login = self.current_user_data.get('login')
            if login in self.favorites:
                messagebox.showinfo("Информация", "Этот пользователь уже в избранных.")
            else:
                self.favorites.append(login)
                self.save_favorites()
                messagebox.showinfo("Готово", f"Пользователь {login} добавлен в избранное.")

    def show_favorites(self):
        fav_str = "\n".join(self.favorites) if self.favorites else "Нет избранных пользователей."
        messagebox.showinfo("Избранные пользователи", fav_str)

if __name__ == "__main__":
    root = tk.Tk()
    app = GitHubUserFinder(root)
    root.mainloop()