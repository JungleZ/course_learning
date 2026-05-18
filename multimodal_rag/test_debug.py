import sys
sys.path.insert(0, 'D:/code_workspaces/multimodal_rag/src')
from retriever import VisualRetriever
from image_encoder import ImageEncoder
import numpy as np
from PIL import Image

encoder = ImageEncoder(mode='pixel')
retriever = VisualRetriever(persist_dir='D:/code_workspaces/multimodal_rag/index', dim=128)
retriever.load()

results = retriever.search_by_text('red', encoder, k=5)
print('Found %d results' % len(results))
for r in results:
    print('  %s: score=%.4f, path=%s' % (r['filename'], r['score'], r['filepath']))
    try:
        img = Image.open(r['filepath'])
        arr = np.array(img)
        print('    OK: shape=%s' % str(arr.shape))
    except Exception as e:
        print('    FAIL: %s' % str(e))
