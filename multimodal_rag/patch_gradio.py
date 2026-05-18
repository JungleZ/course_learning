\"\"\"
??????python patch_gradio.py
???? Gradio 3.34.0 ? PredictBody ?? event_id ??????
\"\"\"
import os, sys

# ?? gradio ? data_classes.py
try:
    import gradio.data_classes as dc
    filepath = dc.__file__
except:
    print(\"[FAIL] gradio ????????\")
    sys.exit(1)

# ??????
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# ?????????
if 'event_id: Optional[str] = None' in content:
    print(\"[OK] ????????????\")
    sys.exit(0)

# ?? PredictBody ??
old = '''class PredictBody(BaseModel):
    session_hash: Optional[str]
    event_id: Optional[str]
    data: List[Any]
    event_data: Optional[Any]
    fn_index: Optional[int]'''

new = '''class PredictBody(BaseModel):
    session_hash: Optional[str] = None
    event_id: Optional[str] = None
    data: List[Any]
    event_data: Optional[Any] = None
    fn_index: Optional[int] = None'''

if old not in content:
    print(\"[FAIL] ???? PredictBody ???Gradio ???????\")
    sys.exit(1)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content.replace(old, new))

print(\"[OK] Gradio PredictBody ?????event_id/event_data ????\")
