import sys
sys.path.insert(0, 'D:/code_workspaces/multimodal_rag/src')
from data_processing import process_images, load_index
from image_encoder import ImageEncoder
from retriever import Retriever
from generator import Generator
import json, os

index_path = 'D:/code_workspaces/multimodal_rag/index'
img_dir = 'D:/code_workspaces/multimodal_rag/images'

# Check if index needs building
if not os.listdir(index_path):
    print('Building index...')
    process_images(img_dir, index_path)

# Load modules
encoder = ImageEncoder(mode='pixel')
retriever = Retriever(index_path, encoder)
generator = Generator(mode='mock')

# Test text search
print('\n--- Text Search Test ---')
results = retriever.search_text('cat', top_k=3)
print(f'Found {len(results)} results')
for r in results:
    print(f'  {r["filename"]}: score={r["score"]:.4f}')

print('\n--- Mock QA Test ---')
answer = generator.generate('cat image', results)
print(f'Answer: {answer}')
print('\nAll tests passed!')
