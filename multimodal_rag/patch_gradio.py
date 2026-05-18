"""
部署前运行：python patch_gradio.py
自动修复 Gradio 3.34.0 PredictBody event_id 缺失默认值的问题
"""
import os
import sys

try:
    import gradio.data_classes as dc
    filepath = dc.__file__
except ImportError:
    print("[FAIL] gradio 未安装")
    sys.exit(1)

with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

if "event_id: Optional[str] = None" in content:
    print("[OK] 已打过补丁")
    sys.exit(0)

old = """class PredictBody(BaseModel):
    session_hash: Optional[str]
    event_id: Optional[str]
    data: List[Any]
    event_data: Optional[Any]
    fn_index: Optional[int]"""

new = """class PredictBody(BaseModel):
    session_hash: Optional[str] = None
    event_id: Optional[str] = None
    data: List[Any]
    event_data: Optional[Any] = None
    fn_index: Optional[int] = None"""

if old not in content:
    print("[FAIL] 无法匹配 PredictBody，Gradio 版本可能不兼容")
    sys.exit(1)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content.replace(old, new))

print("[OK] Gradio PredictBody 已打补丁")
