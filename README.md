# 🍽️ Food Nutrition AI Agent

AI Agent chuyên phân tích dinh dưỡng thực phẩm, tính toán calories, protein, chất béo và cung cấp tư vấn chế độ ăn.

## ✨ Tính năng

- 📊 **Phân tích dinh dưỡng**: Tính calories, protein, chất béo, carbs của món ăn
- 🔍 **Web Search**: Tìm kiếm thông tin dinh dưỡng trên internet
- 🥗 **So sánh món ăn**: So sánh giá trị dinh dưỡng giữa các món
- 💡 **Gợi ý healthy**: Đề xuất món ăn thay thế lành mạnh hơn
- 🍲 **Tính tổng bữa ăn**: Tính dinh dưỡng cho cả bữa ăn nhiều món
- 🤖 **Multi-LLM**: Hỗ trợ Deepseek, Claude, OpenAI

## 🚀 Cài đặt

### 1. Clone và cài đặt dependencies

```bash
# Di chuyển vào thư mục project
cd deepshiet

# Tạo virtual environment (khuyến nghị)
python -m venv venv

# Kích hoạt virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Cài đặt dependencies
pip install -r requirements.txt
```

### 2. Cấu hình environment

```bash
# Rename file cấu hình
# Windows:
rename env.example.txt .env
# Linux/Mac:
mv env.example.txt .env

# Chỉnh sửa file .env và thêm API keys
```

### 3. Cấu hình API Keys

Mở file `.env` và thêm:

```env
# BẮT BUỘC: API Key của LLM
MODEL_API_KEY=your_api_key_here

# Tùy chọn: Provider (deepseek/claude/openai)
LLM_PROVIDER=deepseek

# Tùy chọn: API Key cho web search
SERPER_API_KEY=your_serper_key_here
```

**Lấy API Keys:**
- Deepseek: https://platform.deepseek.com/
- Claude: https://console.anthropic.com/
- OpenAI: https://platform.openai.com/
- Serper (Web Search): https://serper.dev/ (2500 free/tháng)

## 🎮 Sử dụng

### Chạy Agent

```bash
python main.py
```

### Ví dụ câu hỏi

```
Bạn: Phân tích dinh dưỡng phở bò

🤖 AI Agent:
## 🍜 Phở Bò

### 📊 Thông tin dinh dưỡng (khẩu phần 500g)
| Chỉ số | Giá trị |
|--------|---------|
| 🔥 Calories | 450 kcal |
| 💪 Protein | 25g |
| 🧈 Fat | 12g |
| 🍚 Carbs | 55g |
...
```

### Các lệnh đặc biệt

- `quit` / `exit` / `q`: Thoát chương trình
- `clear`: Xóa lịch sử hội thoại

## 📁 Cấu trúc Project

```
deepshiet/
├── agent_core/           # Core AI Agent logic
│   ├── __init__.py
│   ├── agent.py          # Main agent class
│   ├── exceptions.py     # Custom exceptions
│   └── tools.py          # Web search & nutrition tools
├── knowledge_base/       # Prompts và templates
│   ├── prompts/
│   │   └── SYSTEM_PROMPT.md
│   └── templates/
│       └── TEMPLATE.md
├── skills/               # Agent skills
│   ├── __init__.py
│   ├── registry.py       # Skill registry
│   └── food_analysis.py  # Food analysis skills
├── config.py             # Configuration management
├── main.py               # Entry point
├── requirements.txt      # Dependencies
├── env.example.txt       # Example environment config
└── README.md
```

## 🔧 Cấu hình nâng cao

### Thay đổi LLM Provider

```env
# Sử dụng Claude
LLM_PROVIDER=claude
MODEL_API_KEY=sk-ant-...

# Sử dụng OpenAI
LLM_PROVIDER=openai
MODEL_API_KEY=sk-...

# Sử dụng Deepseek (mặc định)
LLM_PROVIDER=deepseek
MODEL_API_KEY=sk-...
```

### Tùy chỉnh Model

```env
# Deepseek
LLM_MODEL=deepseek-chat

# Claude
LLM_MODEL=claude-3-5-sonnet-20241022

# OpenAI
LLM_MODEL=gpt-4o
```

### Tùy chỉnh Generation

```env
# Số token tối đa
LLM_MAX_TOKENS=4096

# Temperature (0.0 = focused, 1.0 = creative)
LLM_TEMPERATURE=0.7
```

## 🛠️ Mở rộng

### Thêm skill mới

```python
# skills/my_skill.py
from .registry import registry

@registry.register(
    name="my_skill",
    description="Mô tả skill",
    examples=["Ví dụ 1", "Ví dụ 2"],
    tags=["tag1", "tag2"]
)
async def my_skill(param: str) -> dict:
    # Implementation
    pass
```

### Thêm tool mới

Chỉnh sửa `agent_core/tools.py` và thêm vào `AVAILABLE_TOOLS`.

## 📝 License

MIT License

## 🤝 Đóng góp

Mọi đóng góp đều được hoan nghênh! Hãy tạo Pull Request hoặc Issue.
