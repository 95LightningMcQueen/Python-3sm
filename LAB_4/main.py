import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
import numpy as np


def knopka_click(symbol):
    tekst = pole_vvoda.get()
    pole_vvoda.delete(0, tk.END)
    pole_vvoda.insert(0, tekst + str(symbol))

def delete_all():
    pole_vvoda.delete(0, tk.END)

def count():
    try:
        vyrazhenie = pole_vvoda.get()
        result = eval(vyrazhenie)
        pole_vvoda.delete(0, tk.END)
        pole_vvoda.insert(0, str(result))
    except Exception:
        messagebox.showerror('Ошибка', 'Некорректное выражение')

def print_grafic():
    try:
        equation = pole_grafika.get()
        x = np.linspace(-10, 10, 400)
        safe_dict = {
            'x': x,
            'sin': np.sin,
            'cos': np.cos,
            'tan': np.tan,
            'sqrt': np.sqrt,
            'exp': np.exp,
            'pi': np.pi
        }
        y = eval(equation, {'__builtins__': None}, safe_dict)
        plt.figure('График функции')
        plt.plot(x, y)
        plt.grid(True)
        plt.axhline(0, color='black', lw=1)
        plt.axvline(0, color='black', lw=1)
        plt.title(f'График: y = {equation}')
        plt.xlabel('x')
        plt.ylabel('y')
        plt.show()
    except Exception as e:
        messagebox.showerror('Ошибка графика', 'Проверьте формулу')
        
okno = tk.Tk()
okno.title('Калькулятор и Графики')
okno.geometry('300x450')
pole_vvoda = tk.Entry(okno, font=('Arial', 14), borderwidth=5, relief='flat', justify='right')
pole_vvoda.grid(row=0, column=0, columnspan=4, padx=10, pady=10)
knopki = [
    '7', '8', '9', '/',
    '4', '5', '6', '*',
    '1', '2', '3', '-',
    '0', 'C', '=', '+'
]
stroka = 1
stolbec = 0

for tekst in knopki:
    if tekst == '=':
        komanda = count
    elif tekst == 'C':
        komanda = delete_all
    else:
        komanda = lambda t=tekst: knopka_click(t)
    tk.Button(okno, text=tekst, width=5, height=2, command=komanda).grid(row=stroka, column=stolbec, padx=2, pady=2)
    stolbec += 1
    if stolbec > 3:
        stolbec = 0
        stroka += 1
        
tk.Label(okno, text='Построение графика: ').grid(row=5, column=0, columnspan=4, pady=(20, 0))
pole_grafika = tk.Entry(okno, font=('Arial', 12), borderwidth=3)
pole_grafika.grid(row=6, column=0, columnspan=4, padx=10, pady=5, sticky='we')
pole_grafika.insert(0, '')

knopka_grafik = tk.Button(okno, text='Построить график', bg='#a1d1a1', command=print_grafic)
knopka_grafik.grid(row=7, column=0, columnspan=4, padx=10, pady=10, sticky='we')

okno.mainloop()
