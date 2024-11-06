from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fpdf import FPDF
import time

# Configuração do WebDriver para Firefox
driver_path = 'D:/git/case2/case2/geckodriver.exe'
service = Service(driver_path)

# Especifique o caminho para o Firefox
firefox_binary_path = 'C:/Program Files/Mozilla Firefox/firefox.exe'  # Atualize este caminho, se necessário
options = Options()
options.binary_location = firefox_binary_path

# Inicialize o WebDriver com as opções
driver = webdriver.Firefox(service=service, options=options)

# URL para a pesquisa de celulares Apple
url = "https://store.vivo.com.br/celulares/c?query=:relevance:allCategories:celulares:brand:Apple&sortCode=pricePriority-desc"
driver.get(url)

# Espera a página carregar totalmente
wait = WebDriverWait(driver, 30)  # Espera de até 30 segundos

print("Página principal carregada, aguardando produtos...")

# Loop para encontrar o primeiro produto disponível
products = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'product-card--grid')))
product_found = False

for product in products:
    try:
        # Tenta localizar a div `product-card__bottom` dentro do produto
        product_bottom_elements = product.find_elements(By.CLASS_NAME, 'product-card__bottom')

        # Verifica se `product-card__bottom` contém `product-card__out-of-stock`
        if product_bottom_elements:
            out_of_stock_message = product_bottom_elements[0].find_elements(By.CLASS_NAME, 'product-card__out-of-stock')

            if out_of_stock_message:
                print("Produto esgotado encontrado. Passando para o próximo...")
                continue  # Se a mensagem de esgotado estiver presente, passa para o próximo produto

    except Exception as e:
        print(f"Erro ao verificar disponibilidade do produto: {e}")
        continue

    # Se o produto não tiver o elemento de esgotado, considera-o como disponível
    print("Produto disponível encontrado. Tentando abrir a página do produto...")

    # Rola até o produto e tenta clicar
    driver.execute_script("arguments[0].scrollIntoView();", product)
    time.sleep(1)  # Pequena espera para garantir que o elemento está visível

    try:
        product.click()  # Tenta clicar no produto
        product_found = True
        print("Clique no produto realizado com sucesso.")
        break  # Sai do loop, pois encontrou um produto disponível
    except:
        # Se o clique direto falhar, realiza o clique via JavaScript
        driver.execute_script("arguments[0].click();", product)
        print("Clique no produto realizado via JavaScript.")
        product_found = True
        break

if not product_found:
    print("Nenhum produto disponível encontrado.")
    driver.quit()
    exit()

# Adiciona uma espera extra para garantir que a página do produto carregue completamente
time.sleep(5)

# Coleta de informações do produto
try:
    # Espera e rola até o campo de CEP usando o ID exato do input
    cep_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input#postalCode")))
    driver.execute_script("arguments[0].scrollIntoView();", cep_input)
    time.sleep(1)  # Pequena espera para garantir que o campo está visível

    # Insere o CEP e dispara eventos 'input' e 'change' via JavaScript
    driver.execute_script(
        "arguments[0].value = '87430-000'; arguments[0].dispatchEvent(new Event('input')); arguments[0].dispatchEvent(new Event('change'));",
        cep_input)
    print("CEP inserido com sucesso via JavaScript, com eventos disparados.")

    # Espera até que o botão "Confirmar" de consulta de CEP esteja habilitado
    consult_button = wait.until(EC.element_to_be_clickable((By.ID, 'applyPostalCode')))
    print("Botão de consulta de CEP encontrado e clicado.")
    consult_button.click()

    # Aguarda que o prazo de entrega carregue completamente e captura o texto específico
    delivery_time = wait.until(EC.visibility_of_element_located(
        (By.CLASS_NAME, 'product-delivery-time__content-wrapper__delivery-time__result__days'))).text
    print("Prazo de entrega obtido:", delivery_time)

    # Aguarda que a descrição do produto carregue completamente e captura o texto
    product_description = wait.until(
        EC.visibility_of_element_located((By.CLASS_NAME, 'custom-product-details-tab'))).text
    print("Descrição do produto obtida.")

    # Substituir caracteres problemáticos na descrição
    product_description = product_description.replace("—", "-")

except Exception as e:
    print(f"Erro durante a coleta de informações: {e}")
    driver.quit()
    exit()

# Fecha o navegador
driver.quit()
print("Navegador fechado. Gerando PDF...")

# Gera o PDF com as informações coletadas
pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=12)

pdf.cell(200, 10, txt="Informações do Produto", ln=True, align='C')
pdf.ln(10)

pdf.cell(200, 10, txt="Descrição do Produto:", ln=True)
pdf.multi_cell(0, 10, txt=product_description)
pdf.ln(10)

pdf.cell(200, 10, txt="Prazo de Entrega para CEP 87430-000:", ln=True)
pdf.cell(200, 10, txt=delivery_time, ln=True)

# Salva o PDF
pdf_file_path = "D:/git/case2/case2/informacoes_produto.pdf"
pdf.output(pdf_file_path)

print(f"Arquivo PDF gerado com sucesso em: {pdf_file_path}")
