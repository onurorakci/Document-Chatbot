# Document Chatbot 

Tamamen çevrimdışı çalışan, veri güvenliği odaklı, belge tabanlı soru-cevap (RAG) sistemi.  
PDF'ler, görseller ve OCR ile işlenen belgeler üzerinden yerel bir LLM aracılığıyla sorgu yapılmasını sağlar.  
Hiçbir veri dışarı çıkmaz; tüm işlem yerel donanımda gerçekleşir.

---

## 🧱 Mimari

```
Frontend (React / Vite)
        │
        ▼
Backend (FastAPI + Uvicorn)
        │
   ┌────┴────────────────────┐
   │                         │
RAG Modülü               Model Yöneticisi
(LangChain +             (INT4 Quantized
 Semantic Chunker)        Qwen3 4B)
   │
SQLite Veritabanı
   │
Veri İşleme Katmanı
(PyMuPDF + EasyOCR + Pillow)
```

- **Model:** Qwen3 4B (INT4 quantization ile 6GB VRAM'de kararlı çalışır)
- **Embedding:** `paraphrase-multilingual-MiniLM-L12-v2` (Türkçe + İngilizce destek)
- **Chunking:** Semantic Chunker (anlamsal bütünlük korunur)

---

## ⚙️ Sistem Gereksinimleri

| Bileşen | Sürüm |
|--------|-------|
| Python | 3.10.17 |
| CUDA | 12.5 |
| cuDNN | 9.3 |
| İşletim Sistemi | Ubuntu 24.04 |
| GPU (min.) | 6GB VRAM (RTX 2060 veya üzeri) |
| RAM | 16 GB RAM |


---

## 🚀 Kurulum

### 1. Repoyu klonlayın

```bash
git clone https://github.com/onurorakci/Document-Chatbot
cd proje-adi
```

### 2. Sanal ortam oluşturun ve aktif edin

```bash
python3.10 -m venv venv
source venv/bin/activate
```

### 3. Bağımlılıkları yükleyin

```bash
pip install -r requirements.txt
```

### 4. Backend'i başlatın

```bash
cd backend
python3 main.py
```

### 5. Frontend'i başlatın (ayrı terminal)

```bash
cd frontend
npm install   # package.json'daki tüm bağımlılıkları yükler
npm run dev
```

> Node.js (v18+) ve npm'in kurulu olması gerekir.  
> Kurulum için: https://nodejs.org

### 6. Tarayıcıda açın

```
http://localhost:5173
```

---

## 📖 Kullanım

1. Arayüzden bir **PDF, görsel veya fotoğraf** yükleyin.
2. Belge işlendikten sonra sohbet kutusuna sorunuzu yazın.
3. Sistem yalnızca yüklenen belgedeki bilgilere dayanarak yanıt üretir.
4. Belgede bulunmayan bilgiler için: `"This information is not in the document."` yanıtı döner.

> ⚠️ Sistem kasıtlı olarak önceden eğitilmiş bilgiyi **kullanmaz**. Tüm yanıtlar yalnızca yüklenen belgeden üretilir.

---

## 🗂️ Proje Yapısı

```
📁 proje-adi/
├── 📁 backend/
│   ├── main.py              # FastAPI uygulama giriş noktası
│   ├── model_loader.py      # INT4 quantized model yükleme
│   ├── rag.py               # LangChain RAG + Semantic Chunker
│   ├── file_reader.py        # PyMuPDF + EasyOCR hibrit okuyucu
│   └── db_manager.py          # SQLite oturum ve belge yönetimi
│   └── test_files.zip          # test dosyaları (ipynb, dökümanlar ve sonuçlar)
├── 📁 frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   └── components/
│   └── vite.config.js
├── requirements.txt
└── README.md
```

---

## 📊 Model Performansı (Özet)

| Model | Genel Başarı | Türkçe | OCR/Görsel | Halüsinasyon |
|-------|-------------|--------|------------|--------------|
| **Qwen3 4B** ✅ | %81.1 | %60.0 | %90.0 | %0 |
| Qwen2.5 3B | %69.8 | %66.0 | %90.0 | Orta |
| LLaMA 3.2 3B | %50.4 | %40.0 | %50.0 | %0 |
| IBM Granite 2B | %48.0 | %16.0 | %70.0 | Yüksek |
| Phi-4 mini | %27.6 | %28.0 | %70.0 | Orta |

> Ana model olarak **Qwen3 4B** seçilmiştir.
