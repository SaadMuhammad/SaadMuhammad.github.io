---
title: "Your article title"
date: 2026-11-06
slug: your-article-slug
description: "A short introduction for the article card and search engines."
tags: [Engineering, Agents]
draft: true
---

Write the introduction here. Copy this file to `content/articles/`, set a unique slug and date, and change `draft` to `false` when ready.

## The problem

Explain the problem in your own words.

## An image

![Describe the image for readers](/images/your-image.png)

## An architecture diagram

```mermaid
flowchart TD
    A[Question] --> B[Retrieve sources]
    B --> C[Generate answer]
    C --> D{Evidence sufficient?}
    D -->|Yes| E[Answer with citations]
    D -->|No| F[Ask for clarification]
```

## Code

```python
def answer(question: str) -> str:
    return "Replace this example with your code."
```

## Results

| Measure | Before | After |
| --- | --- | --- |
| Your measure | Value | Value |

## What I learned

Add your conclusion and references.
