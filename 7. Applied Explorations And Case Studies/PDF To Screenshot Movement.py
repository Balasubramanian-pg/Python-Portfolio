import os
from pdf2image import convert_from_path
from pathlib import Path

def pdf_to_images(pdf_path, output_folder="pdf_screenshots"):
    """
    Convert each page of a PDF to an image and save to a folder.
    
    Args:
        pdf_path: Path to the PDF file
        output_folder: Folder where images will be saved (default: "pdf_screenshots")
    """
    # Create output folder if it doesn't exist
    Path(output_folder).mkdir(parents=True, exist_ok=True)
    
    print(f"Converting PDF: {pdf_path}")
    print(f"Output folder: {output_folder}")
    
    try:
        # Convert PDF to list of images
        images = convert_from_path(pdf_path, dpi=300)
        
        # Save each page as an image
        for i, image in enumerate(images, start=1):
            output_path = os.path.join(output_folder, f"slide_{i:03d}.png")
            image.save(output_path, "PNG")
            print(f"Saved: {output_path}")
        
        print(f"\nSuccess! Converted {len(images)} pages to images.")
        print(f"Images saved in: {os.path.abspath(output_folder)}")
        
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure you have poppler installed:")
        print("- Windows: Download from https://github.com/oschwartz10612/poppler-windows/releases/")
        print("- Mac: brew install poppler")
        print("- Linux: sudo apt-get install poppler-utils")

# Usage
if __name__ == "__main__":
    pdf_path = r"C:\Users\ASUS\Downloads\Channel Benchmark Performance.pdf"
    output_folder = "pdf_screenshots"
    
    pdf_to_images(pdf_path, output_folder)