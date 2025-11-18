using System;
using System.IO;
using SkiaSharp;
using Newtonsoft.Json;

namespace FastImageOps
{
    /// <summary>
    /// Processador de imagem de alta performance em C# usando SkiaSharp
    /// Otimizado para operações intensivas que se beneficiam da velocidade do C#
    /// </summary>
    public class ImageProcessor
    {
        /// <summary>
        /// Redimensiona múltiplas imagens em lote com alta performance
        /// </summary>
        public static string BatchResize(string inputJson)
        {
            try
            {
                var request = JsonConvert.DeserializeObject<BatchResizeRequest>(inputJson);
                if (request?.Images == null) return JsonConvert.SerializeObject(new { Error = "Invalid request" });
                
                var results = new List<BatchResizeResult>();

                foreach (var item in request.Images)
                {
                    try
                    {
                        using var inputStream = File.OpenRead(item.Path);
                        using var inputBitmap = SKBitmap.Decode(inputStream);
                        
                        if (inputBitmap == null)
                        {
                            results.Add(new BatchResizeResult 
                            { 
                                OriginalPath = item.Path,
                                Success = false,
                                ErrorMessage = "Failed to decode image"
                            });
                            continue;
                        }
                        
                        // Calcula novas dimensões mantendo proporção
                        int newWidth = (int)(inputBitmap.Width * item.ScaleFactor);
                        int newHeight = (int)(inputBitmap.Height * item.ScaleFactor);
                        
                        // Redimensiona com alta qualidade
                        using var resizedBitmap = inputBitmap.Resize(new SKImageInfo(newWidth, newHeight), SKFilterQuality.High);
                        
                        if (resizedBitmap == null)
                        {
                            results.Add(new BatchResizeResult 
                            { 
                                OriginalPath = item.Path,
                                Success = false,
                                ErrorMessage = "Failed to resize image"
                            });
                            continue;
                        }
                        
                        // Salva resultado
                        string outputPath = Path.Combine(Path.GetDirectoryName(item.Path) ?? "", 
                            $"{Path.GetFileNameWithoutExtension(item.Path)}_resized{Path.GetExtension(item.Path)}");
                        
                        using var image = SKImage.FromBitmap(resizedBitmap);
                        using var data = image.Encode(GetSkiaFormat(Path.GetExtension(item.Path)), 90);
                        using var outputStream = File.OpenWrite(outputPath);
                        data.SaveTo(outputStream);
                        
                        results.Add(new BatchResizeResult 
                        { 
                            OriginalPath = item.Path,
                            OutputPath = outputPath,
                            Success = true,
                            NewWidth = newWidth,
                            NewHeight = newHeight
                        });
                    }
                    catch (Exception ex)
                    {
                        results.Add(new BatchResizeResult 
                        { 
                            OriginalPath = item.Path,
                            Success = false,
                            ErrorMessage = ex.Message
                        });
                    }
                }

                return JsonConvert.SerializeObject(new { Results = results });
            }
            catch (Exception ex)
            {
                return JsonConvert.SerializeObject(new { Error = ex.Message });
            }
        }

        /// <summary>
        /// Aplica filtros de imagem de alta performance
        /// </summary>
        public static string ApplyImageFilters(string inputJson)
        {
            try
            {
                var request = JsonConvert.DeserializeObject<ImageFilterRequest>(inputJson);
                if (request?.ImagePath == null) return JsonConvert.SerializeObject(new { Error = "Invalid request" });
                
                using var inputStream = File.OpenRead(request.ImagePath);
                using var inputBitmap = SKBitmap.Decode(inputStream);
                
                if (inputBitmap == null)
                {
                    return JsonConvert.SerializeObject(new { Success = false, Error = "Failed to decode image" });
                }
                
                // Cria bitmap de saída
                using var outputBitmap = new SKBitmap(inputBitmap.Width, inputBitmap.Height);
                
                // Aplica filtros pixel por pixel para máxima performance
                unsafe
                {
                    var inputPixels = (uint*)inputBitmap.GetPixels().ToPointer();
                    var outputPixels = (uint*)outputBitmap.GetPixels().ToPointer();
                    
                    int pixelCount = inputBitmap.Width * inputBitmap.Height;
                    
                    for (int i = 0; i < pixelCount; i++)
                    {
                        uint pixel = inputPixels[i];
                        
                        // Extrai componentes ARGB
                        byte a = (byte)((pixel >> 24) & 0xFF);
                        byte r = (byte)((pixel >> 16) & 0xFF);
                        byte g = (byte)((pixel >> 8) & 0xFF);
                        byte b = (byte)(pixel & 0xFF);
                        
                        // Aplica ajustes de brilho e contraste
                        r = ClampByte((int)(r * request.Contrast + request.Brightness));
                        g = ClampByte((int)(g * request.Contrast + request.Brightness));
                        b = ClampByte((int)(b * request.Contrast + request.Brightness));
                        
                        // Reconstrói pixel
                        outputPixels[i] = (uint)((a << 24) | (r << 16) | (g << 8) | b);
                    }
                }
                
                // Salva resultado
                string outputPath = Path.Combine(Path.GetDirectoryName(request.ImagePath) ?? "", 
                    $"{Path.GetFileNameWithoutExtension(request.ImagePath)}_filtered{Path.GetExtension(request.ImagePath)}");
                
                using var image = SKImage.FromBitmap(outputBitmap);
                using var data = image.Encode(GetSkiaFormat(Path.GetExtension(request.ImagePath)), 90);
                using var outputStream = File.OpenWrite(outputPath);
                data.SaveTo(outputStream);
                
                return JsonConvert.SerializeObject(new { 
                    Success = true, 
                    OutputPath = outputPath
                });
            }
            catch (Exception ex)
            {
                return JsonConvert.SerializeObject(new { Success = false, Error = ex.Message });
            }
        }

