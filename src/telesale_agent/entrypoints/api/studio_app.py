"""Entrypoint for LangGraph Studio."""

import sys
import os

# Tự động thêm thư mục src vào PYTHONPATH để dễ dàng import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from telesale_agent.bootstrap import build_default_harness

# Khởi tạo harness
harness = build_default_harness()

# Expose biến 'graph' cho LangGraph Studio
graph = harness.graph
