import fitz  # PyMuPDF
from PIL import Image
import numpy as np
import os

def is_color(image, threshold=10):
    # Converte a imagem para um array numpy
    img_array = np.array(image)
    
    # Verifica se a imagem tem 3 canais (RGB) e converte para escala de cinza
    if len(img_array.shape) == 3 and img_array.shape[2] == 3:
        # Converte para escala de cinza
        grayscale = np.dot(img_array[...,:3], [0.299, 0.587, 0.114])
        grayscale = np.stack((grayscale,)*3, axis=-1)
        
        # Verifica se há alguma diferença de cor
        if np.any(np.abs(img_array - grayscale) > threshold):
            return True
    return False

def analyze_pdf(pdf_path, threshold=10):
    try:
        # Abre o arquivo PDF
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"Erro ao abrir o arquivo PDF: {e}")
        return None

    color_pages = 0
    bw_pages = 0
    
    for page_num in range(len(doc)):
        # Obtém a página
        page = doc.load_page(page_num)
        
        # Renderiza a página como uma imagem
        pix = page.get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        
        if is_color(img, threshold):
            color_pages += 1
        else:
            bw_pages += 1
    
    return color_pages, bw_pages
def create_pdf_with_color_pages(pdf_path, output_pdf_path_color, output_pdf_path_bw, mode=(True, False)):
    # Abre o arquivo PDF
    doc = fitz.open(pdf_path)
    
    # Cria novos documentos para páginas coloridas e preto e branco
    pdf_color = fitz.open()
    pdf_bw = fitz.open()
    
    for page_num in range(len(doc)):
        # Obtém a página
        page = doc.load_page(page_num)
        
        # Renderiza a página como uma imagem
        pix = page.get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        
        # Verifica se a página é colorida ou preto e branco
        if is_color(img):
            # Adiciona a página ao PDF colorido
            pdf_color.insert_pdf(doc, from_page=page_num, to_page=page_num)
        else:
            # Adiciona a página ao PDF preto e branco
            pdf_bw.insert_pdf(doc, from_page=page_num, to_page=page_num)
    
    # Salva os PDFs
    if mode[0]:
        pdf_color.save(output_pdf_path_color)
        print(f"PDF com páginas coloridas salvo em {output_pdf_path_color}")
    if mode[1]:
        pdf_bw.save(output_pdf_path_bw)
        print(f"PDF com páginas preto e branco salvo em {output_pdf_path_bw}")
    

def analyze_color_percentage(image, threshold=10):
    # Converte a imagem para um array numpy
    img_array = np.array(image)
    
    # Verifica se a imagem tem 3 canais (RGB)
    if len(img_array.shape) == 3 and img_array.shape[2] == 3:
        # Converte a imagem para escala de cinza
        grayscale = np.dot(img_array[...,:3], [0.299, 0.587, 0.114])
        grayscale = np.stack((grayscale,)*3, axis=-1)
        
        # Máscara para pixels que não são preto e branco
        color_mask = np.abs(img_array - grayscale) > threshold
        color_pixels = np.any(color_mask, axis=-1)
        
        # Calcula a porcentagem de pixels coloridos
        total_pixels = img_array.shape[0] * img_array.shape[1]
        color_pixel_count = np.sum(color_pixels)
        color_percentage = (color_pixel_count / total_pixels) * 100
        
        return color_percentage
    return 0

def analyze_pdf_colors(pdf_path):
    # Abre o arquivo PDF
    doc = fitz.open(pdf_path)
    
    for page_num in range(len(doc)):
        # Obtém a página
        page = doc.load_page(page_num)
        
        # Renderiza a página como uma imagem
        pix = page.get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        
        # Analisa a porcentagem de cores
        color_percentage = analyze_color_percentage(img)
        
        # Exibe o resultado
        print(f"Pagina {page_num + 1} - {color_percentage:.2f}%     colorida")
