from retriever import VisualRetriever
from image_encoder import ImageEncoder
from generator import create_generator

encoder = ImageEncoder(mode='pixel')
retriever = VisualRetriever(persist_dir='D:/code_workspaces/multimodal_rag/index', dim=128)
retriever.load()
generator = create_generator()

print('\n=== ?????? ===')
results = retriever.search_by_text('cat', encoder, k=3)
for r in results:
    print('  %s (%.4f)' % (r['filename'], r['score']))

print('\n=== ?????? ===')
results2 = retriever.search_by_image('D:/code_workspaces/multimodal_rag/images/img_01.png', encoder, k=3)
for r in results2:
    print('  %s (%.4f)' % (r['filename'], r['score']))

print('\n=== Mock???? ===')
resp = generator.generate_from_images('?????', ['D:/code_workspaces/multimodal_rag/images/img_01.png'], [0.95])
print(resp['answer'])
print('\n???????')
