import fitz  # PyMuPDF
from PIL import Image
import numpy as np
import threading
import os

def is_color(image, threshold=10):
    img_array = np.array(image)
    if len(img_array.shape) == 3 and img_array.shape[2] == 3:
        grayscale = np.dot(img_array[...,:3], [0.299, 0.587, 0.114])
        grayscale = np.stack((grayscale,)*3, axis=-1)
        return np.any(np.abs(img_array - grayscale) > threshold)
    return False

def analyze_pdf(pdf_path, threshold=10, result_container=None, index=None):
    try:
        doc = fitz.open(pdf_path)
        color_pages = 0
        bw_pages = 0

        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            pix = page.get_pixmap()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            if is_color(img, threshold):
                color_pages += 1
            else:
                bw_pages += 1
        
        # Se result_container e index são usados, armazene os resultados lá
        if result_container is not None and index is not None:
            result_container[index] = (color_pages, bw_pages)
        else:
            # Caso contrário, retorne os resultados diretamente
            return color_pages, bw_pages

    except Exception as e:
        print(f"Erro ao abrir o arquivo PDF: {e}")
        if result_container is not None and index is not None:
            result_container[index] = (None, None)
        else:
            return None, None

def create_pdf_with_color_pages(pdf_path, output_pdf_path_color, output_pdf_path_bw, mode=(True, False), result_container=None, index=None):
    try:
        doc = fitz.open(pdf_path)
        pdf_color = fitz.open()
        pdf_bw = fitz.open()

        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            pix = page.get_pixmap()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            if is_color(img):
                pdf_color.insert_pdf(doc, from_page=page_num, to_page=page_num)
            else:
                pdf_bw.insert_pdf(doc, from_page=page_num, to_page=page_num)

        if mode[0]:
            color_dir = os.path.dirname(output_pdf_path_color)
            if not os.path.exists(color_dir):
                os.makedirs(color_dir)
            pdf_color.save(output_pdf_path_color)
            print(f"PDF com páginas coloridas salvo em {output_pdf_path_color}")

        if mode[1]:
            bw_dir = os.path.dirname(output_pdf_path_bw)
            if not os.path.exists(bw_dir):
                os.makedirs(bw_dir)
            pdf_bw.save(output_pdf_path_bw)
            print(f"PDF com páginas preto e branco salvo em {output_pdf_path_bw}")

        if result_container is not None and index is not None:
            result_container[index] = True

    except Exception as e:
        print(f"Erro ao processar o PDF: {e}")
        if result_container is not None and index is not None:
            result_container[index] = False

def analyze_color_percentage(image, threshold=10):
    img_array = np.array(image)
    if len(img_array.shape) == 3 and img_array.shape[2] == 3:
        grayscale = np.dot(img_array[...,:3], [0.299, 0.587, 0.114])
        grayscale = np.stack((grayscale,)*3, axis=-1)
        color_mask = np.abs(img_array - grayscale) > threshold
        color_pixels = np.any(color_mask, axis=-1)
        total_pixels = img_array.shape[0] * img_array.shape[1]
        color_pixel_count = np.sum(color_pixels)
        color_percentage = (color_pixel_count / total_pixels) * 100
        return color_percentage
    return 0

def analyze_pdf_colors( pdf_path, threshold=10, result_container=None, index=None):
    try:
        doc = fitz.open(pdf_path)
        total_color_percentage = 0
        page_count = len(doc)

        for page_num in range(page_count):
            page = doc.load_page(page_num)
            pix = page.get_pixmap()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            color_percentage = analyze_color_percentage(img)
            total_color_percentage += color_percentage
            print(f"Página {page_num + 1} - {color_percentage:.2f}% colorida")

        average_color_percentage = (total_color_percentage / page_count) if page_count > 0 else 0
        average_color_percentage = round(average_color_percentage, 2)  # Formatar para 2 casas decimais

        if result_container is not None and index is not None:
            result_container[index] = average_color_percentage

    except Exception as e:
        print(f"Erro ao analisar o PDF: {e}")
        if result_container is not None and index is not None:
            result_container[index] = None

def main( threshold, pdf_path, output_pdf_path_color, output_pdf_path_bw, mode=(True, False), mods=(False, False, False)):
    result_container = [None] * 3  # Para armazenar os resultados das threads

    # Criar threads para cada função
    threads = []
    if mods[0]:
        thread1 = threading.Thread(target=analyze_pdf, args=(pdf_path, threshold, result_container, 0))
        threads.append(thread1)
    if mods[2]:
        thread2 = threading.Thread(target=create_pdf_with_color_pages, args=(pdf_path, output_pdf_path_color, output_pdf_path_bw, mode, result_container, 1))
        threads.append(thread2)
    if mods[1]:
        thread3 = threading.Thread(target=analyze_pdf_colors, args=( pdf_path, threshold, result_container, 2))
        threads.append(thread3)

    # Iniciar as threads
    for thread in threads:
        thread.start()

    # Aguardar o término de todas as threads
    for thread in threads:
        thread.join()

    # Verificar resultados
    results = {
        "analyze_pdf": result_container[0],
        "create_pdf_with_color_pages": result_container[1],
        "analyze_pdf_colors": result_container[2]
    }

    for key, result in results.items():
        if result is None:
            print(f"Erro em {key}")
        elif isinstance(result, tuple):
            print(f"{key} concluído com sucesso: {result}")
        elif isinstance(result, bool) and result:
            print(f"{key} concluído com sucesso")
        else:
            print(f"Erro em {key}")

    return results

if __name__ == "__main__":
    result = main(
        threshold=10, 
        pdf_path="aaa.pdf",  # Substitua pelo caminho correto do PDF
        output_pdf_path_color="output/comCor.pdf",
        output_pdf_path_bw="output/semCor.pdf",
        mode=(True, True),
        mods=(True, False, False)
    )
    print('\n' + str(result))
