# -*- coding: utf-8 -*-
"""
Componentes de interface gráfica - Emojis Melhorados + Assinatura
"""
import tkinter as tk
import customtkinter as ctk
from modules.image_processing import enforce_3x4

class ControlPanel(ctk.CTkScrollableFrame):
    """Painel de controle lateral"""
    
    def __init__(self, parent, callbacks, contrast_var, brightness_var, 
                 quality_var, scale_var, border_var, replace_var, on_border_change=None):
        super().__init__(parent, width=280)
        
        self.callbacks = callbacks
        self.contrast_var = contrast_var
        self.brightness_var = brightness_var
        self.quality_var = quality_var
        self.scale_var = scale_var
        self.border_var = border_var
        self.replace_var = replace_var
        self.on_border_change = on_border_change
        
        self.contrast_label = None
        self.brightness_label = None
        self.quality_label = None
        self.zoom_label = None
        
        self.setup_controls()
    
    def setup_controls(self):
        """Configura controles"""
        
        # ARQUIVO
        file_label = ctk.CTkLabel(self, text="▸ ARQUIVO", font=("Arial", 14, "bold"))
        file_label.pack(fill="x", pady=(0,5))
        
        ctk.CTkButton(
            self, text="⊕ Abrir Imagens", 
            command=self.callbacks['open_images'],
            height=32
        ).pack(fill="x", pady=(0,10))
        
        # NAVEGAÇÃO
        nav_frame = ctk.CTkFrame(self)
        nav_frame.pack(fill="x", pady=(0,10))
        
        ctk.CTkButton(
            nav_frame, text="◄ Anterior", 
            command=self.callbacks['prev_image'],
            height=28
        ).grid(row=0, column=0, sticky="ew", padx=(0,2))
        
        ctk.CTkButton(
            nav_frame, text="Próxima ►", 
            command=self.callbacks['next_image'],
            height=28
        ).grid(row=0, column=1, sticky="ew", padx=(2,0))
        
        nav_frame.columnconfigure(0, weight=1)
        nav_frame.columnconfigure(1, weight=1)
        
        # OPERAÇÕES
        ops_label = ctk.CTkLabel(self, text="▸ OPERAÇÕES", font=("Arial", 14, "bold"))
        ops_label.pack(fill="x", pady=(10,5))
        
        ctk.CTkButton(
            self, text="✂ Cortar Seleção", 
            command=self.callbacks['crop_selection'],
            height=28
        ).pack(fill="x", pady=(0,5))
        
        ctk.CTkButton(
            self, text="● Auto Crop Face", 
            command=self.callbacks['auto_crop_face'],
            height=28
        ).pack(fill="x", pady=(0,5))
        
        ctk.CTkButton(
            self, text="↺ Reverter", 
            command=self.callbacks['revert_current'],
            height=28
        ).pack(fill="x", pady=(0,5))
        
        ctk.CTkButton(
            self, text="✕ Remover Imagem", 
            command=self.callbacks['remove_current'],
            fg_color="#d32f2f",
            hover_color="#b71c1c",
            height=28
        ).pack(fill="x", pady=(0,10))
        
        # AJUSTES
        adj_label = ctk.CTkLabel(self, text="▸ AJUSTES", font=("Arial", 14, "bold"))
        adj_label.pack(fill="x", pady=(10,5))
        
        # Contraste
        contrast_header = ctk.CTkFrame(self, fg_color="transparent")
        contrast_header.pack(fill="x", pady=(0,2))
        
        ctk.CTkLabel(contrast_header, text="◐ Contraste:", anchor="w").pack(side="left")
        self.contrast_label = ctk.CTkLabel(
            contrast_header, text="1.0", width=40, anchor="e", font=("Arial", 10, "bold")
        )
        self.contrast_label.pack(side="right")
        
        ctk.CTkSlider(
            self, from_=0.5, to=2.0, 
            variable=self.contrast_var,
            number_of_steps=30,
            command=self.update_contrast_label
        ).pack(fill="x", pady=(0,5))
        
        # Brilho
        brightness_header = ctk.CTkFrame(self, fg_color="transparent")
        brightness_header.pack(fill="x", pady=(0,2))
        
        ctk.CTkLabel(brightness_header, text="☀ Brilho:", anchor="w").pack(side="left")
        self.brightness_label = ctk.CTkLabel(
            brightness_header, text="1.0", width=40, anchor="e", font=("Arial", 10, "bold")
        )
        self.brightness_label.pack(side="right")
        
        ctk.CTkSlider(
            self, from_=0.5, to=2.0, 
            variable=self.brightness_var,
            number_of_steps=30,
            command=self.update_brightness_label
        ).pack(fill="x", pady=(0,5))
        
        # Qualidade
        quality_header = ctk.CTkFrame(self, fg_color="transparent")
        quality_header.pack(fill="x", pady=(0,2))
        
        ctk.CTkLabel(quality_header, text="◆ Qualidade:", anchor="w").pack(side="left")
        self.quality_label = ctk.CTkLabel(
            quality_header, text="100", width=40, anchor="e", font=("Arial", 10, "bold")
        )
        self.quality_label.pack(side="right")
        
        ctk.CTkSlider(
            self, from_=60, to=100, 
            variable=self.quality_var,
            number_of_steps=40,
            command=self.update_quality_label
        ).pack(fill="x", pady=(0,5))
        
        # Zoom
        zoom_header = ctk.CTkFrame(self, fg_color="transparent")
        zoom_header.pack(fill="x", pady=(0,2))
        
        ctk.CTkLabel(zoom_header, text="⊕ Zoom:", anchor="w").pack(side="left")
        self.zoom_label = ctk.CTkLabel(
            zoom_header, text="100%", width=40, anchor="e", font=("Arial", 10, "bold")
        )
        self.zoom_label.pack(side="right")
        
        ctk.CTkSlider(
            self, from_=0.1, to=2.0, 
            variable=self.scale_var,
            number_of_steps=38,
            command=self.update_zoom_label
        ).pack(fill="x", pady=(0,5))
        
        # BORDA
        border_frame = ctk.CTkFrame(self, fg_color="transparent")
        border_frame.pack(fill="x", pady=(5,10))
        
        self.border_checkbox = ctk.CTkCheckBox(
            border_frame,
            text="▭ Adicionar Borda",
            variable=self.border_var,
            font=("Arial", 11),
            command=self._on_border_toggle
        )
        self.border_checkbox.pack(anchor="w")
        
        # Botão Aplicar
        ctk.CTkButton(
            self, text="✓ Aplicar Alterações", 
            command=self.callbacks['apply_changes'],
            fg_color="#2e7d32",
            hover_color="#1b5e20",
            height=35,
            font=("Arial", 12, "bold")
        ).pack(fill="x", pady=(0,10))
        
        # SALVAMENTO
        ctk.CTkCheckBox(
            self, text="⟲ Substituir Original", 
            variable=self.replace_var,
            font=("Arial", 11)
        ).pack(fill="x", pady=(10,5))
        
        ctk.CTkButton(
            self, text="▼ Salvar Foto", 
            command=self.callbacks['save_image'],
            height=35
        ).pack(fill="x", pady=(0,5))
        
        ctk.CTkButton(
            self, text="▼ Salvar Todas", 
            command=self.callbacks['save_all'],
            height=35
        ).pack(fill="x", pady=(0,15))
        
        # ASSINATURA
        signature_frame = ctk.CTkFrame(self, fg_color="transparent")
        signature_frame.pack(fill="x", pady=(10,5))
        
        ctk.CTkLabel(
            signature_frame,
            text="@Samuel-Fernandes",
            font=("Arial", 10, "italic"),
            text_color="gray50"
        ).pack(anchor="center")
        
        self.update_contrast_label(self.contrast_var.get())
        self.update_brightness_label(self.brightness_var.get())
        self.update_quality_label(self.quality_var.get())
        self.update_zoom_label(self.scale_var.get())
    
    def _on_border_toggle(self):
        """Callback quando checkbox borda é alterado"""
        if self.on_border_change:
            self.on_border_change()
    
    def update_contrast_label(self, value):
        if self.contrast_label:
            self.contrast_label.configure(text=f"{float(value):.1f}")
    
    def update_brightness_label(self, value):
        if self.brightness_label:
            self.brightness_label.configure(text=f"{float(value):.1f}")
    
    def update_quality_label(self, value):
        if self.quality_label:
            self.quality_label.configure(text=f"{int(value)}")
    
    def update_zoom_label(self, value):
        if self.zoom_label:
            self.zoom_label.configure(text=f"{int(float(value) * 100)}%")


