from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
from kivy.uix.gridlayout import GridLayout
from datetime import datetime
from kivy.properties import ObjectProperty
from kivy.uix.image import Image
from kivy.uix.widget import Widget
import csv

class TransactionWidget(BoxLayout):
    def __init__(self, date, name, amount, is_income=True, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(40)

        color = (0, 0.3, 0, 1) if is_income else (0.3, 0, 0, 1)

        # Establecer el color de fondo del widget de transacción
        with self.canvas.before:
            Color(*color)
            self.rect = Rectangle(size=self.size, pos=self.pos)

        self.bind(size=self.update_rect, pos=self.update_rect)

        date_label = Label(text=date, font_size='14sp', size_hint_x=0.2)
        name_label = Label(text=name, font_size='16sp', size_hint_x=0.5)
        amount_label = Label(text=f"${amount}", font_size='16sp', size_hint_x=0.3)

        self.add_widget(date_label)
        self.add_widget(name_label)
        self.add_widget(amount_label)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class MonthButton(Button):
    def __init__(self, month_year, finances_app, **kwargs):
        super().__init__(**kwargs)
        self.text = month_year
        self.month_year = month_year
        self.finances_app = finances_app

        self.size_hint_y = None
        self.height = dp(30)

        # Establecer el color de fondo del botón del mes
        self.background_color = (0.4, 0.4, 0.8, 1)

        self.bind(on_press=self.confirm_delete_month)

    def confirm_delete_month(self, instance):
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        popup_title = Label(text="Borrar mes?", font_size='20sp', size_hint_y=None, height=dp(50), halign='center')
        popup_title.bind(size=popup_title.setter('text_size'))
        content.add_widget(popup_title)

        confirm_button = Button(text="Confirmar", background_color=(0, 1, 0, 1), font_size='16sp', size_hint_y=None, height=dp(50))
        confirm_button.bind(on_press=lambda instance: self.delete_month(instance))
        cancel_button = Button(text="Cancelar", background_color=(1, 0, 0, 1), font_size='16sp', size_hint_y=None, height=dp(50))
        cancel_button.bind(on_press=lambda instance: self.dismiss_popup(instance))

        content.add_widget(confirm_button)
        content.add_widget(cancel_button)

        self.popup = Popup(title=" ", content=content, size_hint=(None, None), size=(dp(300), dp(200)), background_color=(0, 0, 1, 1), separator_color=(0, 0, 0, 0))
        self.popup.open()

    def delete_month(self, instance):
        self.finances_app.remove_month(self.month_year)
        self.dismiss_popup(instance)

    def dismiss_popup(self, instance):
        self.popup.dismiss()

class FinancesApp(App):
    rect = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.total_money = 0
        self.transactions = {}
        self.transactions_layout = None
        self.money_label = Label(text="", font_size='20sp')
        self.load_transactions()

    def build(self):
        root_layout = BoxLayout(orientation='vertical')

        # Cargamos la imagen para usar como fondo
        image = Image(source='image.jpg')
        # Establecemos una imagen de fondo
        with root_layout.canvas.before:
            self.rect = Rectangle(texture=image.texture, size=root_layout.size, pos=root_layout.pos)
        # Vinculamos la propiedad rect para que se actualice automáticamente
        root_layout.bind(size=self.update_rect, pos=self.update_rect)

        # Layout para el texto de "Dinero disponible"
        money_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))

        # Carga la imagen del logo
        icon = Image(source='logoapp2.png', size=(dp(50), dp(50)), size_hint=(None, None))

        # Añade el icono y el texto "Dinero disponible" al layout
        money_layout.add_widget(icon)
        money_layout.add_widget(Widget(size_hint_x=None, width=dp(5)))  # Espacio entre el icono y el texto
        money_layout.add_widget(self.money_label)

        root_layout.add_widget(money_layout)

        # Layout para el historial de transacciones
        transactions_layout = BoxLayout(orientation='vertical')

        self.transactions_scrollview = ScrollView()
        self.transactions_layout = GridLayout(cols=1, spacing=dp(5), size_hint_y=None)
        self.transactions_layout.bind(minimum_height=self.transactions_layout.setter('height'))
        self.transactions_scrollview.add_widget(self.transactions_layout)
        transactions_layout.add_widget(self.transactions_scrollview)

        # Layout para los botones de agregar ganancia y gasto
        buttons_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        add_income_button = Button(text='+', background_color=(0, 1, 0, 1), font_size='20sp')
        add_income_button.bind(on_press=self.add_income_popup)
        buttons_layout.add_widget(add_income_button)

        add_expense_button = Button(text='-', background_color=(1, 0, 0, 1), font_size='20sp')
        add_expense_button.bind(on_press=self.add_expense_popup)
        buttons_layout.add_widget(add_expense_button)

        transactions_layout.add_widget(buttons_layout)
        root_layout.add_widget(transactions_layout)

        self.add_loaded_transactions()

        return root_layout
    
    def update_rect(self, *args):
        self.rect.size = self.root.size
        self.rect.pos = self.root.pos

    def update_money_label(self):
        self.money_label.text = f"Dinero disponible: ${self.total_money}"

    def add_income_popup(self, instance):
        popup_content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))  # Añadimos espaciado
        popup_title = Label(text="Agregar ganancia", font_size='20sp', size_hint_y=None, height=dp(50), halign='center')
        popup_title.bind(size=popup_title.setter('text_size'))
        popup_content.add_widget(popup_title)

        name_input = TextInput(hint_text="Nombre de la ganancia", font_size='16sp', size_hint_y=None, height=dp(40), halign='center')
        money_input = TextInput(hint_text="Cantidad ganada", font_size='16sp', size_hint_y=None, height=dp(40), halign='center')
        add_button = Button(text="Agregar", background_color=(0, 0.8, 0, 1), font_size='16sp', size_hint_y=None, height=dp(50))
        add_button.bind(on_press=lambda instance: self.add_income(name_input.text, money_input.text, popup))

        popup_content.add_widget(name_input)
        popup_content.add_widget(money_input)
        popup_content.add_widget(add_button)

        popup = Popup(title=" ", content=popup_content, size_hint=(None, None), size=(dp(300), dp(250)), background_color=(0, 1, 1, 1), separator_color=(0, 0, 0, 0))  # Añadimos el color del separador
        popup.open()

    def add_income(self, name, amount, popup):
        try:
            amount = float(amount)
            self.total_money += amount
            self.update_money_label()
            self.add_transaction(name, amount, is_income=True)
            self.save_transactions()
            popup.dismiss()
        except ValueError:
            self.show_error_popup("Introduce un número válido.")

    def add_expense_popup(self, instance):
        popup_content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))  # Añadimos espaciado
        popup_title = Label(text="Agregar gasto", font_size='20sp', size_hint_y=None, height=dp(50), halign='center')
        popup_title.bind(size=popup_title.setter('text_size'))
        popup_content.add_widget(popup_title)

        name_input = TextInput(hint_text="Nombre del gasto", font_size='16sp', size_hint_y=None, height=dp(40), halign='center')
        money_input = TextInput(hint_text="Cantidad gastada", font_size='16sp', size_hint_y=None, height=dp(40), halign='center')
        add_button = Button(text="Reducir", background_color=(1, 0, 0, 1), font_size='16sp', size_hint_y=None, height=dp(50))
        add_button.bind(on_press=lambda instance: self.add_expense(name_input.text, money_input.text, popup))

        popup_content.add_widget(name_input)
        popup_content.add_widget(money_input)
        popup_content.add_widget(add_button)

        popup = Popup(title=" ", content=popup_content, size_hint=(None, None), size=(dp(300), dp(250)), background_color=(1, 0, 0, 1), separator_color=(0, 0, 0, 0))  # Añadimos el color del separador
        popup.open()

    def add_expense(self, name, amount, popup):
        try:
            amount = float(amount)
            self.total_money -= amount
            self.update_money_label()
            self.add_transaction(name, amount, is_income=False)
            self.save_transactions()
            popup.dismiss()
        except ValueError:
            self.show_error_popup("Introduce un número válido.")

    def add_transaction(self, name, amount, is_income=True):
        now = datetime.now()
        date_str = now.strftime("%d/%m/%Y")
        month_year_str = now.strftime("%B %Y")

        if month_year_str not in self.transactions:
            self.transactions[month_year_str] = []

        self.transactions[month_year_str].append((date_str, name, amount, is_income))

        if self.transactions_layout:
            self.transactions_layout.clear_widgets()
            for month_year, transactions in self.transactions.items():
                month_year_button = MonthButton(month_year, finances_app=self)
                self.transactions_layout.add_widget(month_year_button)

                for transaction in transactions:
                    date, name, amount, is_income = transaction
                    transaction_widget = TransactionWidget(date, name, amount, is_income)
                    self.transactions_layout.add_widget(transaction_widget)

    def add_loaded_transactions(self):
        if self.transactions_layout:
            for month_year, transactions in self.transactions.items():
                month_year_button = MonthButton(month_year, finances_app=self)
                self.transactions_layout.add_widget(month_year_button)

                for transaction in transactions:
                    date, name, amount, is_income = transaction
                    transaction_widget = TransactionWidget(date, name, amount, is_income)
                    self.transactions_layout.add_widget(transaction_widget)

        self.total_money = sum(amount if is_income else -amount for transactions in self.transactions.values() for _, _, amount, is_income in transactions)
        self.update_money_label()

    def remove_month(self, month_year):
        if month_year in self.transactions:
            del self.transactions[month_year]
            self.transactions_layout.clear_widgets()
            self.add_loaded_transactions()
            self.save_transactions()

    def save_transactions(self):
        with open('transactions.csv', 'w', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            for month_year, transactions in self.transactions.items():
                for transaction in transactions:
                    csvwriter.writerow([month_year] + list(transaction))

    def load_transactions(self):
        try:
            with open('transactions.csv', newline='') as csvfile:
                csvreader = csv.reader(csvfile)
                for row in csvreader:
                    month_year, date, name, amount, is_income = row
                    if month_year not in self.transactions:
                        self.transactions[month_year] = []
                    if is_income == 'True':
                        is_income = True
                    else:
                        is_income = False
                    self.transactions[month_year].append((date, name, float(amount), is_income))
        except FileNotFoundError:
            pass

    def show_error_popup(self, message):
        popup = Popup(title="Error", content=Label(text=message, font_size='16sp'), size_hint=(None, None), size=(dp(200), dp(100)))
        popup.open()

if __name__ == '__main__':
    FinancesApp().run()