---
layout: page
title: Tools and Datasets
permalink: /tools-and-datasets/
---

## Tools

# XL-LEXEME
![xl-lexeme](/xl-lexeme.png "picture")

You can use XL-LEXEME to encode the meaning of words in specific contexts. It represents the state of the art in semantic change detection.
Described in [WiC Pretrained Model for Cross-Lingual LEXical sEMantic changE](https://aclanthology.org/2023.acl-short.135.pdf)

Available here: [https://github.com/pierluigic/xl-lexeme](https://huggingface.co/pierluigic/xl-lexeme)



# Janus
![janus](/janus-pic.png "picture")
With Janus you can generate sentences in which a word appears with a meaning you choose and in the writing style of the historical period you prefer (1700-200).
Described in Sense-specific Historical Word Usage Generation

Available here: [https://huggingface.co/ChangeIsKey/llama3-janus](https://huggingface.co/ChangeIsKey/llama3-janus)


## Datasets

# GWSD
The GWSD Dataset (Graded Word Sense Disambiguation Dataset) is a sense-annotated dataset designed for studying diachronic word usage and semantic change. It contains:

- 2584 word usages from the Oxford English Dicitonary (OED) and 

- 2584 automatically generated word usage examples.

In particular, the automatically generated word usage are obtained using Janus,  a fine-tuned language model trained on the Oxford English Dictionary (OED), allowing for temporally aligned and sense-specific word usage examples spanning historical periods from 1700–2010. 
Described in Sense-specific Historical Word Usage Generation

Available here: [https://zenodo.org/records/14974455](https://zenodo.org/records/14974455)

# DWUG IT: Diachronic Word Usage Graphs for Italian
DWUG IT provides sense annotations for up to 50 sentences for each time period (1948–1960 and 1970–1990) and for each of the 18 target words. The annotations were performed on the Italian corpus L'Unità.

Available here: [https://ceur-ws.org/Vol-3878/22_main_long.pdf](https://ceur-ws.org/Vol-3878/22_main_long.pdf)


