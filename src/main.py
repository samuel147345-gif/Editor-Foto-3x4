# -*- coding: utf-8 -*-
"""
Editor de Fotos 3x4
By Samuel Fernandes
Versão 3.1.0 - Melhorias UX Borda + Versão na Interface
"""

import sys
import os
import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageTk
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules'))

from modules.gui_components import ControlPanel, ImageCanvas
from modules.cs_bridge import get_cs_bridge, is_cs_available
from modules.face_detection import expand_and_pad_face_crop
from modules.file_manager import FileManager
from modules.utils import get_image_name_from_path
from modules.config_manager import get_config_manager

try:
    from modules.image_processing_hybrid import (
        enforce_3x4, apply_image_enhancements, 
        resize_image, add_border, compute_initial_scale,
        get_performance_info
    )
    HYBRID_MODE = True
except ImportError:
    from modules.image_processing import (
        enforce_3x4, apply_image_enhancements, 
        resize_image, add_border, compute_initial_scale
    )
    HYBRID_MODE = False

VERSION = Path("../version.txt").read_text().strip().lstrip('v') if Path("../version.txt").exists() else "3.1.0"

MAX_DIMENSION = 4000
MAX_IMAGES = 50

class PhotoEditor(ctk.CTk):
    """Editor de Fotos 3x4"""
    
    def __init__(self):
        super().__init__()
        self.title(f"Editor de Fotos 3x4 - v{VERSION}")
        self.geometry("900x650")
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Config Manager
        self.config_mgr = get_config_manager()
        
        # Estado
        self.image_paths = []
        self.original_images = []
        self.processed_images = []
        self.current_index = 0
        self.crop_box = None
        self.tk_image = None
        self.zoom_memory = {}
        
        # Variáveis controle
        self.contrast_var = tk.DoubleVar(value=1.0)
        self.brightness_var = tk.DoubleVar(value=1.0)
        self.quality_var = tk.IntVar(value=100)
        self.scale_var = tk.DoubleVar(value=1.0)
        
        # CARREGAR ESTADO BORDA DA CONFIG
        border_saved = self.config_mgr.get("border_enabled", False)
        self.border_var = tk.BooleanVar(value=border_saved)
        
        self.replace_var = tk.BooleanVar(value=self.config_mgr.get("replace_original", False))
        
        self.setup_ui()
        self.setup_shortcuts()
    
    def setup_ui(self):
        """Configura interface"""
        self.canvas = ImageCanvas(self, on_selection=self.on_crop_selection)
        self.canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        self.control_panel = ControlPanel(
            self,
            callbacks={
                'open_images': self.open_images,
                'prev_image': self.prev_image,
                'next_image': self.next_image,
                'crop_selection': self.crop_selection,
                'revert_current': self.reset_image,
                'remove_current': self.remove_current,
                'auto_crop_face': self.auto_crop_face,
                'apply_changes': self.apply_changes,
                'save_image': self.save_image,
                'save_all': self.save_all_images
            },
            contrast_var=self.contrast_var,
            brightness_var=self.brightness_var,
            quality_var=self.quality_var,
            scale_var=self.scale_var,
            border_var=self.border_var,
            replace_var=self.replace_var,
            on_border_change=self.on_border_change  # CALLBACK BORDA
        )
        self.control_panel.pack(side="right", fill="y", padx=10, pady=10)
        
        # Barra Status
        self.status_bar = ctk.CTkFrame(self, height=25)
        self.status_bar.pack(side="bottom", fill="x", padx=10, pady=(0,10))
        
        self.status_label = ctk.CTkLabel(
            self.status_bar, text="Nenhuma imagem carregada", anchor="w"
        )
        self.status_label.pack(side="left", padx=10)
        
        # LABEL VERSÃO
        self.version_label = ctk.CTkLabel(
            self.status_bar, text=f"v{VERSION}", anchor="e", 
            font=("Arial", 9), text_color="gray60"
        )
        self.version_label.pack(side="right", padx=10)
        
        self.update_status()
    
    def setup_shortcuts(self):
        """Atalhos teclado"""
        self.bind("<Control-o>", lambda e: self.open_images())
        self.bind("<Control-s>", lambda e: self.save_image())
        self.bind("<Control-Shift-S>", lambda e: self.save_all_images())
        self.bind("<Left>", lambda e: self.prev_image())
        self.bind("<Right>", lambda e: self.next_image())
        self.bind("<Control-z>", lambda e: self.reset_image())
    
    def on_border_change(self):
        """Callback quando borda é alterada - APLICAÇÃO AUTOMÁTICA"""
        # Salvar estado
        self.config_mgr.set("border_enabled", self.border_var.get())
        
        # Aplicar automaticamente
        if self.processed_images:
            self.refresh_preview()
    
    def update_status(self):
        """Atualiza barra status"""
        if not self.image_paths:
            self.status_label.configure(text="Nenhuma imagem carregada")
            return
        
        total = len(self.image_paths)
        current = self.current_index + 1
        name = get_image_name_from_path(self.image_paths[self.current_index])
        self.status_label.configure(text=f"[{current}/{total}] {name}")
    
    def open_images(self):
        """Abre imagens"""
        paths = FileManager.open_images()
        if not paths:
            return
        
        if len(paths) > MAX_IMAGES:
            messagebox.showwarning("Limite", f"Máximo {MAX_IMAGES} imagens por sessão.")
            paths = paths[:MAX_IMAGES]
        
        self.image_paths = paths
        self.original_images = []
        self.processed_images = []
        self.zoom_memory = {}
        
        for p in paths:
            try:
                img = Image.open(p).convert("RGB")
                if max(img.size) > MAX_DIMENSION:
                    img.thumbnail((MAX_DIMENSION, MAX_DIMENSION), Image.LANCZOS)
                self.original_images.append(img.copy())
                self.processed_images.append(img.copy())
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao abrir {p}:\n{str(e)}")
        
        if self.processed_images:
            self.current_index = 0
            self.load_current_image()
    
    def load_current_image(self):
        """Carrega imagem atual"""
        if not self.processed_images:
            return
        
        # Restaurar zoom
        if self.current_index in self.zoom_memory:
            self.scale_var.set(self.zoom_memory[self.current_index])
        else:
            img = self.processed_images[self.current_index]
            scale = compute_initial_scale(img, 800, 650)
            self.scale_var.set(scale)
            self.zoom_memory[self.current_index] = scale
        
        self.refresh_preview()
        self.update_status()
    
    def refresh_preview(self):
        """Atualiza preview"""
        if not self.processed_images:
            return
        
        img = self.processed_images[self.current_index].copy()
        
        # APLICAR BORDA SE ATIVADA
        if self.border_var.get():
            img = add_border(img, border_width=5, border_color="black")
        
        scale = self.scale_var.get()
        display_img = resize_image(img, scale)
        
        self.tk_image = ImageTk.PhotoImage(display_img)
        self.canvas.delete("all")
        
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        if cw < 10:
            cw = 800
        if ch < 10:
            ch = 650
        
        x = cw // 2
        y = ch // 2
        self.canvas.create_image(x, y, image=self.tk_image)
    
    def prev_image(self):
        """Imagem anterior"""
        if not self.processed_images:
            return
        self.current_index = (self.current_index - 1) % len(self.processed_images)
        self.load_current_image()
    
    def next_image(self):
        """Próxima imagem"""
        if not self.processed_images:
            return
        self.current_index = (self.current_index + 1) % len(self.processed_images)
        self.load_current_image()
    
    def on_crop_selection(self, box):
        """Callback seleção crop"""
        if not self.processed_images:
            return
        
        img = self.processed_images[self.current_index]
        scale = self.scale_var.get()
        
        x0 = int(box[0] / scale)
        y0 = int(box[1] / scale)
        x1 = int(box[2] / scale)
        y1 = int(box[3] / scale)
        
        self.crop_box = enforce_3x4((x0, y0, x1, y1), img.size)
    
    def crop_selection(self):
        """Corta seleção"""
        if not self.crop_box:
            messagebox.showinfo("Info", "Nenhuma seleção para cortar.")
            return
        
        img = self.processed_images[self.current_index]
        self.processed_images[self.current_index] = img.crop(self.crop_box)
        self.crop_box = None
        self.load_current_image()
    
    def remove_current(self):
        """Remove imagem"""
        if not self.processed_images:
            return
        
        if len(self.processed_images) == 1:
            self.processed_images.clear()
            self.original_images.clear()
            self.image_paths.clear()
            self.current_index = 0
            self.zoom_memory.clear()
            self.canvas.delete("all")
            self.update_status()
            messagebox.showinfo("Info", "Última imagem removida.")
            return
        
        del self.processed_images[self.current_index]
        del self.original_images[self.current_index]
        del self.image_paths[self.current_index]
        
        if self.current_index in self.zoom_memory:
            del self.zoom_memory[self.current_index]
        
        if self.current_index >= len(self.processed_images):
            self.current_index = len(self.processed_images) - 1
        
        self.load_current_image()
    
    def auto_crop_face(self):
        """Crop facial automático"""
        try:
            path = self.image_paths[self.current_index]
            result = expand_and_pad_face_crop(path)
            
            if result:
                self.processed_images[self.current_index] = result
                self.load_current_image()
            else:
                messagebox.showwarning(
                    "Face Não Detectada", 
                    "Nenhuma face detectada.\nUse crop manual."
                )
        except Exception as e:
            messagebox.showerror("Erro", f"Erro detecção facial:\n{str(e)}")
    
    def apply_changes(self):
        """Aplica alterações (SEM BORDA)"""
        if not self.processed_images:
            return
        
        img = self.processed_images[self.current_index].copy()
        
        img = apply_image_enhancements(
            img,
            contrast=self.contrast_var.get(),
            brightness=self.brightness_var.get(),
            quality=self.quality_var.get()
        )
        
        # BORDA NÃO É APLICADA AQUI, APENAS NO PREVIEW
        
        self.processed_images[self.current_index] = img
        self.refresh_preview()
    
    def reset_image(self):
        """Reseta imagem"""
        if self.processed_images:
            self.processed_images[self.current_index] = self.original_images[self.current_index].copy()
            self.load_current_image()
    
    def save_image(self):
        """Salva imagem atual"""
        if not self.processed_images:
            messagebox.showinfo("Info", "Nenhuma imagem para salvar.")
            return
        
        try:
            img = self.processed_images[self.current_index].copy()
            
            # APLICAR BORDA SE ATIVADA
            if self.border_var.get():
                img = add_border(img, border_width=5, border_color="black")
            
            path = self.image_paths[self.current_index]
            
            if self.replace_var.get():
                output_path = path
            else:
                output_path = FileManager.save_single_image(img, path)
            
            if output_path:
                img.save(output_path, quality=self.quality_var.get())
                messagebox.showinfo("Sucesso", f"Salva em:\n{output_path}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar:\n{str(e)}")
    
    def save_all_images(self):
        """Salva todas as imagens"""
        if not self.processed_images:
            messagebox.showinfo("Info", "Nenhuma imagem para salvar.")
            return
        
        try:
            saved_count = 0
            for i, img in enumerate(self.processed_images):
                img_copy = img.copy()
                
                # APLICAR BORDA SE ATIVADA
                if self.border_var.get():
                    img_copy = add_border(img_copy, border_width=5, border_color="black")
                
                path = self.image_paths[i]
                
                if self.replace_var.get():
                    output_path = path
                else:
                    output_path = FileManager.save_single_image(img_copy, path)
                
                if output_path:
                    img_copy.save(output_path, quality=self.quality_var.get())
                    saved_count += 1
            
            messagebox.showinfo("Sucesso", f"{saved_count} imagens salvas!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar:\n{str(e)}")
    
    def on_close(self):
        """Fecha aplicação"""
        if messagebox.askokcancel("Sair", "Deseja sair?"):
            self.destroy()

if __name__ == "__main__":
    app = PhotoEditor()
    app.mainloop()
        