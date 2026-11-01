from langchain_neo4j import GraphCypherQAChain, Neo4jGraph
from langchain_ollama import ChatOllama

from gr2neo4j.questions import QUESTIONS


def setup_graph_rag(graph: Neo4jGraph, chat_model):
    graph.refresh_schema()
    print("A gráf sémája:")
    print(graph.schema)
    print("-" * 50)
    
    chain = GraphCypherQAChain.from_llm(
        llm=ChatOllama(model=chat_model, temperature=0),
        graph=graph,
        top_k=50,
        validate_cypher=True,
        allow_dangerous_requests=True,
        verbose=True,
    )

    return chain


def run_diagnostic_report(graph: Neo4jGraph):
    rt = "KORPUSZ SZERKEZETI ÉS DIAGNOSZTIKAI RIPORTJA"
    
    print("\n" + "=" * rt.__len__())
    print(rt)
    print("=" * rt.__len__())
    
    # 1. Lekérdezés: Leghosszabb dokumentum
    r1 = graph.query(QUESTIONS[0])
    print("\n1. LEGHOSSZABB DOKUMENTUM: ")
    if r1:
        print(f"  - Cím: {r1[0]['Dokumentum']}")
        print(f"  - Chunkok száma: {r1[0]['ChunkokSzama']} db")
    else:
        print("  Nincs adat.")

    # 2. Lekérdezés: Legrövidebb dokumentumok
    r2 = graph.query(QUESTIONS[1])
    print("\n2. LEGRÖVIDEBB DOKUMENTUMOK: ")
    if r2:
        for row in r2:
            print(f"  - {row['Dokumentum']}: {row['ChunkokSzama']} db chunk")
    else:
        print("  - Nincs adat.")

    # 3. Lekérdezés: Üres vagy szemét chunkok szűrése (<15 karakter)
    r3 = graph.query(QUESTIONS[2])
    print("\n3. GYANÚS/SZEMÉT CHUNKOK (Hossz < 15 karakter): ")
    if r3:
        for row in r3:
            print(f"  - Hiba itt: {row['Dokumentum']} -> {row['ChunkID']} ({row['KarakterekSzama']} karakter)")
    else:
        print("  - Tiszta korpusz! Nincsenek kritikusan rövid vagy üres chunkok.")

    # 4. Lekérdezés: Megszakadt NEXT_CHUNK láncok ellenőrzése
    r4 = graph.query(QUESTIONS[3])
    print("\n4. LÁNCOLATI ÉPSÉG (Megszakadt NEXT_CHUNK kapcsolatok): ")
    if r4:
        for row in r4:
            print(f"  - MEGSZAKADT LÁNC: {row['Dokumentum']} oldalon a(z) {row['Sorszam']}. sorszámú chunk után hiányzik az él!")
    else:
        print("  - Tökéletes láncolat! Minden egymást követő chunk sikeresen össze van kötve.")

    # 5. Lekérdezés: Globális statisztika
    r5 = graph.query(QUESTIONS[4])
    print("\n5. GLOBÁLIS STATISZTIKA: ")
    if r5:
        print(f"  - Összes betöltött dokumentum: {r5[0]['OsszesDokumentum']} db")
        print(f"  - Adatbázisban lévő összes chunk: {r5[0]['OsszesChunk']} db")
        print(f"  - Chunkok átlagos hossza: {r5[0]['AtlagosChunkKarakterhossz']} karakter")
        
    print("\n" + "-" * 80 + "\n")
    
    # 6. Lekérdezés: Hány vállalatcsoportnak vagy márkának van főhadiszállása egy adott kontinensen (pl. Európa)?
    r6 = graph.query(QUESTIONS[5])
    print("\n6. FŐHADISZÁLLÁSOK SZÁMA ADOTT KONTINENSEN (EURÓPA): ")
    if r6:
        print(f"  - {r6[0]['VallalatcsoportokSzama']} + {r6[0]['MarkakSzama']} db főhadiszállás")
    else:
        print("  - Nincs adat az adott kontinensre vonatkozóan.")
    
    # 7. Lekérdezés: Mik a Scania testvérmárkái (legfeljebb 5 mélységben)?
    r7 = graph.query(QUESTIONS[6])
    print("\n7. SCANIA TESTVÉRMÁRKÁI (LEGFELJEBB 5 MÉLYSÉGBEN): ")
    if r7:
        for row in r7:
            print(f"  - {row['TestverMarka']}")
    else:
        print("  - Nincs adat a Scania testvérmárkáira vonatkozóan.")
    
    # 8. Lekérdezés: Számold meg, hogy az egyes vállalatcsoportok alá közvetlenül hány márka tartozik!
    r8 = graph.query(QUESTIONS[7])
    print("\n8. VÁLLALATCSOPORTOK ALÁ TARTOZÓ MÁRKÁK SZÁMA: ")
    if r8:
        for row in r8:
            print(f"  - {row['Vallalatcsoport']}: {row['OsszesMelysegiMarka']} db márka")
    else:
        print("  - Nincs adat a vállalatcsoportokra vonatkozóan.")
    
    print("\n" + "=" * 80)
