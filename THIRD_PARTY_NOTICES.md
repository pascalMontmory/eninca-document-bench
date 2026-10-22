# Third-party components / Composants tiers

This prototype combines existing components with original ENINCA integration code. It does not claim to have invented or trained the embedding model, mean pooling, cosine retrieval or centroid classification.

Ce prototype combine des composants existants et du code d'intégration original ENINCA. Il ne revendique pas la création ou l'entraînement du modèle d'embeddings, du pooling moyen, de la recherche cosinus ou du classement par centroïdes.

| Component / Composant | License / Licence | Source |
|---|---|---|
| Sentence Transformers multilingual MiniLM model, tokenizer and model card | Apache-2.0, as declared by its authors / selon ses auteurs | [Pinned upstream repository / Dépôt figé](https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2/tree/ae06c001a2546bef168b9bf8f570ccb1a16aaa27) |
| NumPy | BSD-3-Clause | [NumPy license](https://github.com/numpy/numpy/blob/main/LICENSE.txt) |
| ONNX Runtime | MIT | [ONNX Runtime license](https://github.com/microsoft/onnxruntime/blob/main/LICENSE) |
| Hugging Face Tokenizers | Apache-2.0 | [Tokenizers license](https://github.com/huggingface/tokenizers/blob/main/LICENSE) |
| Service Public / DILA practical-information corpus | Licence Ouverte / Open Licence (`fr-lo`) | [Publisher terms / Conditions de l'éditeur](https://www.service-public.gouv.fr/P10004), [per-document attribution / attribution par fiche](data/dila-v1/manifest.json) |

Dependencies are installed separately with their own notices; their transitive dependencies retain their own licenses. The model download is explicit, contains no remote Python code, and remains outside the source package. Consult the upstream model card retained in the model cache. The synthetic French example texts were authored for this prototype and are not customer records.

Les dépendances sont installées séparément avec leurs notices ; leurs dépendances transitives conservent leurs licences. Le téléchargement du modèle est explicite, ne contient aucun code Python distant et reste hors du paquet source. Sa fiche d'origine est conservée dans le cache du modèle. Les exemples français sont fictifs, rédigés pour le prototype et ne proviennent d'aucun client.

Method references / Références de méthode:

- [Sentence Transformers: ONNX execution requires the appropriate pooling and normalization](https://www.sbert.net/docs/sentence_transformer/usage/efficiency.html)
- [Original model: mean pooling and 384-dimensional embeddings](https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2/blob/ae06c001a2546bef168b9bf8f570ccb1a16aaa27/README.md)
- [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0)
