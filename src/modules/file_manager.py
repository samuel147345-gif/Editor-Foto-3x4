"""
Módulo de gerenciamento de arquivos
Contém funcionalidades de salvamento e manipulação de arquivos
"""
import os
from tkinter import filedialog, messagebox

class FileManager:
    """
    Gerenciador de arquivos para o editor de fotos
    """
    
    @staticmethod
    def get_extension_map():
        """Retorna mapeamento de formatos para extensões"""
        return {
            "JPEG": ".jpeg",
            "PNG": ".png", 
            "BMP": ".bmp",
            "TIFF": ".tiff"
        }
    
    @staticmethod
    def get_file_types():
        """Retorna tipos de arquivo suportados para diálogos"""
        return [
            ("JPEG", "*.jpg;*.jpeg"),
            ("PNG", "*.png"),
            ("BMP", "*.bmp"),
            ("TIFF", "*.tiff")
        ]
    
    @staticmethod
    def open_images():
        """
        Abre diálogo para seleção de múltiplas imagens
        Retorna lista de caminhos selecionados
        """
        return filedialog.askopenfilenames(
            filetypes=[("Imagens", "*.jpg *.jpeg *.png *.bmp *.tiff")]
        )
    
    @staticmethod
    def save_single_image(image, format_type, quality=90, overwrite=False, original_path=None):
        """
        Salva uma única imagem
        """
        ext_map = FileManager.get_extension_map()
        
        if overwrite and original_path:
            base_name, _ = os.path.splitext(original_path)
            save_path = base_name + ext_map[format_type]
        else:
            save_path = filedialog.asksaveasfilename(
                defaultextension=ext_map[format_type],
                filetypes=FileManager.get_file_types()
            )
            if not save_path:
                return None
        
        save_kwargs = {"quality": quality} if format_type == "JPEG" else {}
        image.save(save_path, format_type, **save_kwargs)
        
        return save_path
    
    @staticmethod
    def save_batch_images(images, image_paths, format_type, quality=90, overwrite=False):
        """
        Salva múltiplas imagens em lote
        """
        ext_map = FileManager.get_extension_map()
        
        if overwrite:
            targets = []
            for orig in image_paths:
                base_name, _ = os.path.splitext(orig)
                targets.append(base_name + ext_map[format_type])
        else:
            folder = filedialog.askdirectory(title="Selecione pasta para salvar todas")
            if not folder:
                return 0
            targets = [
                os.path.join(folder, os.path.splitext(os.path.basename(orig))[0] + ext_map[format_type])
                for orig in image_paths
            ]
        
        saved = 0
        save_kwargs = {"quality": quality} if format_type == "JPEG" else {}
        
        for img, target in zip(images, targets):
            try:
                img.save(target, format_type, **save_kwargs)
                saved += 1
            except Exception as e:
                messagebox.showerror("Erro ao salvar", f"Erro ao salvar {target}: {str(e)}")
        
        return saved
