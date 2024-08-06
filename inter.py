import sys
import os
import threading
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
        self.default_output_dir = os.path.join(os.getcwd(), 'outputs')
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
        self.send_button = QPushButton("enviar")
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
        self.radio_dir = QRadioButton("diretório")
        self.radio_file = QRadioButton("arquivo")
        self.radio_dir.setStyleSheet("color: #ffffff; font-size: 14px;")
        self.radio_file.setStyleSheet("color: #ffffff; font-size: 14px;")
        self.radio_file.setChecked(True)  # Marcar "diretório" por padrão
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
        self.checkbox_func1 = QCheckBox("contar P/B ou Color")
        self.checkbox_func2 = QCheckBox("none")
        self.checkbox_func3 = QCheckBox("none")
        self.checkbox_func4 = QCheckBox("Separar para analizar")
        self.checkbox_func1.setStyleSheet("color: #ffffff; font-size: 14px;")
        self.checkbox_func2.setStyleSheet("color: #ffffff; font-size: 14px;")
        self.checkbox_func3.setStyleSheet("color: #ffffff; font-size: 14px;")
        self.checkbox_func4.setStyleSheet("color: #ffffff; font-size: 14px;")
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
        self.checkbox_additional2 = QCheckBox("Separar Preto e branco")
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
        main_layout.addWidget(self.send_button)
        main_layout.addWidget(self.radio_group)
        main_layout.addWidget(self.log_text)
        main_layout.addWidget(self.function_group)
        main_layout.addWidget(self.additional_group)

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

    def analyze_pdf_in_thread(self, threshold):
        # Função que será executada no thread
        test = func.analyze_pdf(self.selected_path, threshold)
        # Atualize a interface do usuário (exemplo)
        self.update_log(test)

    def update_log(self, test):
        # Atualize a interface do usuário com os resultados
        self.log_text.append(str(f"paginas Coloridas: {test[0]}\npaginas preto e branco: {test[1]}"))

    def on_send_clicked(self):
        self.log_text.clear()
        if not self.selected_path:
            QMessageBox.warning(self, "Aviso", "Por favor, escolha um diretório ou arquivo primeiro.")
            return
        

        # Verifica quais funções estão habilitadas
        func1_enabled = self.checkbox_func1.isChecked()
        func2_enabled = self.checkbox_func2.isChecked()
        func3_enabled = self.checkbox_func3.isChecked()
        func4_enabled = self.checkbox_func4.isChecked()

        
        if not (func1_enabled or func2_enabled or func3_enabled or func4_enabled):
            QMessageBox.warning(self, "Aviso", "Nenhuma opção abaixo foi selecionada.")
            return

        additional1_enabled = self.checkbox_additional1.isChecked()
        additional2_enabled = self.checkbox_additional2.isChecked()


        if func1_enabled:
            # Exibir o diálogo de loading e iniciar o thread
            loading_msg = QMessageBox(self)
            loading_msg.setWindowTitle("LOADING")
            loading_msg.setText("O arquivo está sendo processado, por favor aguarde...")
            loading_msg.setStandardButtons(QMessageBox.NoButton)
            loading_msg.show()
            threading.Thread(target=self.analyze_pdf_in_thread_with_loading, args=(threshold, loading_msg)).start()

        if func2_enabled:
            func.create_pdf_with_color_pages(self.selected_path, "output/comCor", "output/semCor", (additional1_enabled, additional2_enabled))

    def analyze_pdf_in_thread_with_loading(self, threshold, loading_msg):
        test = func.analyze_pdf(self.selected_path, threshold)
        self.update_log(test)
        loading_msg.accept()  # Fechar o diálogo de loading


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
