# Étude de cas — TENSIL, lampe articulée en studio

| Rubrique | Contenu |
|---|---|
| Contexte | Projet personnel de portfolio. Aucun client, marque fictive. |
| Objectif | Montrer la chaîne complète d'un objet produit en 3D : modélisation, matériaux, éclairage, rendus, animation, asset web optimisé. |
| Démarche | Brief validé → blocage clay → modèle et rig scriptés → 4 coloris testés → studio et caméras → rendus finaux → animation → export GLB compressé → documentation. Chaque étape vérifiée par un rendu de contrôle. |
| Mon rôle | Choix du concept (lampe à ressorts), du public, du style packshot, de l'animation (dépliement + allumage), du coloris graphite et du nom TENSIL ; validation des étapes. |
| Rôle de l'IA | Claude (Opus 5.5, Claude Code) a écrit et exécuté les scripts Python Blender, réglé lumières et cadrages à partir des rendus de test, produit les exports et la documentation. Aucune modélisation manuelle dans l'interface Blender. |
| Outils | Blender 5.2.2 LTS (Cycles/OptiX), glTF-Transform 4.5.1, Claude Code. Coût : 0 €. |
| Difficultés | Ressorts qui doivent suivre le bras (contraintes *Stretch To*, puis cuisson des transformations pour le glTF qui ignore les contraintes) ; pose pliée sans collision avec le sol (vérifiée par calcul) ; WebP plus sombres que les PNG (transformation AgX appliquée deux fois, corrigée) ; animation exportée en 8 clips séparés (corrigé en un seul clip). |
| Résultat | 4 images 1080p, animation de 8 s, 3 visuels de processus + vue du plateau, GLB de 203 Ko (~41 k triangles) et version animée de 201 Ko, scène entièrement reproductible en une commande. |
