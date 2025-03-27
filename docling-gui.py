import os
import threading
import tkinter as tk
import webbrowser
from tkinter import filedialog, scrolledtext, messagebox, ttk

from docling.document_converter import DocumentConverter


class DoclingConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Docling Converter")
        self.root.geometry("800x600")
        self.root.minsize(640, 480)

        # Configurar o conversor
        self.converter = DocumentConverter()

        # Criar o layout
        self.create_widgets()

    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Fonte do caminho de entrada
        input_frame = ttk.LabelFrame(main_frame, text="Fonte do Documento", padding="5")
        input_frame.pack(fill=tk.X, pady=5)

        # Opções de entrada: URL ou Arquivo
        self.input_type = tk.StringVar(value="url")
        ttk.Radiobutton(input_frame, text="URL", variable=self.input_type, value="url").grid(row=0, column=0, padx=5)
        ttk.Radiobutton(input_frame, text="Arquivo Local", variable=self.input_type, value="file").grid(row=0, column=1, padx=5)

        # Campo de entrada
        self.input_var = tk.StringVar()
        self.input_entry = ttk.Entry(input_frame, textvariable=self.input_var, width=60)
        self.input_entry.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        # Botão para procurar arquivo
        self.browse_btn = ttk.Button(input_frame, text="Procurar...", command=self.browse_file)
        self.browse_btn.grid(row=1, column=2, padx=5, pady=5)

        # Botão de conversão
        convert_frame = ttk.Frame(main_frame)
        convert_frame.pack(fill=tk.X, pady=5)

        self.convert_btn = ttk.Button(convert_frame, text="Converter para Markdown", command=self.start_conversion)
        self.convert_btn.pack(pady=10)

        # Barra de progresso
        self.progress = ttk.Progressbar(convert_frame, mode="indeterminate")
        self.progress.pack(fill=tk.X, pady=5)

        # Área de saída
        output_frame = ttk.LabelFrame(main_frame, text="Markdown Gerado", padding="5")
        output_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.output_text = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD)
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Botões de ação
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X, pady=5)

        self.save_btn = ttk.Button(action_frame, text="Salvar Markdown", command=self.save_markdown)
        self.save_btn.pack(side=tk.LEFT, padx=5)

        self.copy_btn = ttk.Button(action_frame, text="Copiar para Área de Transferência", command=self.copy_to_clipboard)
        self.copy_btn.pack(side=tk.LEFT, padx=5)

        self.clear_btn = ttk.Button(action_frame, text="Limpar", command=self.clear_output)
        self.clear_btn.pack(side=tk.RIGHT, padx=5)

        # Rodapé com informações
        footer_frame = ttk.Frame(main_frame)
        footer_frame.pack(fill=tk.X, pady=5)

        footer_text = "Desenvolvido com Docling - Converta facilmente documentos para Markdown"
        footer_label = ttk.Label(footer_frame, text=footer_text)
        footer_label.pack(side=tk.LEFT)

        help_link = ttk.Label(footer_frame, text="Ajuda", foreground="blue", cursor="hand2")
        help_link.pack(side=tk.RIGHT)
        help_link.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/docling-core/docling"))

    def browse_file(self):
        filetypes = (
            ("Documentos PDF", "*.pdf"),
            ("Documentos Word", "*.docx"),
            ("Documentos HTML", "*.html"),
            ("Todos os arquivos", "*.*")
        )
        filename = filedialog.askopenfilename(title="Selecione um arquivo", filetypes=filetypes)
        if filename:
            self.input_var.set(filename)
            self.input_type.set("file")

    def start_conversion(self):
        self.progress.start()
        self.convert_btn.configure(state="disabled")

        # Iniciar conversão em uma thread separada para não bloquear a interface
        conversion_thread = threading.Thread(target=self.convert_document)
        conversion_thread.daemon = True
        conversion_thread.start()

    def convert_document(self):
        try:
            source = self.input_var.get().strip()
            if not source:
                self.show_error("Por favor, forneça uma URL ou caminho de arquivo válido.")
                return

            # Verificar se é um arquivo e se ele existe
            if self.input_type.get() == "file" and not os.path.exists(source):
                self.show_error(f"O arquivo '{source}' não existe.")
                return

            # Realizar a conversão
            result = self.converter.convert(source)
            markdown_text = result.document.export_to_markdown()

            # Atualizar a interface com o resultado
            self.root.after(0, lambda: self.update_output(markdown_text))

        except Exception as e:
            self.root.after(0, lambda: self.show_error(f"Erro ao converter documento: {str(e)}"))
        finally:
            self.root.after(0, self.finish_conversion)

    def update_output(self, text):
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, text)

    def finish_conversion(self):
        self.progress.stop()
        self.convert_btn.configure(state="normal")

    def save_markdown(self):
        if not self.output_text.get(1.0, tk.END).strip():
            messagebox.showinfo("Informação", "Não há conteúdo para salvar.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".md",
            filetypes=[("Markdown", "*.md"), ("Arquivo de texto", "*.txt"), ("Todos os arquivos", "*.*")]
        )

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(self.output_text.get(1.0, tk.END))
                messagebox.showinfo("Sucesso", f"Arquivo salvo com sucesso em:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao salvar arquivo: {str(e)}")

    def copy_to_clipboard(self):
        content = self.output_text.get(1.0, tk.END).strip()
        if not content:
            messagebox.showinfo("Informação", "Não há conteúdo para copiar.")
            return

        self.root.clipboard_clear()
        self.root.clipboard_append(content)
        messagebox.showinfo("Sucesso", "Conteúdo copiado para a área de transferência!")

    def clear_output(self):
        self.output_text.delete(1.0, tk.END)

    def show_error(self, message):
        messagebox.showerror("Erro", message)

def main():
    root = tk.Tk()
    app = DoclingConverterApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
