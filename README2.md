# Gráfadatbázis sématerve

## 1. Csomópontok

A gráfban négy fő entitásfajta található, amelyek a való világ egységeit reprezentálják:

| Csomópont | Leírás | Tulajdonság |
| --- | --- | --- |
| `Region` | Földrajzi vagy politikai régiók (pl. kontinensek vagy szubrégiók). | `name` (a régió neve) |
| `Country` | Konkrét országok, amelyek valamilyen régióhoz tartoznak. | `name` (az ország neve) |
| `CompanyGroup` | Felső szintű vállalatcsoportok, holdingok vagy leányvállalat-csoportok. | `name` (a vállalatcsoport neve) |
| `TruckBrand` | Maguk a teherautó-márkák, amelyek a járműveket gyártják. | `name` (a márka neve) |

## 2. Élek

A csomópontok között az alábbi hierarchikus és relációs szabályok érvényesek:

### Földrajzi hierarchia — `LOCATED_IN`

- Egy ország (`Country`) elhelyezkedhet egy régióban (`Region`), például Svédország Nyugat-Európában.
- Egy régió (`Region`) beágyazható egy másik, nagyobb régióba (`Region`), például Nyugat-Európa Európába.

### Vállalati tulajdonosi struktúra — `OWNS`

- Egy vállalatcsoport (`CompanyGroup`) birtokolhat egy másik vállalatcsoportot (`CompanyGroup`), például a Volkswagen Group a Traton Groupot.
- Egy vállalatcsoport (`CompanyGroup`) közvetlenül birtokolhat egy vagy több teherautó-márkát (`TruckBrand`), például a Traton Group a Scaniát és a MAN-t.

### Központok elhelyezkedése

- `GROUP_HQ_IN`: Egy vállalatcsoport (`CompanyGroup`) főhadiszállása egy adott országban (`Country`) található.
- `HEADQUARTERED_IN`: Egy teherautó-márka (`TruckBrand`) operatív vagy történelmi központja egy adott országban (`Country`) található.

## 3. A gráf leírása

A gráfséma célja a globális haszongépjármű-ipar tulajdonosi és földrajzi struktúrájának feltérképezése. A modell alulról felfelé építkezik: a teherautó-márkák (mint a Scania vagy a MAN) vállalatcsoportok tulajdonában állnak, amelyek maguk is alkothatnak többszintű holdingstruktúrát (például a VW Group birtokolja a Tratont, amely a Scaniát birtokolja). A cégek és márkák a főhadiszállásuk révén országokhoz kötődnek. Az országok pedig régiók segítségével tetszőlegesen mély földrajzi hierarchiába rendeződnek (ország → alrégió → kontinens).
