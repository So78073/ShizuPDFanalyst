import sys
import os
import functions as func
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QRadioButton, QGroupBox, QTextEdit,
                             QFileDialog, QCheckBox, QDialog, QMessageBox)

threshold = 10

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Configurando a janela principal
        self.setWindowTitle("Nome do App")
        self.setGeometry(100, 100, 600, 400)
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
        self.radio_file = QRadioButton("Arquivo")
        self.radio_dir.setStyleSheet("color: #ffffff; font-size: 14px;")
        self.radio_file.setStyleSheet("color: #ffffff; font-size: 14px;")
        self.radio_file.setChecked(True)  # Marcar "arquivo" por padrão
        self.radio_dir.toggled.connect(self.update_choose_button_text)
        self.radio_file.toggled.connect(self.update_choose_button_text)
        radio_layout.addWidget(self.radio_dir)
        radio_layout.addWidget(self.radio_file)
        self.radio_group.setLayout(radio_layout)

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
        self.checkbox_func2 = QCheckBox("Nenhuma")
        self.checkbox_func3 = QCheckBox("Nenhuma")
        self.checkbox_func4 = QCheckBox("Separar para analisar")
        self.checkbox_func1.setStyleSheet("color: #ffffff; font-size: 14px;")
        self.checkbox_func2.setStyleSheet("color: #ffffff; font-size: 14px;")
        self.checkbox_func3.setStyleSheet("color: #ffffff; font-size: 14px;")
        self.checkbox_func4.setStyleSheet("color: #ffffff; font-size: 14px;")
        self.checkbox_func1.toggled.connect(self.update_checkbox_color)
        self.checkbox_func2.toggled.connect(self.update_checkbox_color)
        self.checkbox_func3.toggled.connect(self.update_checkbox_color)
        self.checkbox_func4.toggled.connect(self.update_checkbox_color)
        self.checkbox_func4.stateChanged.connect(self.toggle_additional_options)
        function_layout.addWidget(self.checkbox_func1)
        function_layout.addWidget(self.checkbox_func2)
        function_layout.addWidget(self.checkbox_func3)
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
                self.log_text.append(f"Diretório escolhido: {directory}")

        elif self.radio_file.isChecked():
            file, _ = QFileDialog.getOpenFileName(self, "Escolher Arquivo")
            if file:
                self.selected_path = file
                self.log_text.append(f"Arquivo escolhido: {file}")

    def choose_output_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Escolher Diretório de Saída", self.default_output_dir)
        if directory:
            self.output_path = directory
            self.log_text.append(f"Diretório de saída escolhido: {directory}")

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
        self.checkbox_func3.setStyleSheet(f"color: {get_checkbox_color(self.checkbox_func3)}; font-size: 14px;")
        self.checkbox_func4.setStyleSheet(f"color: {get_checkbox_color(self.checkbox_func4)}; font-size: 14px;")

    def analyze_pdf(self, threshold):
        # Função que será executada
        result = func.analyze_pdf(self.selected_path, threshold)
        # Atualize a interface do usuário com os resultados
        self.update_log(result)

    def create_pdf_with_color_pages(self, output_path_color, output_path_bw, mode=(True, False)):
        func.create_pdf_with_color_pages(self.selected_path, output_path_color, output_path_bw, mode)
        self.update_log(f"PDF com páginas coloridas e P/B criado em: {output_path_color}, {output_path_bw}")

    def analyze_for_printing(self, input_path, output_path_color, output_path_bw, separate_color, separate_bw):
        # Funções de análise adicionais

        # -- AQUII --
        if self.checkbox_func2.isChecked():
            func.some_other_function_1(input_path, output_path_color, separate_color)
        if self.checkbox_func3.isChecked():
            func.some_other_function_2(input_path, output_path_bw, separate_bw)
        if self.checkbox_func4.isChecked():
            self.create_pdf_with_color_pages(output_path_color, output_path_bw, (separate_color, separate_bw))

    def on_send_clicked(self):
        if not self.selected_path:
            QMessageBox.warning(self, "Atenção", "Por favor, escolha um diretório ou arquivo.")
            return

        if not self.output_path:
            QMessageBox.warning(self, "Atenção", "Por favor, escolha um diretório de saída.")
            return

        # Verifique qual função foi selecionada e chame-a
        if self.checkbox_func1.isChecked():
            self.analyze_pdf(threshold)

        if self.checkbox_func4.isChecked():
            separate_color = self.checkbox_additional1.isChecked()
            separate_bw = self.checkbox_additional2.isChecked()
            output_path_color = os.path.join(self.output_path, 'coloridas.pdf')
            output_path_bw = os.path.join(self.output_path, 'preto_e_branco.pdf')
            
            self.analyze_for_printing(self.selected_path, output_path_color, output_path_bw, separate_color, separate_bw)

        self.log_text.append("Análise concluída.")

    def update_log(self, message):
        self.log_text.append(message)

    def show_message(self, title, message):
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setStyleSheet("background-color: #3c3f41; color: #ffffff;")
        msg.exec_()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
