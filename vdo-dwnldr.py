import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os
import sys
import platform

def install_or_update_yt_dlp():
    """Verifica se yt-dlp está instalado; se sim, atualiza; senão, tenta instalar."""
    try:
        subprocess.run(["yt-dlp", "--version"], capture_output=True, check=True)
        # Atualiza yt-dlp para evitar erros com sites
        subprocess.run(["yt-dlp", "-U"], check=True)
        return True
    except FileNotFoundError:
        if platform.system() == "Windows":
            try:
                subprocess.run(["winget", "install", "-e", "--id", "yt-dlp.yt-dlp"], check=True)
                return True
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao instalar yt-dlp com winget:\n{e}")
        else:
            messagebox.showwarning(
                "Instalação necessária",
                "yt-dlp não encontrado. Instale manualmente com:\n\npip install -U yt-dlp"
            )
        return False

def select_cookies():
    file_path = filedialog.askopenfilename(
        title="Selecione o arquivo de cookies",
        filetypes=[("Arquivos de cookies", "*.txt"), ("Todos os arquivos", "*.*")]
    )
    if file_path:
        cookies_entry.delete(0, tk.END)
        cookies_entry.insert(0, file_path)

def select_output():
    file_path = filedialog.asksaveasfilename(
        title="Salvar como",
        defaultextension=".mp4",
        filetypes=[("Vídeo MP4", "*.mp4")]
    )
    if file_path:
        output_entry.delete(0, tk.END)
        output_entry.insert(0, file_path)

def download_video():
    url = url_entry.get().strip()
    output = output_entry.get().strip()
    cookies = cookies_entry.get().strip()

    if not url or not output:
        messagebox.showerror("Erro", "URL e caminho de saída são obrigatórios.")
        return

    if not url.startswith("http"):
        messagebox.showerror("Erro", "URL inválida.")
        return

    if cookies and not os.path.exists(cookies):
        messagebox.showerror("Erro", "Arquivo de cookies não encontrado.")
        return

    if not output.endswith(".mp4"):
        output += ".mp4"

    command = [
        "yt-dlp",
    ]

    if cookies:
        command.extend(["--cookies", cookies])

    command.extend([
        "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36",
        "--no-check-certificate",
        "--extractor-args", "generic:impersonate",
        "-f", "b",
        "--merge-output-format", "mp4",
        url,
        "-o", output
    ])

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        print(result.stdout)
        messagebox.showinfo("Sucesso", f"Download concluído:\n{output}")
    except subprocess.CalledProcessError as e:
        stderr = e.stderr.lower()
        print(e.stderr)
        if "http error 403" in stderr:
            messagebox.showerror(
                "Erro 403 - Proibido",
                "Erro 403 ao tentar baixar o vídeo.\n"
                "Isso pode ser causado por proteção anti-bot do site ou bloqueio de rede.\n"
                "Tente usar cookies válidos, alterar sua rede ou configurar proxy/vpn."
            )
        else:
            messagebox.showerror("Erro", f"Erro ao baixar o vídeo:\n{e.stderr}")

# Verifica instalação e atualização
if not install_or_update_yt_dlp():
    sys.exit(1)

# GUI
root = tk.Tk()
root.title("Download de vídeos - yt-dlp GUI")
root.geometry("460x320")
root.resizable(False, False)

# Link do vídeo
tk.Label(root, text="Link do vídeo:").pack(pady=(10, 0))
url_entry = tk.Entry(root, width=60)
url_entry.pack()

# Caminho de saída
tk.Label(root, text="Salvar como (video.mp4):").pack(pady=(10, 0))
output_frame = tk.Frame(root)
output_frame.pack()
output_entry = tk.Entry(output_frame, width=45)
output_entry.pack(side=tk.LEFT, padx=(0, 5))
tk.Button(output_frame, text="Selecionar", command=select_output).pack(side=tk.LEFT)

# Cookies (opcional)
tk.Label(root, text="Arquivo de cookies (.txt) [opcional]:").pack(pady=(10, 0))
cookies_frame = tk.Frame(root)
cookies_frame.pack()
cookies_entry = tk.Entry(cookies_frame, width=45)
cookies_entry.pack(side=tk.LEFT, padx=(0, 5))
tk.Button(cookies_frame, text="Selecionar", command=select_cookies).pack(side=tk.LEFT)

# Botão de download
tk.Button(
    root,
    text="Download",
    command=download_video,
    bg="#4CAF50",
    fg="white",
    height=2,
    width=20
).pack(pady=20)

# Inicia a GUI
root.mainloop()
