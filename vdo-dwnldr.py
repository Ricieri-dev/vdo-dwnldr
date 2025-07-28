import customtkinter as ctk
from tkinter import filedialog, messagebox
import subprocess
import os
import sys
import platform
import threading
import re

def install_or_update_yt_dlp():
    try:
        subprocess.run(["yt-dlp", "--version"], capture_output=True, check=True)
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

def start_download_thread():
    threading.Thread(target=download_video).start()

def select_output():
    file_path = filedialog.asksaveasfilename(
        title="Salvar como",
        defaultextension=".mp4",
        filetypes=[("Vídeo MP4", "*.mp4")]
    )
    if file_path:
        output_entry.delete(0, ctk.END)
        output_entry.insert(0, file_path)

def download_video():
    url = url_entry.get().strip()
    output = output_entry.get().strip()

    if not url or not output:
        messagebox.showerror("Erro", "URL e caminho de saída são obrigatórios.")
        return

    if not url.startswith("http"):
        messagebox.showerror("Erro", "URL inválida.")
        return

    if not output.endswith(".mp4"):
        output += ".mp4"

    progress_label.configure(text="0%")
    progress.set(0)

    command = [
        "yt-dlp",
        "--newline",  # necessário para imprimir progresso linha a linha
        "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36",
        "--no-check-certificate",
        "--extractor-args", "generic:impersonate",
        "-f", "b",
        "--merge-output-format", "mp4",
        "-o", output,
        url
    ]

    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

        for line in process.stdout:
            print(line.strip())
            match = re.search(r"\[download\]\s+(\d{1,3}\.\d)%", line)
            if match:
                percent = float(match.group(1))
                progress.set(percent / 100)
                progress_label.configure(text=f"{percent:.1f}%")
            app.update_idletasks()

        process.wait()

        if process.returncode == 0:
            messagebox.showinfo("Sucesso", f"Download concluído:\n{output}")
        else:
            messagebox.showerror("Erro", "Erro ao baixar o vídeo.")

    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro:\n{e}")
    finally:
        progress_label.configure(text="")

# Verifica instalação do yt-dlp
if not install_or_update_yt_dlp():
    sys.exit(1)

# Configura estilo do customtkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# GUI principal
app = ctk.CTk()
app.title("Download de vídeos - yt-dlp GUI")
app.geometry("500x400")
app.resizable(False, False)

# Campo URL
ctk.CTkLabel(app, text="Link do vídeo:").pack(pady=(10, 0))
url_entry = ctk.CTkEntry(app, width=460)
url_entry.pack(pady=5)

# Campo caminho de saída
ctk.CTkLabel(app, text="Salvar como (video.mp4):").pack(pady=(10, 0))
frame_saida = ctk.CTkFrame(app)
frame_saida.pack(pady=5)
output_entry = ctk.CTkEntry(frame_saida, width=360)
output_entry.pack(side="left", padx=(0, 10), pady=5)
ctk.CTkButton(frame_saida, text="Selecionar", command=select_output).pack(side="left")

# Botão de download
ctk.CTkButton(app, text="Download", command=start_download_thread, width=200).pack(pady=20)

# Barra de progresso + texto %
progress = ctk.CTkProgressBar(app, orientation="horizontal", width=400, mode="determinate")
progress.set(0)
progress.pack(pady=(10, 2))
progress_label = ctk.CTkLabel(app, text="", font=ctk.CTkFont(size=14))
progress_label.pack()

# Inicia o app
app.mainloop()
