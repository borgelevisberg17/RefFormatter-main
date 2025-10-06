
import re
import uuid
import json
import yaml
import os

def detect_reference_type(text):
    text_lower = text.lower()
    if "disponível em:" in text_lower:
        return "misc"
    elif "tese de doutorado" in text_lower:
        return "phdthesis"
    elif "dissertação de mestrado" in text_lower:
        return "mastersthesis"
    elif "anais" in text_lower or "congresso" in text_lower:
        return "inproceedings"
    elif "revista" in text_lower or re.search(r"v.\s*\d+", text_lower):
        return "article"
    elif "rfc" in text_lower:
        return "techreport"
    elif "in:" in text_lower:
        return "incollection"
    else:
        return "book"

def generate_citekey(author, year):
    if not author:
        return f"anon{year}"

    author_name = author.strip()

    if ',' in author_name:
        last_name_part = author_name.split(',')[0]
    else:
        last_name_part = author_name

    name_words = re.findall(r"[A-Za-zÀ-ÿ]+", last_name_part)

    if not name_words:
        return f"anon{year}"

    cite_key_name = name_words[-1].lower()

    return f"{cite_key_name}{year}"

def extract_data(text):
    author_match = re.match(r"^([A-Z\s,.]+)", text)
    title_match = re.search(r".\s*(.+?).\s", text)
    year_match = re.search(r"\b(19|20)\d{2}\b", text)
    url_match = re.search(r"dispon[ií]vel em:\s*(https?://\S+)", text.lower())
    acesso_match = re.search(r"acess[oa] em:\s*([^\n]+)", text.lower())
    institution_match = re.search(r"(universidade|instituto|faculdade)\s+[a-zà-ú\s]+", text.lower())

    return {
        "author": author_match.group(1).strip().title() if author_match else "Autor Desconhecido",
        "title": title_match.group(1).strip() if title_match else "Título Desconhecido",
        "year": year_match.group(0) if year_match else "0000",
        "url": url_match.group(1) if url_match else "",
        "accessed": acesso_match.group(1).strip().capitalize() if acesso_match else "",
        "institution": institution_match.group(0).title() if institution_match else "",
    }

def format_reference(data, ref_type, style="bibtex"):
    citekey = generate_citekey(data["author"], data["year"])

    if style == "bibtex":
        entry = f"@{ref_type}{{{citekey},\n"
        entry += f"  author    = {{{data['author']}}},\n"
        entry += f"  title     = {{{data['title']}}},\n"
        entry += f"  year      = {{{data['year']}}},\n"
        if ref_type == "misc" and data['url']:
            entry += f"  url       = {{{data['url']}}},\n"
            entry += f"  note      = {{Acesso em: {data['accessed']}}},\n"
        if ref_type in ["phdthesis", "mastersthesis"] and data['institution']:
            entry += f"  school    = {{{data['institution']}}},\n"
        entry = entry.rstrip(",\n") + "\n}"
        return entry

    elif style == "abnt":
        result = f"{data['author'].upper()}. {data['title']}. "
        if ref_type == "phdthesis":
            result += f"Tese (Doutorado) – {data['institution']}, {data['year']}."
        elif ref_type == "mastersthesis":
            result += f"Dissertação (Mestrado) – {data['institution']}, {data['year']}."
        elif ref_type == "misc" and data["url"]:
            result += f"Disponível em: {data['url']}. Acesso em: {data['accessed']}."
        else:
            result += f"{data['year']}."
        return result

    elif style == "apa":
        if data['url']:
            return f"{data['author']} ({data['year']}). {data['title']}. Retrieved from {data['url']}"
        else:
            return f"{data['author']} ({data['year']}). {data['title']}."

    elif style == "custom":
        return f"[{data['year']}] {data['author']} - {data['title']} [{ref_type}]"

    else:
        return f"Formato desconhecido: {style}"

def export_references(entries, base_file, style, format_out):
    ext = {
        "txt": f"{style}.txt",
        "bib": ".bib",
        "json": f"{style}.json",
        "yaml": f"{style}.yaml"
    }.get(format_out, f"{style}.txt")

    output_file = base_file.replace(".txt", ext)

    with open(output_file, 'w', encoding='utf-8') as f:
        if format_out in ["txt", "bib"]:
            f.write("\n\n".join(entries))
        elif format_out == "json":
            json.dump(entries, f, indent=4, ensure_ascii=False)
        elif format_out == "yaml":
            yaml.dump(entries, f, allow_unicode=True)

    print(f"\nArquivo exportado: {output_file}")

def process_references(file_path, style="bibtex", format_out="txt"):
    with open(file_path, 'r', encoding='utf-8') as f:
        raw_text = f.read()
    refs = re.split(r'\n\s*\n', raw_text.strip())  # quebra por blocos mesmo com espaços

    entries = []
    for ref in refs:
        if ref.strip():
            ref_type = detect_reference_type(ref)
            data = extract_data(ref)
            formatted = format_reference(data, ref_type, style)
            entries.append(formatted if format_out in ["txt", "bib"] else data)

    export_references(entries, file_path, style, format_out)

def run_cli():
    print("\n=== Gerador de Referências Acadêmicas ===\n")
    file_path = input("Nome do arquivo de entrada (.txt): ").strip()

    if not os.path.exists(file_path):
        print("Arquivo não encontrado.")
        return

    print("\nEscolha o estilo:")
    print("1. BibTeX\n2. ABNT\n3. APA\n4. Custom")
    style_opt = input("Digite o número do estilo: ").strip()
    style_map = {"1": "bibtex", "2": "abnt", "3": "apa", "4": "custom"}
    style = style_map.get(style_opt, "bibtex")

    print("\nFormato de exportação:")
    print("1. TXT\n2. JSON\n3. YAML\n4. BIB")
    format_opt = input("Digite o número do formato: ").strip()
    format_map = {"1": "txt", "2": "json", "3": "yaml", "4": "bib"}
    format_out = format_map.get(format_opt, "txt")

    process_references(file_path, style, format_out)

    print("\n\nFeito com bits, café forte e fé em Deus.")
    print("By Borge — o cientista hacker com gosto por citação bem feita!\n")

if __name__ == "__main__":
    run_cli()

