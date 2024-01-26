from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
import csv
import time
from urllib.parse import urljoin

def pesquisar_instituicao(instituicao_pesquisar, writer, posicao_inicial=0):
    driver = None
    try:
        # Configuração do WebDriver
        driver = webdriver.Chrome()

        # Navega até a página do Sisu
        driver.get("https://sisu.mec.gov.br/#/vagas")

        # Localize o campo de pesquisa
        campo_pesquisa = driver.find_element(By.XPATH, "//input[@role='combobox']")
        campo_pesquisa.send_keys(instituicao_pesquisar)

        opcoes = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.ng-option.ng-option-child'))
        )

        # Itera sobre os elementos e verifica se o texto corresponde ao nome desejado
        for opcao in opcoes:
            nome_curso_opcao = opcao.find_element(By.TAG_NAME, 'span').text.strip()
            if instituicao_pesquisar.lower() == nome_curso_opcao.lower():
                # Faça a ação desejada com a opção (por exemplo, clicar)
                opcao.click()
                break  # Termina o loop após encontrar a correspondência

        # Espere até que os resultados sejam carregados
        driver.implicitly_wait(10)

        # Localize todas as divs com os cards de vaga
        divs_cards = driver.find_elements(By.CSS_SELECTOR, '.card-vaga')

        # Lista para armazenar os links de detalhes
        links_detalhes = []

        # Itera sobre os divs_cards e obtém os atributos href
        for div_card in divs_cards:
            href_value = div_card.get_attribute('href')
            links_detalhes.append(href_value)

        # Itera sobre os links de detalhes coletados a partir da posição inicial
        for detalhes_url in links_detalhes[posicao_inicial:]:
            try:
                # Construir a URL completa usando urljoin
                detalhes_url_completa = urljoin(driver.current_url, detalhes_url)

                # Clique no card para abrir a página de detalhes
                driver.get(detalhes_url_completa)
                time.sleep(2)  # Adicione uma pausa para garantir que a página seja totalmente carregada
                instituicao = driver.find_element(By.TAG_NAME, 'h3').text
                print(instituicao)

                # Agora você está na página de detalhes do curso, extraia as informações necessárias
                nome_curso = driver.find_element(By.CLASS_NAME, 'titulo-box').text.strip()
                
                # Encontraro todas as divs dentro da div principal
                termo_ies_divs = driver.find_elements(By.CLASS_NAME, 'termo-ies')
                grau = termo_ies_divs[1].find_element(By.CLASS_NAME, 'titulo-box').text.strip()
                turno = termo_ies_divs[2].find_element(By.CLASS_NAME, 'titulo-box').text.strip()
                total_vagas = termo_ies_divs[3].find_element(By.CLASS_NAME, 'titulo-box').text.strip()
                acoes_afirmativas = termo_ies_divs[4].find_element(By.CLASS_NAME, 'titulo-box').text.strip()
                # print([nome_curso, grau, turno, total_vagas, acoes_afirmativas])
                div_rows_notas = driver.find_elements(By.CLASS_NAME,'row')
                try:
                    div_ampla_concorrencia = div_rows_notas[6]
                except IndexError:
                    div_ampla_concorrencia = div_rows_notas[3]
                notas_ampla_concorrencia = div_ampla_concorrencia.find_elements(By.CLASS_NAME,'col-md-6')
                try:
                    texto_alvo = notas_ampla_concorrencia[0].find_element(By.CLASS_NAME,'nota-modalidade')
                except IndexError:
                    continue
                    
                try:
                    # Tentar encontrar o elemento 'strong'
                    nota_alvo = texto_alvo.find_element(By.TAG_NAME, 'strong').text

                except NoSuchElementException:
                # Se o elemento 'strong' não for encontrado, atribuir 0
                    nota_alvo = 0
                print(nota_alvo)
                writer.writerow([instituicao,nome_curso, grau, turno, total_vagas, acoes_afirmativas,nota_alvo])

                # Volte à página anterior (lista de cursos)
                driver.back()
                time.sleep(2)  # Adicione uma pausa para garantir que a página anterior seja totalmente carregada


            except StaleElementReferenceException:
                print("Elemento não está mais presente no DOM.")
                continue
            except NoSuchElementException:
                print("Link dentro da div não encontrado. HTML da div:")
                print(div_card.get_attribute('outerHTML'))

    except KeyboardInterrupt:
        print("Interrupção do usuário. Fechando o WebDriver.")

    finally:
        if driver:
            # Feche o navegador ao finalizar
            driver.quit()

# Abra o arquivo CSV em modo de apêndice ('a')
with open('saida_Administração_2_dia.csv', 'a', newline='', encoding='utf-8') as csv_output:
    # Crie um escritor CSV sem cabeçalhos
    csv_writer = csv.writer(csv_output)

    # Chame a função pesquisar_instituicao com a posição inicial especificada
    pesquisar_instituicao('Administração', csv_writer, 182)
    time.sleep(2)
