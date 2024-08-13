import fitz  # PyMuPDF
from PIL import Image
import numpy as np
import threading
import time 

def is_color(image, threshold=10):
    img_array = np.array(image)

    if img_array.ndim == 3 and img_array.shape[2] == 3:
        # Reduz a resolução da imagem para acelerar o processamento
        img_array = img_array[::4, ::4]

        # Calcular as diferenças entre os canais de cor diretamente
        r_g_diff = np.abs(img_array[..., 0] - img_array[..., 1])
        r_b_diff = np.abs(img_array[..., 0] - img_array[..., 2])
        g_b_diff = np.abs(img_array[..., 1] - img_array[..., 2])

        # Verificar se qualquer diferença entre os canais excede o threshold
        return np.any((r_g_diff > threshold) | (r_b_diff > threshold) | (g_b_diff > threshold))
    return False

def analyze_pdf_range(doc, page_range, threshold, result_container, index):
    color_pages = 0
    bw_pages = 0

    for page_num in page_range:
        page = doc.load_page(page_num)
        pix = page.get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        if is_color(img, threshold):
            color_pages += 1
        else:
            bw_pages += 1

    result_container[index] = (color_pages, bw_pages)

def analyze_pdf_threaded(pdf_path, threshold=10, num_threads=4):
    try:
        doc = fitz.open(pdf_path)
        total_pages = len(doc)
        pages_per_thread = total_pages // num_threads
        threads = []
        results = [None] * num_threads

        for i in range(num_threads):
            start_page = i * pages_per_thread
            if i == num_threads - 1:
                end_page = total_pages
            else:
                end_page = (i + 1) * pages_per_thread

            thread = threading.Thread(target=analyze_pdf_range,
                                      args=(doc, range(start_page, end_page), threshold, results, i))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        total_color_pages = sum(result[0] for result in results if result is not None)
        total_bw_pages = sum(result[1] for result in results if result is not None)

        return total_color_pages, total_bw_pages

    except Exception as e:
        print(f"Erro ao abrir o arquivo PDF: {e}")
        return None, None

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
# =-=-=-=-=-=-==-=-=-=-=-=-==-=-=-=-=-=-==-=-=-=-=-=-==-=-=-=-=-=-==-=-=-=-=-=-==-=-=-=-=-=-==-=-=-=-=-=-=
# Começa a contagem do tempo
start_time = time.time()

# Execute o código apenas uma vez para medir o tempo corretamente
color_pages, bw_pages = analyze_pdf('aaa.pdf')

# Calcula o tempo total de execução
end_time = time.time()
execution_time = end_time - start_time

# Mostra o tempo de execução e o resultado
print('-=-=-=-=-=-=-=-==-=-==-=-=-=-=-=-=-=-=-=-==-=-==-=-=-=-=-=-=-=-=-=-==\n - def analyze_pdf_threaded - new time\n')
print(f"O codigo levou {execution_time:.2f} segundos para rodar.")
print(f"Paginas coloridas: {color_pages}, Paginas preto e branco: {bw_pages}")
print('-=-=-=-=-=-=-=-==-=-==-=-=-=-=-=-=-=-=-=-==-=-==-=-=-=-=-=-=-=-=-=-==')

