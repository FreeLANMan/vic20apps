#!/usr/bin/env python3
# Conversor de texto para código BASIC do VIC-20
# Este script converte texto em código BASIC para o VIC-20 com expansão de 35Kb

# Criado por Adrian Rupp maio 2025.

import os
import sys
import unicodedata
import re

def remover_acentos_e_especiais(texto):
    """Remove acentos, cedilha, trata aspas duplas e emoticons"""
    # Converter para minúsculas
    texto = texto.lower()
    
    # Normalizar texto para remover acentos
    texto_sem_acentos = unicodedata.normalize('NFD', texto)
    texto_sem_acentos = ''.join([c for c in texto_sem_acentos if not unicodedata.combining(c)])
    
    # Substituições básicas de caracteres especiais
    mapa_substituicoes = {
        'ç': 'c', 'Ç': 'c',
        'ñ': 'n', 'Ñ': 'n',
        'º': "'", '°': "'",
        '"': "'",  # Substituir aspas duplas por aspas simples
        '"': "'",  # Aspas tipográficas de abertura
        '"': "'",  # Aspas tipográficas de fechamento
    }
    
    # Dicionário de emoticons comuns
    emoticons = {
        '😊': ':)',
        '🙂': ':)',
        '😃': ':)',
        '😄': ':d',
        '😁': ':d',
        '🤣': 'xd',
        '😂': ':d',
        '😉': ';)',
        '😎': '8)',
        '😢': ':(',
        '😭': ':(',
        '😍': '<3',
        '❤️': '<3',
        '👍': '+1',
        '👎': '-1',
        '🤔': '?',
        '🙄': '://',
        '😮': ':o',
        '😱': ':o',
    }
    
    # Aplicar substituições básicas
    for original, substituto in mapa_substituicoes.items():
        texto_sem_acentos = texto_sem_acentos.replace(original, substituto)
    
    # Substituir emoticons conhecidos
    for emoji, ascii_emoticon in emoticons.items():
        texto_sem_acentos = texto_sem_acentos.replace(emoji, ascii_emoticon)
    
    # Remover outros caracteres não ASCII e emoticons não mapeados
    resultado = ''
    for c in texto_sem_acentos:
        # Manter apenas caracteres imprimíveis ASCII básicos (códigos 32-126)
        if 32 <= ord(c) <= 126:
            resultado += c
    
    return resultado

