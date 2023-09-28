import os
import re
import json
import argparse
from collections import Counter

# Função para pré-processar o texto
def preprocess_text(text):
    # Remove números
    text = re.sub(r'\b\d+\b', '', text) # \b: Isso representa uma âncora de limite de palavra, garantindo que
                                        # o número seja uma palavra completa e não uma parte de uma palavra
                                        # \d+: Isso corresponde a um ou mais dígitos (0-9).
    
    # Remove símbolos e outros caracteres indesejados
    text = re.sub(r'[^\w\s\']', ' ', text) # ^\w\s\': Isso significa que estamos procurando por caracteres que
                                           # não sejam Letras, Espaços em branco ou Apóstrofos e os substituindo
    
    # Normaliza para letras minúsculas
    text = text.lower()
    
    return text

# Função para contar palavras em um arquivo
def count_words_in_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    text = ' '.join([line.strip() for line in lines if not line.strip().isdigit()])
    text = preprocess_text(text) # Processa o texto antes de separá-lo novamente
    
    words = text.split()
    word_counts = Counter(words)
    
    return word_counts

# Função para processar a temporada
def process_season(directory):
    # Encontra todos os arquivos .srt na temporada
    episode_files = [os.path.join(root, file) for root, _, files in os.walk(directory) for file in files if file.endswith(".srt")]
    
    # Função para processar um arquivo individual e contar palavras
    def process_file(file_path):
        return count_words_in_file(file_path)
    
    # Aplica a função process_file a cada arquivo de episódio e combina as contagens com Counter e sum => Composição de Funções
    episode_word_counts = map(process_file, episode_files) # Map => Funções de alta Ordem
    return Counter(dict(sum(episode_word_counts, Counter())))

# Função para salvar contagens de palavras em um arquivo JSON
def save_word_counts_to_json(word_counts, output_file):
    sorted_word_counts = [{"palavra": word, "frequencia": count} for word, count in word_counts.items()]
    sorted_word_counts.sort(key=lambda x: x["frequencia"], reverse=True)
    
    with open(output_file, 'w', encoding='utf-8') as json_file:
        json.dump(sorted_word_counts, json_file, ensure_ascii=False, indent=4)

# Função principal que coordena todo o processo
def main(input_directory, output_directory):
    season_word_counts = process_season(input_directory)
    
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)  # Cria o diretório se ele não existir
    
    season_output_file = os.path.join(output_directory, f'temporada-{os.path.basename(input_directory)}.json')
    save_word_counts_to_json(season_word_counts, season_output_file)
    
    for root, _, files in os.walk(input_directory):
        for file in files:
            if file.endswith(".srt"):
                file_path = os.path.join(root, file)
                episode_word_counts = count_words_in_file(file_path)
                episode_output_file = os.path.join(output_directory, f'episodio-{os.path.basename(file_path)}.json')
                save_word_counts_to_json(episode_word_counts, episode_output_file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Contar palavras em arquivos .srt de uma temporada de série.")
    parser.add_argument("input_directory", help="Diretório contendo os arquivos .srt da temporada.")
    parser.add_argument("output_directory", nargs='?', default="resultados", help="Diretório de saída para os resultados em formato JSON. (Padrão: 'resultados')")
    args = parser.parse_args()
    
    main(args.input_directory, args.output_directory)
