# LangFlow Workflows - FanPulse

## 📁 ساختار فایل‌ها

### 1. Flow File (JSON)

#### `FanPulse Multi-Agent.json` ⭐ **CURRENT FLOW**
- **معماری**: 3-Agent با Tool Calling
- **Components**: Orchestrator + VAR-Lens + Tactical Pulse
- **وضعیت**: ✅ آماده برای استفاده
- **استفاده**: Import به LangFlow UI

---

### 2. System Prompts (3 files)

- **`ORCHESTRATOR_SYSTEM_PROMPT.md`** - Orchestrator Agent prompt
- **`TACTICAL_PULSE_SYSTEM_PROMPT.md`** - Tactical Pulse Agent prompt
- **`VAR_LENS_SYSTEM_PROMPT.md`** - VAR-Lens Agent prompt

---

### 3. Data Schema & Guides (3 files)

- **`DATA_SCHEMA_GUIDE_V2.md`** - Complete data schema (World Cup 2022 + 2026)
- **`MATCH_ID_PREFIX_GUIDE.md`** - Match ID prefix system (17 tournaments)
- **`MULTI_TOURNAMENT_GUIDE.md`** - Multi-tournament support guide

---

### 4. Architecture & Analysis (1 file)

- **`PROMPT_ARCHITECTURE_ANALYSIS.md`** - Prompt architecture analysis & recommendations

---

### 5. Setup Guide (1 file)

- **`COMPLETE_WORKFLOW_SETUP.md`** - راهنمای جامع ساخت Flow در LangFlow (717 خط)
  - Import کامپوننت‌ها
  - ساخت Flow
  - اتصالات صحیح
  - Agent as Tool Setup
  - تست و عیب‌یابی
  - آماده‌سازی Demo

---

## 🚀 شروع سریع

### مرحله 1: Import کامپوننت‌ها
```bash
cd d:/MyPythonProjects/FanPulse
cp langflow_components/*.py ~/.langflow/components/
```

### مرحله 2: راه‌اندازی LangFlow
```bash
langflow run
```

### مرحله 3: Import Flow
1. باز کردن LangFlow UI: `http://localhost:7860`
2. کلیک روی "New Flow"
3. کلیک روی "Import"
4. انتخاب `FanPulse Multi-Agent.json`

### مرحله 4: راهنمای کامل
برای راهنمای قدم به قدم، مراجعه کنید به:
📄 **[`COMPLETE_WORKFLOW_SETUP.md`](./COMPLETE_WORKFLOW_SETUP.md)**

---

## 📊 معماری

```
┌──────────────┐
│  Chat Input  │
└──────┬───────┘
       │
       ▼
┌─────────────────────────────────────────┐
│        FanPulse Orchestrator            │
│         (با Tool Calling)               │
└─────────────────────────────────────────┘
       ▲                    ▲
       │                    │
┌──────┴────────┐    ┌──────┴──────────┐
│  VAR-Lens     │    │ Tactical Pulse  │
│  Agent        │    │ Agent           │
└───────────────┘    └─────────────────┘
       ▲                    ▲
       │                    │
┌──────┴────────┐    ┌──────┴──────────┐
│ FIFA Docs     │    │ 5 Tactical      │
│ Tool          │    │ Tools           │
└───────────────┘    └─────────────────┘
```

---

## 🎯 ویژگی‌های کلیدی

- ✅ **3-Agent Architecture** با Tool Calling واقعی
- ✅ **LLM-based Routing** با IBM Granite 3.1 8B
- ✅ **Parallel Execution** برای سوالات پیچیده
- ✅ **FIFA Rules RAG** با 658 vectors
- ✅ **World Cup 2022 + 2026 Data** با 45K+ matches
- ✅ **Native Streaming** در LangFlow

---

## 📝 نکات مهم

### برای Demo Video:
1. **نشان دادن 3-Agent Architecture**: Orchestrator + VAR-Lens + Tactical Pulse
2. **Tool Calling**: نمایش در logs
3. **Parallel Execution**: نمایش همزمان بودن اجرای Agents
4. **Synthesis Quality**: کیفیت ترکیب پاسخ‌ها

### سوالات نمونه:
```
VAR-Lens:
- "What is the offside rule?"
- "Explain VAR protocol"

Tactical Pulse:
- "Analyze Argentina's performance in World Cup 2022"
- "Compare Brazil and France"

Multiple Intents:
- "Explain offside rule and predict Brazil vs Argentina"
```

---

## 🔗 لینک‌های مفید

- **مستندات LangFlow**: https://docs.langflow.org/agents
- **GitHub Repository**: https://github.com/babaksh/FanPulse
- **IBM Challenge**: https://ibmskillsbuildchallenge-hub.bemyapp.com

---

## 📅 Timeline

- **Deadline**: June 30, 2026, 11:59 PM ET
- **Days Remaining**: 15 days
- **Current Phase**: LangFlow Setup & Testing

---

**Built for IBM Skills Build AI Builders Challenge 2026**
