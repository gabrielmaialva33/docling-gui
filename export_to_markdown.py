from docling.document_converter import DocumentConverter

source = "https://pub-aeffe9170abb4d33b96ae4fb7cb1621b.r2.dev/uploads/2025/03/26/1743042576980-w1kiob2r-monografia_felipe_2024.pdf"
converter = DocumentConverter()
result = converter.convert(source)
with open('output.md', 'w') as f:
    f.write(result.document.export_to_markdown())