        /// <summary>
        /// Operação de crop otimizada para múltiplas imagens
        /// </summary>
        public static string BatchCrop(string inputJson)
        {
            try
            {
                var request = JsonConvert.DeserializeObject<BatchCropRequest>(inputJson);
                if (request?.Images == null) return JsonConvert.SerializeObject(new { Error = "Invalid request" });
                
                var results = new List<BatchCropResult>();

                foreach (var item in request.Images)
                {
                    try
                    {
                        using var inputStream = File.OpenRead(item.Path);
                        using var inputBitmap = SKBitmap.Decode(inputStream);
                        
                        if (inputBitmap == null)
                        {
                            results.Add(new BatchCropResult 
                            { 
                                OriginalPath = item.Path,
                                Success = false,
                                ErrorMessage = "Failed to decode image"
                            });
                            continue;
                        }
                        
                        // Valida coordenadas de crop
                        var cropRect = SKRectI.Create(
                            Math.Max(0, item.X),
                            Math.Max(0, item.Y),
                            Math.Min(item.Width, inputBitmap.Width - Math.Max(0, item.X)),
                            Math.Min(item.Height, inputBitmap.Height - Math.Max(0, item.Y))
                        );
                        
                        using var croppedBitmap = new SKBitmap(cropRect.Width, cropRect.Height);
                        inputBitmap.ExtractSubset(croppedBitmap, cropRect);
                        
                        string outputPath = Path.Combine(Path.GetDirectoryName(item.Path) ?? "", 
                            $"{Path.GetFileNameWithoutExtension(item.Path)}_cropped{Path.GetExtension(item.Path)}");
                        
                        using var image = SKImage.FromBitmap(croppedBitmap);
                        using var data = image.Encode(GetSkiaFormat(Path.GetExtension(item.Path)), 90);
                        using var outputStream = File.OpenWrite(outputPath);
                        data.SaveTo(outputStream);
                        
                        results.Add(new BatchCropResult 
                        { 
                            OriginalPath = item.Path,
                            OutputPath = outputPath,
                            Success = true,
                            CroppedWidth = cropRect.Width,
                            CroppedHeight = cropRect.Height
                        });
                    }
                    catch (Exception ex)
                    {
                        results.Add(new BatchCropResult 
                        { 
                            OriginalPath = item.Path,
                            Success = false,
                            ErrorMessage = ex.Message
                        });
                    }
                }

                return JsonConvert.SerializeObject(new { Results = results });
            }
            catch (Exception ex)
            {
                return JsonConvert.SerializeObject(new { Error = ex.Message });
            }
        }

        private static SKEncodedImageFormat GetSkiaFormat(string extension)
        {
            return extension.ToLower() switch
            {
                ".jpg" or ".jpeg" => SKEncodedImageFormat.Jpeg,
                ".png" => SKEncodedImageFormat.Png,
                ".bmp" => SKEncodedImageFormat.Bmp,
                ".webp" => SKEncodedImageFormat.Webp,
                _ => SKEncodedImageFormat.Jpeg
            };
        }

        private static byte ClampByte(int value)
        {
            return (byte)Math.Max(0, Math.Min(255, value));
        }
    }

    // Classes de modelo para serialização JSON
    public class BatchResizeRequest
    {
        public List<ResizeItem> Images { get; set; } = new();
    }

    public class ResizeItem
    {
        public string Path { get; set; } = "";
        public double ScaleFactor { get; set; }
    }

    public class BatchResizeResult
    {
        public string OriginalPath { get; set; } = "";
        public string OutputPath { get; set; } = "";
        public bool Success { get; set; }
        public string ErrorMessage { get; set; } = "";
        public int NewWidth { get; set; }
        public int NewHeight { get; set; }
    }

    public class ImageFilterRequest
    {
        public string ImagePath { get; set; } = "";
        public double Contrast { get; set; } = 1.0;
        public double Brightness { get; set; } = 0.0;
    }

    public class BatchCropRequest
    {
        public List<CropItem> Images { get; set; } = new();
    }

    public class CropItem
    {
        public string Path { get; set; } = "";
        public int X { get; set; }
        public int Y { get; set; }
        public int Width { get; set; }
        public int Height { get; set; }
    }

    public class BatchCropResult
    {
        public string OriginalPath { get; set; } = "";
        public string OutputPath { get; set; } = "";
        public bool Success { get; set; }
        public string ErrorMessage { get; set; } = "";
        public int CroppedWidth { get; set; }
        public int CroppedHeight { get; set; }
    }
}
