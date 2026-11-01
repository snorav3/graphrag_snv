# LEKÉRDEZÉSEK: 
# 0. Hány chunk tartozik a leghosszabb dokumentumhoz?
# 1. Melyik dokumentumok a legrövidebbek (és hány chunkból állnak)?
# 2. Vannak-e üres, túl rövid vagy "szemét" chunk-ok?
# 3. Megszakadt láncok ellenőrzése (Láncolati épség teszt)
# 4. A korpusz globális statisztikai összegzése
#
# 5. Hány vállalatcsoportnak vagy márkának van főhadiszállása egy adott kontinensen (pl. Európa)?
# 6. Mik a Scania testvérmárkái (legfeljebb 5 mélységben)?
# 7. Számold meg, hogy az egyes vállalatcsoportok alá közvetlenül hány márka tartozik!


QUESTIONS = [
    """
    MATCH (d:Document)-[:CONTAINS]->(c:Chunk)
    RETURN d.title AS Dokumentum, count(c) AS ChunkokSzama
    ORDER BY ChunkokSzama DESC
    LIMIT 1
    """, 
    
    """
    MATCH (d:Document)-[:CONTAINS]->(c:Chunk)
    RETURN d.title AS Dokumentum, count(c) AS ChunkokSzama
    ORDER BY ChunkokSzama ASC
    LIMIT 5
    """, 
    
    """
    MATCH (d:Document)-[:CONTAINS]->(c:Chunk)
    WHERE c.text IS NULL OR size(c.text) < 15
    RETURN d.title AS Dokumentum, c.id AS ChunkID, c.text AS GyanusTartalom, size(c.text) AS KarakterekSzama
    """, 
    
    """
    MATCH (d:Document)-[:CONTAINS]->(c:Chunk)
    WITH d, c, [(d)-[:CONTAINS]->(all_c) | all_c.sequence] AS sorszamok
    WITH d, c, apoc.coll.max(sorszamok) AS max_sequence
    WHERE c.sequence < max_sequence AND NOT (c)-[:NEXT_CHUNK]->()
    RETURN d.title AS Dokumentum, c.id AS HibasChunkID, c.sequence AS Sorszam
    """, 
    
    """
    MATCH (c:Chunk)
    WITH count(c) AS OsszesChunk, avg(size(c.text)) AS AtlagosChunkHossz
    MATCH (d:Document)
    RETURN count(d) AS OsszesDokumentum, OsszesChunk, round(AtlagosChunkHossz) AS AtlagosChunkKarakterhossz
    """, 
    
    
    """
    MATCH (europe:Region {name: 'Európa'})
    MATCH (c:Country)-[:LOCATED_IN*1..]->(europe)
    OPTIONAL MATCH (cg:CompanyGroup)-[:GROUP_HQ_IN]->(c)
    OPTIONAL MATCH (tb:TruckBrand)-[:HEADQUARTERED_IN]->(c)
    RETURN count(DISTINCT cg) AS VallalatcsoportokSzama, count(DISTINCT tb) AS MarkakSzama
    """, 
    
    """
    MATCH (scania:TruckBrand {name: 'Scania'})
    MATCH (scania)<-[:OWNS*1..5]-(parent:CompanyGroup)-[:OWNS*1..5]->(sibling:TruckBrand)
    WHERE sibling <> scania
    RETURN DISTINCT sibling.name AS TestverMarka
    """, 
    
    """
    MATCH (cg:CompanyGroup)-[:OWNS*1..5]->(tb:TruckBrand)
    RETURN cg.name AS Vallalatcsoport, count(DISTINCT tb) AS OsszesMelysegiMarka
    ORDER BY OsszesMelysegiMarka DESC
    """
]

"""
3.: MATCH (d:Document)-[:CONTAINS]->(c:Chunk)
WHERE NOT (c)-[:NEXT_CHUNK]->()
WITH d, c, count(c) as x
MATCH (d)-[:CONTAINS]->(last_c:Chunk)
WITH d, c, max(last_c.sequence) as max_seq
WHERE c.sequence < max_seq
RETURN d.title AS Dokumentum, c.id AS MegszakadtChunk, c.sequence AS Sorszam
"""