def texto_para_basic(nome_arquivo):
    try:
        with open(nome_arquivo, 'r', encoding='utf-8') as arquivo:
            linhas_texto = arquivo.readlines()

        nome_saida_base = os.path.splitext(nome_arquivo)[0]
        linhas_basic = []
        num_linha_basic = 10
        incremento_linha = 1
        contador_tela = 0
        telas_inicio = []
        tela_atual = 0
        max_linhas_por_tela = 20

        primeiro_conteudo = num_linha_basic
        telas_inicio.append(primeiro_conteudo)

        for linha_texto in linhas_texto:
            linha_texto = linha_texto.rstrip('\n')
            linha_texto = remover_acentos_e_especiais(linha_texto)
            if not linha_texto.strip():
                continue

            partes = []
            if len(linha_texto) <= 22:
                partes.append(linha_texto)
            else:
                for i in range(0, len(linha_texto), 22):
                    partes.append(linha_texto[i:i+22])

            for i, parte in enumerate(partes):
                ultima_parte = i == len(partes) - 1
                # Escapar qualquer aspas simples restantes no texto para BASIC
                parte_escapada = parte.replace("'", "''")
                
                if ultima_parte:
                    linha_basic = f"{num_linha_basic} ?\"{parte_escapada}\":?"
                else:
                    linha_basic = f"{num_linha_basic} ?\"{parte_escapada}\";"
                linhas_basic.append(linha_basic.lower())  # Convertendo para minúsculas
                num_linha_basic += incremento_linha
                contador_tela += 1

                if ultima_parte:
                    contador_tela += 1

                if contador_tela >= max_linhas_por_tela:
                    linha_espera = num_linha_basic
                    linhas_basic.append(f"{num_linha_basic} get k$:if k$=\"\" then {num_linha_basic}")
                    num_linha_basic += incremento_linha

                    if tela_atual > 0:
                        tela_anterior = tela_atual - 1
                        linha_tela_anterior = telas_inicio[tela_anterior]
                        linhas_basic.append(f"{num_linha_basic} if asc(k$)=145 then ? chr$(147):goto {linha_tela_anterior}")
                        num_linha_basic += incremento_linha

                    tela_atual += 1
                    telas_inicio.append(num_linha_basic + incremento_linha)
                    linhas_basic.append(f"{num_linha_basic} ? chr$(147)")
                    num_linha_basic += incremento_linha
                    contador_tela = 0

        linhas_basic.append(f"{num_linha_basic} end")
        linhas_basic.insert(0, "1 ? chr$(147):poke 36879,8:poke 646,1")

        # Dividir o conteúdo em partes
        content_lines = linhas_basic[1:-1]
        chunks = [content_lines[i:i+471] for i in range(0, len(content_lines), 471)]

        for chunk_num, chunk in enumerate(chunks):
            new_lines = []
            old_to_new = {}
            current_line = 10
            local_telas = []  # Armazena os números de linha de início de tela para esse chunk
            
            # Primeiro passo: atribuir novos números de linha e construir o mapeamento
            for line in chunk:
                parts = line.split(' ', 1)
                old_line = int(parts[0])
                new_line_num = current_line
                old_to_new[old_line] = new_line_num
                
                # Verificar se esta linha é um início de tela
                for tela_inicio in telas_inicio:
                    if old_line == tela_inicio:
                        local_telas.append(new_line_num)
                
                new_line = f"{new_line_num} {parts[1]}"
                new_lines.append(new_line)
                current_line += incremento_linha

            # Segundo passo: atualizar os GOTOs para referenciar a numeração local
            updated_lines = []
            for line in new_lines:
                parts = line.split(' ', 1)
                line_num = int(parts[0])
                content_part = parts[1]
                
                # Procurar GOTOs e referências a linhas
                if "goto" in content_part.lower():
                    # Encontrar o número após "GOTO"
                    goto_match = re.search(r'goto\s+(\d+)', content_part.lower())
                    if goto_match:
                        old_goto = int(goto_match.group(1))
                        
                        # Verificar se o destino do GOTO está neste chunk
                        if old_goto in old_to_new:
                            new_goto = old_to_new[old_goto]
                            content_part = re.sub(r'goto\s+\d+', f'goto {new_goto}', content_part.lower())
                        else:
                            # Se estamos tentando voltar para uma tela anterior que não está neste chunk
                            # Vamos modificar para ir para a primeira linha deste chunk
                            if "asc(k$)=145" in content_part.lower():  # Tecla para voltar
                                if len(local_telas) > 0:
                                    # Apontar para a tela anterior dentro deste chunk
                                    current_tela_index = None
                                    for i, tela in enumerate(local_telas):
                                        if tela <= line_num and (current_tela_index is None or tela > local_telas[current_tela_index]):
                                            current_tela_index = i
                                    
                                    # Se encontramos a tela atual, vamos para a anterior (se houver)
                                    if current_tela_index is not None and current_tela_index > 0:
                                        new_goto = local_telas[current_tela_index - 1]
                                    else:
                                        # Se estamos na primeira tela deste chunk, mantemos na mesma tela
                                        new_goto = local_telas[0] if local_telas else 10
                                else:
                                    new_goto = 10  # Ir para o início deste chunk
                                
                                content_part = re.sub(r'goto\s+\d+', f'goto {new_goto}', content_part.lower())
                
                # Substituir referências em IF THEN para "esperando tecla"
                if "then" in content_part.lower() and "if k$=\"\"" in content_part.lower():
                    then_match = re.search(r'then\s+(\d+)', content_part.lower())
                    if then_match:
                        old_then = int(then_match.group(1))
                        if old_then in old_to_new:
                            new_then = old_to_new[old_then]
                            content_part = re.sub(r'then\s+\d+', f'then {new_then}', content_part.lower())
                        else:
                            # Se a linha não existe neste chunk, apontar para a própria linha
                            content_part = re.sub(r'then\s+\d+', f'then {line_num}', content_part.lower())

                updated_line = f"{line_num} {content_part.lower()}"
                updated_lines.append(updated_line)
            
            # Adicionar navegação entre arquivos para chunks subsequentes
            if chunk_num < len(chunks) - 1:  # Se não for o último chunk
                # Adicionar instrução para carregar o próximo arquivo
                next_part = chunk_num + 2  # +2 porque chunk_num começa em 0 e o nome do arquivo começa com part1
                updated_lines.append(f"{current_line} ? \"carregar parte {next_part}\"")
                current_line += incremento_linha
            
            # Construir o arquivo completo com a nova numeração
            full_lines = [
                "1 ? chr$(147):poke 36879,8:poke 646,1",  # Linha inicial
                *updated_lines,
                f"{current_line} end"  # Linha final
            ]

            # Salvar o arquivo
            nome_saida = f"{nome_saida_base}_part{chunk_num + 1}.bas"
            with open(nome_saida, 'w', encoding='utf-8') as f:
                for linha in full_lines:
                    f.write(linha + '\n')
            print(f"Arquivo '{nome_saida}' gerado com sucesso!")

        return True

    except FileNotFoundError:
        print(f"Erro: O arquivo '{nome_arquivo}' não foi encontrado.")
        return False
    except Exception as e:
        print(f"Erro: {e}")
        return False

if __name__ == "__main__":
    # Processa todos os arquivos .txt no diretório atual
    arquivos_txt = [arquivo for arquivo in os.listdir() if arquivo.endswith('.txt')]
    if not arquivos_txt:
        print("Nenhum arquivo .txt encontrado no diretório.")
    else:
        for arquivo in arquivos_txt:
            print(f"Convertendo arquivo: {arquivo}")
            texto_para_basic(arquivo)

# Criado por Adrian Rupp maio 2025.
