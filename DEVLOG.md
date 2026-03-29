# 4.2. TESTING.md — Test ve Doğrulama

Bu belge, geliştirilen yerel RAG (Retrieval-Augmented Generation) sisteminin doğruluğunu, sınırlarını ve farklı modellerin performanslarını ölçmek amacıyla yapılan kalitatif ve kantitatif test süreçlerini özetlemektedir.

## 1. Test Stratejisi ve Kurallar

Sistem, tamamen dışa kapalı bir savunma sanayii senaryosu baz alınarak tasarlandığı için aşağıdaki katı "Sistem İstemi" (System Prompt) kural setiyle test edilmiştir:

> **System Prompt Kuralları:**

-   > SADECE sağlanan belgeyi kullanarak cevap ver.
    
-   > Önceden eğitildiğin bilgileri (prior knowledge) KULLANMA.
    
-   > Belgede ilgili bilgiyi bulursan, cevaplamak için ZORUNLU olarak kullan.
    
-   > Bilgi belgede yoksa, sadece "This information is not in the document." yanıtını dön.
    

**Model Seçim Kriterleri:**

-   Donanım kısıtlamaları (6GB VRAM) nedeniyle HuggingFace Leaderboard üzerinden 4B parametre ve altındaki modeller seçildi.
    
-   Base Meta/Llama ve Google Gemma gibi dışarıdan istek/onay gerektiren modeller, "tamamen yerel sistem" kuralını ihlal ettiği için (iFaz 3B hariç tutularak) değerlendirmeye alınmadı.
    

## 2. Kalitatif (Manuel) Testler ve Gözlemler

İlk aşamada arayüz üzerinden 108 sayfalık _Bioinformatics_ ders notu PDF'i ile temel sorgular ("What is FASTA?", "What are the steps of the BLAST Algorithm?") yapılarak sistemin tepkileri ölçülmüştür.

**Modeller Üzerine Kanaat Notları:**

-   **Qwen3 4B:** Genel olarak en tutarlı model. Bazı spesifik sorularda yanlış cevap verebiliyor ancak "system prompt" üzerinde yapılan küçük oynamalara (prompt tuning) en iyi tepkiyi verip düzelen model oldu.
    
-   **Qwen2.5 3B:** Sentezlemek yerine metni PDF'ten doğrudan kopyala-yapıştır yapma eğiliminde. Bazen de bilgi olduğu halde "belgede yoktur" hatasına düşüyor.
    
-   **IBM Granite 3.1 2B:** Halüsinasyon (uydurma) oranı kabul edilemez düzeyde yüksek bulundu.
    
-   **Qwen3 1.7B:** RAG entegrasyonunda tamamen başarısız oldu, her soruya "belgede yoktur" yanıtı döndürdü.
    
-   **Microsoft Phi-4:** Yanıt boyutu uzadıkça metin bütünlüğünde ciddi bozulmalar/saçmalamalar gözlemlendi.
    
-   **Phi 3.5 & DeepSeek R1:** Beklentinin çok altında kaldı.
    
-   **Episteme AI:** VRAM limitlerine takılarak Out-of-Memory hatası verdi.
    

## 3. Kantitatif Doğrulama (LLM-as-a-Judge)

Manuel testlerin ardından 5 model (Qwen 3.0 4B, Qwen 2.5 3B, IBM Granite 2B, Phi-4 mini, LLaMA 3.2 3B Tuned), **Grok API** kullanılarak otomatik ve objektif bir puanlamaya tabi tutulmuştur.

## Test Seti 1: Qasper Veriseti

Hazır soru-cevap çiftleri içeren 10 adet akademik metin üzerinden yapılan ilk temel RAG testinde (Ortalama Doğruluk):

1.  **Phi-4:** %46.2
    
2.  **Qwen3 4B:** %43.5
    
3.  **IBM Granite:** %40.3
    
4.  **Qwen2.5 3B:** %39.0
    
