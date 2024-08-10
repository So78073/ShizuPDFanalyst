import sys
import os
import functions as func
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QRadioButton, QGroupBox, QTextEdit,
                             QFileDialog, QCheckBox, QDialog, QMessageBox)


colorText = {
    "alert": "yellow",
    "error": "red",
    "accept": "#00FFFF",

    "obs": "#FF00FF"
}

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Configurando a janela principal
        self.setWindowTitle("@shizu_ankai_netcat   PDF.copyTem.Soft")
        self.setGeometry(100, 100, 600, 400)
        self.setWindowIcon(QIcon("icon.png"))
        self.setStyleSheet("""
            background-color: #2b2b2b; 
            color: #ffffff;
            font-family: Arial, sans-serif;
        """)

        # Diretório de saída padrão
        self.default_output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')
        print(self.default_output_dir)
        if not os.path.exists(self.default_output_dir):
            os.makedirs(self.default_output_dir)
        self.output_path = self.default_output_dir

        # Layout principal
        main_layout = QVBoxLayout()

        # Botão para escolher diretório ou arquivo
        self.choose_button = QPushButton("Escolher diretório ou arquivo")
        self.choose_button.setStyleSheet("""
            background-color: #3c3f41; 
            color: #ffffff; 
            border: 1px solid #555555; 
            padding: 5px;
            font-size: 14px;
        """)
        self.choose_button.clicked.connect(self.choose_file_or_directory)

        # Botão para escolher diretório de saída
        self.output_button = QPushButton("Escolher diretório de saída")
        self.output_button.setStyleSheet("""
            background-color: #3c3f41; 
            color: #ffffff; 
            border: 1px solid #555555; 
            padding: 5px;
            font-size: 14px;
        """)
        self.output_button.clicked.connect(self.choose_output_directory)

        # Botão enviar
        self.send_button = QPushButton("Enviar")
        self.send_button.setStyleSheet("""
            background-color: #3c3f41; 
            color: #ffffff; 
            border: 1px solid #555555; 
            padding: 5px;
            font-size: 14px;
        """)
        self.send_button.clicked.connect(self.on_send_clicked)

        # Grupo de botões de rádio
        self.radio_group = QGroupBox()
        self.radio_group.setStyleSheet("border: none;")
        radio_layout = QHBoxLayout()
        self.radio_dir = QRadioButton("Diretório")
        self.radio_dir.setEnabled(False)  
        self.radio_file = QRadioButton("Arquivo")
        self.radio_dir.setStyleSheet("color: #ffffff; font-size: 14px;")
        self.radio_file.setStyleSheet("color: #ffffff; font-size: 14px;")
        self.radio_file.setChecked(True)  # Marcar "arquivo" por padrão
        self.radio_dir.toggled.connect(self.update_choose_button_text)
        self.radio_file.toggled.connect(self.update_choose_button_text)
        radio_layout.addWidget(self.radio_dir)
        radio_layout.addWidget(self.radio_file)
        self.radio_group.setLayout(radio_layout)
        self.radio_dir.setEnabled(False)

        # Campo de texto para debug/log (somente leitura)
        self.log_text = QTextEdit()
        self.log_text.setPlaceholderText("debug / ações do app / log")
        self.log_text.setStyleSheet("""
            background-color: #3c3f41; 
            color: #ffffff; 
            border: 1px solid #555555; 
            font-size: 14px;
        """)
        self.log_text.setReadOnly(True)

        # Grupo de checkboxes para habilitar funções
        self.function_group = QGroupBox()
        self.function_group.setStyleSheet("border: none;")
        function_layout = QHBoxLayout()
        self.checkbox_func1 = QCheckBox("Contar P/B ou Color")
        self.checkbox_func2 = QCheckBox("'/, de cor do pdf ")
        self.checkbox_func4 = QCheckBox("Separar para analisar")
        self.checkbox_func1.setStyleSheet("color: #ffffff; font-size: 14px;")
        self.checkbox_func2.setStyleSheet("color: #ffffff; font-size: 14px;")
        self.checkbox_func4.setStyleSheet("color: #ffffff; font-size: 14px;")

        self.checkbox_func1.setChecked(True)
        self.checkbox_func2.setChecked(True)
        self.checkbox_func4.setChecked(True)
        
        self.checkbox_func1.toggled.connect(self.update_checkbox_color)
        self.checkbox_func2.toggled.connect(self.update_checkbox_color)
        self.checkbox_func4.toggled.connect(self.update_checkbox_color)
        self.checkbox_func4.stateChanged.connect(self.toggle_additional_options)
        function_layout.addWidget(self.checkbox_func1)
        function_layout.addWidget(self.checkbox_func2)
        function_layout.addWidget(self.checkbox_func4)
        self.function_group.setLayout(function_layout)

        # Novas opções para a quarta função
        self.additional_group = QGroupBox()
        self.additional_group.setStyleSheet("border: none;")
        additional_layout = QHBoxLayout()
        self.checkbox_additional1 = QCheckBox("Separar Coloridas")
        self.checkbox_additional2 = QCheckBox("Separar Preto e Branco")
        self.checkbox_additional1.setStyleSheet("color: #ffffff; font-size: 14px;")
        self.checkbox_additional2.setStyleSheet("color: #ffffff; font-size: 14px;")
        self.checkbox_additional1.setChecked(True)  # Marcar uma por padrão
        self.checkbox_additional1.stateChanged.connect(self.ensure_at_least_one_checked)
        self.checkbox_additional2.stateChanged.connect(self.ensure_at_least_one_checked)
        additional_layout.addWidget(self.checkbox_additional1)
        additional_layout.addWidget(self.checkbox_additional2)
        self.additional_group.setLayout(additional_layout)
        self.additional_group.setVisible(False)  # Inicialmente invisível

        # Adicionando widgets ao layout principal
        main_layout.addWidget(self.choose_button)
        main_layout.addWidget(self.output_button)  # Adiciona o botão de escolha do diretório de saída
        main_layout.addWidget(self.radio_group)
        main_layout.addWidget(self.log_text)
        main_layout.addWidget(self.function_group)
        main_layout.addWidget(self.additional_group)
        main_layout.addWidget(self.send_button)  # Move o botão de envio para o final

        self.setLayout(main_layout)

        # Variável para armazenar o caminho do diretório ou arquivo escolhido
        self.selected_path = ""

    def choose_file_or_directory(self):
        if self.radio_dir.isChecked():
            directory = QFileDialog.getExistingDirectory(self, "Escolher Diretório")
            if directory:
                self.selected_path = directory
                self.update_log(f"Diretório escolhido: {directory}", "alert")

        elif self.radio_file.isChecked():
            file, _ = QFileDialog.getOpenFileName(self, "Escolher Arquivo")
            if file:
                self.selected_path = file
                self.update_log(f"Arquivo escolhido: {file}", "alert")

    def choose_output_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Escolher Diretório de Saída", self.default_output_dir)
        if directory:
            self.output_path = directory
            self.update_log(f"Diretório de saída escolhido: {directory}", "alert")

    def update_choose_button_text(self):
        if self.radio_dir.isChecked():
            self.choose_button.setText("Escolher diretório")
        elif self.radio_file.isChecked():
            self.choose_button.setText("Escolher arquivo")

    def toggle_additional_options(self, state):
        if state == 2:  # Se a checkbox_func4 estiver marcada
            self.additional_group.setVisible(True)
        else:
            self.additional_group.setVisible(False)

    def ensure_at_least_one_checked(self, state):
        if not self.checkbox_additional1.isChecked() and not self.checkbox_additional2.isChecked():
            # Se nenhuma das opções estiver marcada, marcar uma delas
            self.checkbox_additional1.setChecked(True)

    def update_checkbox_color(self):
        def get_checkbox_color(checkbox):
            return "#00aaff" if checkbox.isChecked() else "#ffffff"

        self.checkbox_func1.setStyleSheet(f"color: {get_checkbox_color(self.checkbox_func1)}; font-size: 14px;")
        self.checkbox_func2.setStyleSheet(f"color: {get_checkbox_color(self.checkbox_func2)}; font-size: 14px;")

        self.checkbox_func4.setStyleSheet(f"color: {get_checkbox_color(self.checkbox_func4)}; font-size: 14px;")

    def format_log_message(self, message, color_key):
        color = colorText.get(color_key, "#ffffff")
        return f'<span style="color: {color};">{message}</span>'

    def show_progress_message(self, message):
        self.log_text.append(self.format_log_message(message, "alert"))
        QApplication.processEvents()  # Atualiza a interface do usuário


    def on_send_clicked(self):
        if not self.selected_path:
            self.update_log("Nenhum diretório ou arquivo escolhido.", "error")
            return

        # Determinar o modo com base nos checkboxes
        mode = (self.checkbox_additional1.isChecked(), self.checkbox_additional2.isChecked())

        # Mostrar mensagem de progresso
        self.show_progress_message(f"<span style='color: {colorText['obs']};'>Iniciando análise...\nO Software não travou, estamos apenas analizando seu arquivo ^^ se estiver demorando muito é por que o arquivo é bem grande .</span>")

        # Executar a função principal com os parâmetros corretos
        try:
            mainFunction = func.main(
                threshold=10, 
                pdf_path=self.selected_path,  # Use o caminho selecionado
                output_pdf_path_color=os.path.join(self.output_path, "comCor.pdf"),
                output_pdf_path_bw=os.path.join(self.output_path, "semCor.pdf"),
                mode=mode,
                mods=(self.checkbox_func1.isChecked(), self.checkbox_func2.isChecked(), self.checkbox_func4.isChecked())
            )


            self.log_text.append(f'''<span style="color: {colorText['accept']};">
Paginas coloridas: {str(mainFunction['analyze_pdf'][0])}<br>
Paginas P/B: {str(mainFunction['analyze_pdf'][1])}<br><br>
Paginas Geradas pelo app: {str(mainFunction['create_pdf_with_color_pages'])} ( parta output padrão pelo software)<br><br>
Porcentagem de cor: {str(mainFunction['analyze_pdf_colors'])}
</span>''')



            self.show_progress_message(f"<span style='color: {colorText['obs']};>Análise concluída.<>/span")
        except Exception as e:
            self.update_log(f"Ocorreu um erro: {e}", "error")


    def update_log(self, message, color_key="white"):
        formatted_message = self.format_log_message(message, color_key)
        self.log_text.append(formatted_message)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
