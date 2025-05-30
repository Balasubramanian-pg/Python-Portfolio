import os
from PIL import Image
import glob

def images_to_pdf(folder_path, output_pdf_name="combined_images.pdf"):
    """
    Convert all images in a folder to a single PDF file.
    
    Args:
        folder_path (str): Path to the folder containing images
        output_pdf_name (str): Name of the output PDF file
    """
    
    # Supported image formats
    image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.tiff', '*.tif', '*.gif']
    
    # Get all image files from the folder
    image_files = []
    for extension in image_extensions:
        image_files.extend(glob.glob(os.path.join(folder_path, extension)))
        image_files.extend(glob.glob(os.path.join(folder_path, extension.upper())))
    
    if not image_files:
        print(f"No image files found in {folder_path}")
        return
    
    # Sort files to maintain order
    image_files.sort()
    
    print(f"Found {len(image_files)} image files")
    
    # Convert images to PDF
    images = []
    
    for img_path in image_files:
        try:
            print(f"Processing: {os.path.basename(img_path)}")
            
            # Open and convert image
            img = Image.open(img_path)
            
            # Convert to RGB if necessary (for PNG with transparency, etc.)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            images.append(img)
            
        except Exception as e:
            print(f"Error processing {img_path}: {e}")
            continue
    
    if not images:
        print("No valid images to convert")
        return
    
    # Save as PDF
    try:
        output_path = os.path.join(folder_path, output_pdf_name)
        
        # Save the first image and append the rest
        images[0].save(
            output_path, 
            "PDF", 
            resolution=100.0, 
            save_all=True, 
            append_images=images[1:]
        )
        
        print(f"\nPDF created successfully: {output_path}")
        print(f"Total pages: {len(images)}")
        
    except Exception as e:
        print(f"Error creating PDF: {e}")

# Example usage
if __name__ == "__main__":
    # Your folder path
    folder_path = r"F:\Flipcarbon\2025\5.May\26-05-2025\ASPL"
    
    # PDF name
    pdf_name = "combined_images.pdf"
    
    # Ensure PDF extension
    if not pdf_name.endswith('.pdf'):
        pdf_name += '.pdf'
    
    # Check if folder exists
    if os.path.exists(folder_path):
        images_to_pdf(folder_path, pdf_name)
    else:
        print(f"Folder not found: {folder_path}")