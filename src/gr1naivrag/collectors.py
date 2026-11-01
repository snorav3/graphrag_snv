import re


def collect_wikipedia_links(file_path: str) -> list[str]:
    """Wikipédia URL-ek kigyűjtése az md-fájlból."""
    print(f"Wikipédia linkek kigyűjtése a '{file_path}' fájlból...")
    
    wiki_regex = r'https://hu\.wikipedia\.org/wiki/[^\s>\"\']+'
    # en ??
    
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    found_links = re.findall(wiki_regex, content)
    
    pure_links = list(set(found_links))
    
    print(f"[Fájlkezelő] Wikipédia linkek száma: {len(pure_links)}")
    for link in pure_links:
        print(f"   -> {link}")
        
    return pure_links


def collect_questions(file_path: str) -> list[str]:
    """'## Kérdések' alatti listaelemek (kérdések) kigyűjtése az md-fájlból."""
    print(f"Kérdések kigyűjtése a '{file_path}' fájlból...")
    
    quests = []
    inside_quests = False
    
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            pure_line = line.strip()
            
            if pure_line.startswith("## Kérdések:"):
                inside_quests = True
                continue
            
            # Egy másik főszekciónál kikapcsoljuk a gyűjtést
            if inside_quests and pure_line.startswith("##"):
                break

            # A kérdések sorszámozottak
            if inside_quests and re.match(r'^\d+\.\s+', pure_line):
                quest = re.sub(r'^\d+\.\s*', '', pure_line)
                if quest:
                    quests.append(quest)
                    
    print(f"[Fájlkezelő] Talált kérdések száma: {len(quests)}")

    return quests
