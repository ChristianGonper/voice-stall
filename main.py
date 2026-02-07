import os
import sys
import threading
import time
import tkinter as tk
import ctypes

import pyautogui
import pyperclip
from pynput import keyboard

from recorder import AudioRecorder
from engine import STTEngine


class VoiceStallApp:
    def __init__(self):
        # Inicialización de componentes
        self.recorder = AudioRecorder()
        # Intentamos usar CUDA con float16 para máximo rendimiento con tu A5070
        self.engine = STTEngine(model_size="large-v3-turbo", device="cuda", compute_type="float16")
        self.is_recording = False
        self.is_processing = False
        self.icon_image = None
        self.logo_image = None

        # Configuración de la GUI (Tkinter)
        self.root = tk.Tk()
        self.root.title("Voice Stall")
        self.root.geometry("344x136+20+20")
        self.root.overrideredirect(False)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.97)
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self.shutdown)

        # Minimal Pro: neutros elegantes + acentos funcionales
        self.bg_color = "#0A0D11"
        self.frame_color = "#10161E"
        self.header_color = "#141C26"
        self.border_idle = "#2B3A4E"
        self.idle_color = "#95A8C4"
        self.recording_color = "#FF6B72"
        self.processing_color = "#F0B25F"
        self.text_color = "#EAF1FE"
        self.subtitle_color = "#9EACC2"
        self.hotkey_bg = "#1A2434"
        self.hotkey_fg = "#C8D5EA"
        self.brand_color = "#8FB7FF"
        self.accent_idle = "#3E74B8"

        self.root.configure(bg=self.bg_color)
        self.configure_icon()

        self.outer_frame = tk.Frame(self.root, bg="#06080C", padx=1, pady=1)
        self.outer_frame.pack(expand=True, fill="both")

        self.main_frame = tk.Frame(
            self.outer_frame,
            bg=self.frame_color,
            highlightthickness=1,
            highlightbackground=self.border_idle,
        )
        self.main_frame.pack(expand=True, fill="both")

        # Header premium: marca + modo + arrastre
        self.header = tk.Frame(self.main_frame, bg=self.header_color, height=44)
        self.header.pack(fill="x", side="top")
        self.header.pack_propagate(False)

        self.header_left = tk.Frame(self.header, bg=self.header_color)
        self.header_left.pack(side="left", padx=10, pady=6)

        self.logo_label = tk.Label(
            self.header_left,
            image=self.logo_image,
            text="" if self.logo_image else "VS",
            fg=self.brand_color,
            bg=self.header_color,
            font=("Bahnschrift SemiBold", 11),
        )
        self.logo_label.pack(side="left", padx=(0, 8))

        self.brand_block = tk.Frame(self.header_left, bg=self.header_color)
        self.brand_block.pack(side="left")

        self.title_label = tk.Label(
            self.brand_block,
            text="Voice Stall",
            fg=self.text_color,
            bg=self.header_color,
            font=("Bahnschrift SemiBold", 11),
        )
        self.title_label.pack(anchor="w")

        self.subtitle_label = tk.Label(
            self.brand_block,
            text="Minimal Pro",
            fg="#7D8CA4",
            bg=self.header_color,
            font=("Bahnschrift", 8),
        )
        self.subtitle_label.pack(anchor="w")

        self.header_right = tk.Frame(self.header, bg=self.header_color)
        self.header_right.pack(side="right", padx=(0, 10), pady=7)

        self.mode_badge = tk.Label(
            self.header_right,
            text="IDLE",
            fg=self.hotkey_fg,
            bg=self.hotkey_bg,
            font=("Bahnschrift SemiBold", 8),
            padx=8,
            pady=2,
        )
        self.mode_badge.pack(side="left", padx=(0, 8))

        self.drag_hint = tk.Label(
            self.header_right,
            text="⋮⋮",
            fg="#5F6E87",
            bg=self.header_color,
            font=("Bahnschrift", 10),
        )
        self.drag_hint.pack(side="left")

        # Línea de acento superior
        self.accent_line = tk.Frame(self.main_frame, bg=self.accent_idle, height=2)
        self.accent_line.pack(fill="x", side="top")

        # Contenido principal inferior
        self.status_container = tk.Frame(self.main_frame, bg=self.frame_color)
        self.status_container.pack(expand=True, fill="both", padx=12, pady=(10, 9))

        self.indicator = tk.Label(
            self.status_container,
            text="●",
            fg=self.idle_color,
            bg=self.frame_color,
            font=("Bahnschrift SemiBold", 14),
        )
        self.indicator.pack(side="left", anchor="n", pady=(1, 0))

        self.status_text_block = tk.Frame(self.status_container, bg=self.frame_color)
        self.status_text_block.pack(side="left", fill="x", expand=True, padx=(8, 8))

        self.status_text = tk.Label(
            self.status_text_block,
            text="Listo para dictar",
            fg=self.subtitle_color,
            bg=self.frame_color,
            font=("Bahnschrift SemiBold", 10),
        )
        self.status_text.pack(anchor="w")

        self.hint_text = tk.Label(
            self.status_text_block,
            text="Pulsa Ctrl + Alt + S para iniciar",
            fg="#7E8EA8",
            bg=self.frame_color,
            font=("Bahnschrift", 8),
        )
        self.hint_text.pack(anchor="w", pady=(1, 0))

        self.hotkey_badge = tk.Label(
            self.status_container,
            text="Ctrl + Alt + S",
            fg=self.hotkey_fg,
            bg=self.hotkey_bg,
            font=("Bahnschrift SemiBold", 8),
            padx=8,
            pady=3,
        )
        self.hotkey_badge.pack(side="right", anchor="center")

        # Soporte para arrastrar
        for widget in (
            self.outer_frame,
            self.main_frame,
            self.header,
            self.header_left,
            self.logo_label,
            self.brand_block,
            self.title_label,
            self.subtitle_label,
            self.header_right,
            self.mode_badge,
            self.drag_hint,
            self.status_container,
            self.indicator,
            self.status_text_block,
            self.status_text,
            self.hint_text,
            self.hotkey_badge,
        ):
            widget.bind("<Button-1>", self.start_move)
            widget.bind("<B1-Motion>", self.do_move)

        # Hotkey global: Ctrl + Alt + S
        self.hotkey_listener = keyboard.GlobalHotKeys({"<ctrl>+<alt>+s": self.toggle_dictation})
        self.hotkey_listener.start()
        self.root.after(0, self.configure_taskbar_visibility)

        print("Voice Stall iniciado localmente.")
        print("Atajo: Ctrl + Alt + S")

    def configure_icon(self):
        base_dir = os.path.dirname(__file__)
        icon_png_path = os.path.join(base_dir, "voice_stall_icon.png")
        icon_ico_path = os.path.join(base_dir, "voice_stall_icon.ico")

        try:
            # Icono nativo de Windows (barra de tareas y ventana)
            if sys.platform == "win32" and os.path.exists(icon_ico_path):
                self.root.iconbitmap(default=icon_ico_path)
        except Exception as e:
            print(f"No se pudo cargar el icono .ico: {e}")

        try:
            if not os.path.exists(icon_png_path):
                print(f"Icono no encontrado: {icon_png_path}")
                return
            self.icon_image = tk.PhotoImage(file=icon_png_path)
            self.root.iconphoto(True, self.icon_image)
            self.logo_image = self.icon_image.subsample(14, 14)
        except Exception as e:
            print(f"No se pudo cargar el icono .png: {e}")

    def configure_taskbar_visibility(self):
        if sys.platform != "win32":
            return

        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("VoiceStall.App")
            hwnd = self.root.winfo_id()
            GWL_EXSTYLE = -20
            WS_EX_TOOLWINDOW = 0x00000080
            WS_EX_APPWINDOW = 0x00040000
            exstyle = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            exstyle = (exstyle & ~WS_EX_TOOLWINDOW) | WS_EX_APPWINDOW
            ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, exstyle)
            self.root.withdraw()
            self.root.after(10, self.root.deiconify)
        except Exception as e:
            print(f"No se pudo configurar la barra de tareas: {e}")

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay

        # Mantener overlay dentro de la pantalla
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        win_w = self.root.winfo_width()
        win_h = self.root.winfo_height()
        x = max(0, min(x, screen_w - win_w))
        y = max(0, min(y, screen_h - win_h))

        self.root.geometry(f"+{x}+{y}")

    def update_ui(self, status):
        if status == "idle":
            self.indicator.config(fg=self.idle_color, text="●")
            self.status_text.config(text="Listo para dictar", fg=self.subtitle_color)
            self.hint_text.config(text="Pulsa Ctrl + Alt + S para iniciar", fg="#7E8EA8")
            self.main_frame.config(highlightbackground=self.border_idle)
            self.accent_line.config(bg=self.accent_idle)
            self.hotkey_badge.config(fg=self.hotkey_fg, bg=self.hotkey_bg)
            self.mode_badge.config(text="IDLE", fg=self.hotkey_fg, bg=self.hotkey_bg)
        elif status == "recording":
            self.indicator.config(fg=self.recording_color, text="●")
            self.status_text.config(text="Dictando en vivo...", fg=self.recording_color)
            self.hint_text.config(text="Pulsa Ctrl + Alt + S para detener", fg="#EAA7AA")
            self.main_frame.config(highlightbackground=self.recording_color)
            self.accent_line.config(bg=self.recording_color)
            self.hotkey_badge.config(fg="#FFD8D9", bg="#3A1D24")
            self.mode_badge.config(text="REC", fg="#FFD8D9", bg="#3A1D24")
        elif status == "processing":
            self.indicator.config(fg=self.processing_color, text="●")
            self.status_text.config(text="Procesando audio...", fg=self.processing_color)
            self.hint_text.config(text="Transcribiendo y pegando texto", fg="#EBCF9E")
            self.main_frame.config(highlightbackground=self.processing_color)
            self.accent_line.config(bg=self.processing_color)
            self.hotkey_badge.config(fg="#FFE8BC", bg="#3A2B14")
            self.mode_badge.config(text="PROC", fg="#FFE8BC", bg="#3A2B14")

    def toggle_dictation(self):
        if self.is_processing:
            return

        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        started = self.recorder.start_recording()
        if not started:
            self.is_recording = False
            self.root.after(0, lambda: self.update_ui("idle"))
            return

        self.is_recording = True
        self.root.after(0, lambda: self.update_ui("recording"))

    def stop_recording(self):
        self.is_recording = False
        self.is_processing = True
        self.root.after(0, lambda: self.update_ui("processing"))

        audio_file = self.recorder.stop_recording()
        if not audio_file:
            self.is_processing = False
            self.root.after(0, lambda: self.update_ui("idle"))
            return

        threading.Thread(target=self.process_audio, args=(audio_file,), daemon=True).start()

    def process_audio(self, audio_file):
        try:
            if not audio_file or not os.path.exists(audio_file):
                return

            text = self.engine.transcribe(audio_file)
            if text:
                # Respaldo de seguridad local para evitar pérdida de datos
                try:
                    with open("backup_dictado.txt", "w", encoding="utf-8") as f:
                        f.write(text)
                except Exception as backup_error:
                    print(f"Error al guardar respaldo: {backup_error}")

                pyperclip.copy(text)
                time.sleep(0.1)
                pyautogui.hotkey("ctrl", "v")
                pyautogui.press("space")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            if audio_file and os.path.exists(audio_file):
                os.remove(audio_file)
            self.is_processing = False
            self.root.after(0, lambda: self.update_ui("idle"))

    def shutdown(self):
        try:
            if self.is_recording:
                self.recorder.stop_recording()
        except Exception as e:
            print(f"Error al detener grabación: {e}")

        try:
            self.hotkey_listener.stop()
        except Exception as e:
            print(f"Error al detener hotkey listener: {e}")

        try:
            self.recorder.cleanup()
        except Exception as e:
            print(f"Error al limpiar audio: {e}")

        self.root.destroy()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = VoiceStallApp()
    app.run()

