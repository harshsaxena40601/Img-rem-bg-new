---
name: Replit Python dependency resolution
description: Replit's managed uv installer can generate an overly broad PyTorch index override that breaks Hugging Face package resolution.
---

When the managed Python package installer reports that normal PyPI packages such
as `huggingface-hub` or `transformers` have no compatible versions, inspect
`pyproject.toml` for generated `tool.uv` PyTorch index overrides. The project
can still use Replit's managed `.pythonlibs` environment, but standard `pip`
against the Replit package firewall may be needed as a fallback after the
managed resolver fails.

**Why:** The resolver may route packages that are not hosted on the CPU-only
PyTorch index, or use stale package metadata, even though the package firewall
can download them successfully.

**How to apply:** Keep a clean project dependency declaration, prefer the
managed installer first, and use the direct Python package fallback only when
the resolver failure is reproducible and specific to its generated index data.