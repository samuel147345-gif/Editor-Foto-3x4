using System;
using FastImageOps;

namespace FastImageOps
{
    /// <summary>
    /// Programa principal para execução standalone dos componentes C#
    /// Permite chamadas via linha de comando do Python
    /// </summary>
    class Program
    {
        static void Main(string[] args)
        {
            if (args.Length < 2)
            {
                Console.WriteLine("Uso: FastImageOps <operacao> <json_input>");
                Console.WriteLine("Operações disponíveis: batch-resize, apply-filters, batch-crop");
                return;
            }

            string operation = args[0].ToLower();
            string jsonInput = args[1];

            try
            {
                string result = operation switch
                {
                    "batch-resize" => ImageProcessor.BatchResize(jsonInput),
                    "apply-filters" => ImageProcessor.ApplyImageFilters(jsonInput),
                    "batch-crop" => ImageProcessor.BatchCrop(jsonInput),
                    _ => "{\"Error\": \"Operação não reconhecida\"}"
                };

                Console.WriteLine(result);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"{{\"Error\": \"{ex.Message}\"}}");
            }
        }
    }
}