5.  **LLama3.1 Tuned****:** %35.3 (Not: Bu standart testte modeller birbirine yakın performans gösterdi.)
    

## Test Seti 2: Gerçek Hayat Stres Testleri

Sistemin gerçek dünya koşullarındaki sınırlarını görmek için 6 farklı zorlu belge kullanıldı:

-   Bioinformatics ders notu (Metin yoğun PDF)
    
-   ResNet & LSTM makaleleri (Akademik format)
    
-   TUSAŞ halka açık el kitabı (Türkçe kurumsal metin)
    
-   "Attention is All You Need" makalesinin telefonla çekilmiş fotoğrafı (Kötü OCR senaryosu)
    
-   JAX dokümantasyon ekran görüntüsü (Kod ve tablo içeren görsel)
    

Gemini Pro kullanılarak bu belgelerden tarafsız sorular üretildi (%80 İngilizce, %20 Türkçe / %80 Belge içi, %20 Belge dışı). Grok API ile yapılan puanlama sonuçları (Ortalama Başarı Yüzdeleri):

  

Kategori

1. Model

2. Model

Diğer Modeller (Ortalama Başarı)

**Genel Başarı (Tümü)**

**Qwen3 (%81.1)**

Qwen2.5 (%69.8)

LLaMA (%50.4), IBM (%48.0), Phi-4 (%27.6)

**İngilizce Metinler**

**Qwen3 (%85.2)**

Qwen2.5 (%64.4)

LLaMA (%54.0), IBM (%51.4), Phi-4 (%13.3)

**Türkçe Metinler**

**Qwen2.5 (%66.0)**

Qwen3 (%60.0)

LLaMA (%40.0), Phi-4 (%28.0), IBM (%16.0)

**Görsel/OCR Soruları**

**Qwen3 (%90.0)**

**Qwen2.5 (%90.0)**

IBM (%70.0), Phi-4 (%70.0), LLaMA (%50.0)

E-Tablolar'a aktar

## 4. Kritik Senaryo Testleri

**Belgede Olmayan Bir Bilgi Sorulduğunda Sistem Nasıl Davranıyor?** Sistemin güvenlik ve doğruluk açısından en önemli özelliklerinden biri "bilmiyorum" diyebilmesidir. Test setindeki soruların %20'si özellikle belgede yer almayan konulardan seçilmiştir.

-   **Sonuç:** Qwen3 4B ve LLaMA 3.2 modelleri bu testten **%100 tam puan** alarak, "This information is not in the document" kuralına kusursuz uymuş ve hiçbir halüsinasyon üretmemiştir. (Qwen 2.5 %60'ta kalırken, IBM %10 ile bu konuda sınıfta kalmıştır).
    

**Sistemin Başarısız Olduğu veya Yetersiz Kaldığı Durumlar:**

-   **Dil Bariyeri:** Test sonuçlarında net bir şekilde görüldüğü üzere, sistem İngilizce metinlerde %85 başarı yakalarken Türkçe metinlerde bu oran %60-66 bandına düşmektedir. Modellerin anadili İngilizce olduğu için Türkçe semantik aramalarda (vektör eşleştirmelerinde) daha zayıf kalmaktadır.
    
-   **Aşırı Karmaşık Tablolar:** OCR sistemi, satır ve sütun çizgileri net olmayan karmaşık görsellerdeki tabloları metne dönüştürürken yapıyı bozabilmekte, bu da RAG modelinin bağlamı yanlış anlamasına yol açabilmektedir.
    

## 5. Sonuç Kararı

Gerek "belgede olmayan bilgiye halüsinasyon üretmeme" konusundaki %100'lük başarısı, gerek zorlu OCR senaryolarındaki %90'lık performansı, gerekse genel ortalamada (%81.1) rakiplerine açık ara fark atması sebebiyle projenin ana motoru olarak **Qwen 3.0 4B** modeli seçilmiştir.