class ImageCanvas(tk.Canvas):
    """Canvas para exibição e seleção"""
    
    def __init__(self, parent, on_selection):
        super().__init__(parent, bg="#1a1a1a", cursor="cross", highlightthickness=0)
        
        self.on_selection = on_selection
        self.start_x = self.start_y = 0
        self.rect = None
        self.dim_text = None
        
        self.bind("<ButtonPress-1>", self.on_press)
        self.bind("<B1-Motion>", self.on_drag)
        self.bind("<ButtonRelease-1>", self.on_release)
    
    def on_press(self, event):
        self.start_x, self.start_y = event.x, event.y
        if self.rect:
            self.delete(self.rect)
        if self.dim_text:
            self.delete(self.dim_text)
        self.rect = None
        self.dim_text = None
    
    def on_drag(self, event):
        if self.rect:
            self.delete(self.rect)
        if self.dim_text:
            self.delete(self.dim_text)
        
        x0, y0 = self.start_x, self.start_y
        x1, y1 = event.x, event.y
        
        w, h = abs(x1 - x0), abs(y1 - y0)
        if w < 5 or h < 5:
            return
        
        target = 3/4
        
        if w / h > target:
            new_h = int(w / target)
            cy = (y0 + y1) // 2
            y0, y1 = cy - new_h // 2, cy + new_h // 2
        else:
            new_w = int(h * target)
            cx = (x0 + x1) // 2
            x0, x1 = cx - new_w // 2, cx + new_w // 2
        
        self.rect = self.create_rectangle(
            x0, y0, x1, y1,
            outline="lime", width=2, dash=(5, 5)
        )
        
        self.dim_text = self.create_text(
            (x0 + x1) // 2, y0 - 15,
            text=f"{abs(x1-x0)}x{abs(y1-y0)}",
            fill="lime", font=("Arial", 11, "bold")
        )
    
    def on_release(self, event):
        if self.rect:
            x0, y0, x1, y1 = self.coords(self.rect)
            self.on_selection((int(x0), int(y0), int(x1), int(y1)))