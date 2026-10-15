# Brief — Lampe articulée TENSIL

> Validé le 2026-10-15.

## Concept
Lampe de bureau articulée à ressorts, design original, marque fictive **TENSIL**. Projet réalisé en duo humain + IA :
- **Elliott** : choix du concept, du style, du public, de la marque ; validation de chaque étape.
- **Claude (IA)** : production 3D par scripts Python Blender (`bpy`) exécutés sans interface, rendus, exports, documentation.

## Public
Mixte : recruteurs (3D / création / dev), clients e-commerce, studios web 3D.

## Intention visuelle
Packshot studio épuré : fond neutre en dégradé, grandes sources douces, objet seul. Dans l'animation, la lumière studio baisse pendant l'allumage pour rendre la lumière émise lisible.

## Livrables
| Livrable | Détail |
|---|---|
| Images finales | 4 : 3/4 héros, profil, gros plan ressort/articulation, lampe allumée |
| Animation | 6–10 s : dépliement puis allumage, MP4 H.264 1080p |
| Processus | wireframe, clay (sans matériau), plan d'éclairage |
| Asset web | GLB optimisé (cible < 3 Mo), animation de dépliement optionnelle |
| Portfolio | vignette de carte, texte de page projet, étude de cas |
| Source | scripts `bpy` + `.blend` généré (non destiné aux visiteurs) |

## Exclu
Site portfolio, lecteur 3D, Remotion/EffectCraft, son, simulations, texture painting, scène de bureau complète, identité de marque complète, cloud, toute dépense.

## Compétences démontrées
Modélisation hard-surface et mécanique, matériaux PBR procéduraux, éclairage studio + émissif, rig et animation produit, composition, optimisation web, **automatisation d'un pipeline 3D par code et IA**, documentation des compromis.

## Références

### Fonctionnement (inspiration uniquement)
| Référence | Ce qu'on en retient | Lien |
|---|---|---|
| Mécanisme à ressorts de George Carwardine (brevet 1932) | Principe d'équilibrage par ressorts et leviers | [Design Museum](https://designmuseum.org/design/anglepoise) |
| Histoire de la lampe Anglepoise (version industrielle à 4 ressorts, version domestique à 3) | Typologie des bras et du nombre de ressorts | [anglepoise.com](https://www.anglepoise.com/about) |

**À ne pas copier :** silhouette, tête et base des modèles Anglepoise, qui sont une marque déposée et des designs connus. TENSIL utilise une silhouette propre : base disque lestée, 2 ressorts par segment, tête conique à réflecteur interne, articulations à flasques.

### Style (inspiration uniquement)
Packshot produit classique : fond « cyclo » (sol et fond fondus sans angle visible), éclairage à grandes sources douces, ombres de contact. Je n'ai collecté aucune image : les rendus seront jugés sur les tests.

### Ressources utilisées directement
| Ressource | Licence | Usage commercial | Attribution | Source |
|---|---|---|---|---|
| Blender 5.2.2 LTS | GPL ; les créations appartiennent à l'auteur | Oui | Non | [blender.org/about/license](https://www.blender.org/about/license/) |
| Police Inter (fournie avec Blender), pour le logo | SIL OFL 1.1 | Oui (sauf vente de la police seule) | Non requise pour un logo converti en maillage | `license/license.md` de Blender, [rsms.me/inter](https://rsms.me/inter/) |
| glTF-Transform CLI 4.5.1 | MIT | Oui | Non | [npm](https://www.npmjs.com/package/@gltf-transform/cli) |

Aucune texture et aucun HDRI externe : tout est procédural. Si un HDRI s'avère nécessaire, ce sera [Poly Haven](https://polyhaven.com/license) (CC0, usage commercial autorisé, sans attribution).

### Nom de marque
- **Recherche indicative** (ce n'est pas un avis juridique) : aucune marque « TENSIL » trouvée dans l'éclairage.
- **Marque proche :** **TENSUL** (USPTO 97708276), déposée en 2022 pour des lampes, statut « new application ». Le risque de confusion est faible pour une marque fictive jamais commercialisée.
- **Non consultés :** l'INPI et l'EUIPO. À faire avant tout usage réel.

## Contraintes
| Sujet | Fait vérifié |
|---|---|
| Matériel | RTX 2050 avec 4 Go de VRAM, Cycles via OptiX : 640×360 à 64 échantillons rendu en 4 s |
| GitHub | Avertissement à partir de 50 Mio, fichier bloqué au-delà de 100 Mio, dépôt conseillé sous 1 Go ([docs](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github)) |
| Coût | 0 € |

## Tâches
| # | Tâche | Résultat attendu |
|---|---|---|
| 1 | Volumes et proportions | Silhouette lisible, rendu clay de contrôle |
| 2 | Modélisation détaillée | Base, bras, ressorts, articulations, tête, câble, logo |
| 3 | Rig | Hiérarchie des pivots, ressorts qui suivent les angles |
| 4 | Matériaux | Laque, métal, caoutchouc, émissif, gravure |
| 5 | Studio et éclairage | Fond cyclo, sources douces, rendus de test |
| 6 | Images finales | 4 PNG et versions WebP |
| 7 | Animation | MP4 de dépliement puis allumage |
| 8 | Visuels du processus | Wireframe, clay, plan d'éclairage |
| 9 | Export web | GLB brut puis optimisé, avec les chiffres (taille, triangles) |
| 10 | Documentation | README, crédits, coûts, étude de cas, texte portfolio |
| 11 | Contrôle final | Livrables comparés au brief |
