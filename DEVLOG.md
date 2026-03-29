4.1. DEVLOG.md — Geliştirme Süreci Kaydı
Bu belge, savunma sanayii için tamamen yerel (local) çalışması gereken, veri güvenliği odaklı chatbot projesinin geliştirme sürecini, karşılaşılan darboğazları ve alınan teknik kararları kronolojik olarak özetlemektedir.
Geliştirme Günlüğü
1. Gün: Temel Atma ve Mimari Kararlar
    • Problem: Projenin savunma sanayi şirketine hazırlanacak olması, sistemin tamamen çevrimdışı ve yerel çalışmasını zorunlu kıldı. Frontend tecrübem olmadığı ve 1 haftalık kısıtlı bir süre olduğu için hızlı prototipleme amacıyla başlangıçta Streamlit tercih edildi.
    • Geliştirme: PDF'lerden ve fotoğraflardan metin çıkaran temel fonksiyonlar yazıldı. Eşzamanlı farklı dosya formatlarını destekleyen çoklu dosya yükleme sistemi tasarlandı.
    • Kritik Karar/Revizyon: Görsel okuma için PyTesseract yerine EasyOCR denendiğinde ciddi performans sorunları gözlemlendi. RAG ve yerel LLM entegrasyonu da eklendiğinde Streamlit mimarisinin darboğaz yaratacağı anlaşıldı. Bu nedenle projenin ilk gününde teknoloji yığını değiştirildi: Arayüz için Node.js/React (Vite) geçişi yapıldı, backend ise FastAPI ile yeniden kurgulandı.
2. Gün: Yerel LLM Entegrasyonu ve Donanım Kısıtlamaları
    • Problem: Kullanılan donanımın (RTX 2060 laptop) 6GB VRAM sınırına sahip olması. İlk denemelerde 4B ve üzeri modellerde Out of Memory (OOM) hatası alındı.
    • Çözüm: Başlangıç modeli olarak Qwen 2.5 3B seçildi. Modellerin donanımda çalışabilmesi için özel bir "model loader" yazılarak INT4 (quantization) formatında çalıştırılması sağlandı.
    • Geliştirme: LLM bağlamını korumak için arka planda (backend) "Trimmed Chat History" sistemi eklendi. Frontend arayüzünde kullanıcı tüm sohbet geçmişini kesintisiz görmeye devam ederken, bellek taşmasını (OOM) önlemek amacıyla sadece modele gönderilen metin (content) içeriği, belirlenen max_token limitine göre en eski mesajlardan kırpılarak (trimming) optimize edildi.
3. Gün: Veritabanı, RAG ve Model Arayışı
    • Problem: Modele takip soruları sorulduğunda veya bağlam genişlediğinde yanlış cevaplar üretildiği tespit edildi.
    • Geliştirme: Veri kalıcılığı için SQL veritabanı sistemine geçildi. Frontend-Backend ayrımı tam olarak oturtuldu; arayüz sadece veri taşıma ve sonuç gösterme işlevine indirgendi. LangChain kullanılarak RAG mimarisi entegre edildi. Türkçe ve İngilizce metinleri anlaşılabilmesi için ‘paraphrase-multilingual-MiniLM-L12-v2’ embeddings modeli kullanıldı.
    • Model Denemeleri: HuggingFace Leaderboard üzerinden alternatif modeller incelendi. Hedef kitlenin kurumsal bir firma olması sebebiyle IBM Granite 3.1 2B-Instruct denendi, ancak ilk testlerde Qwen'e kıyasla yetersiz kaldı.
    • UI Güncellemeleri: Kullanıcı deneyimini artırmak için "yanıt hazırlanıyor" animasyonu ve yeni mesaja otomatik odaklanan scroll eklendi.
4. Gün: Model Karşılaştırmaları ve RAG Optimizasyonu
    • Model Test Süreci:
        ◦ IBM Granite: Halüsinasyon oranı çok yüksek bulundu.
        ◦ Qwen3 1.7B: RAG performansında başarısız oldu, sürekli "belgede yoktur" yanıtı döndürdü.
        ◦ Microsoft Phi-4: Yanıt boyutu uzadıkça metin bütünlüğünde bozulmalar gözlemlendi.
        ◦ Llama 3.2 Tuned (iFaz 3B): Base Meta modeli için dışarıdan erişim izni/istek gerektirdiği için "tamamen yerel sistem" kuralını ihlal ettiğinden elendi.
        ◦ Phi 3.5 & DeepSeek R1: Beklentinin çok altında, kötü sonuçlar verdi.
        ◦ Episteme AI: VRAM limitlerine takıldı.
    • Kritik Karar (RAG): RAG sisteminde metinleri 300 karakterlik sabit parçalara bölen (fixed chunking) yapıdan, anlamsal bütünlüğü koruyan "Semantic Chunker" yapısına geçildi. Bu değişiklik doğruluk oranında belirgin bir artış sağladı. RAG bağlam boyutunun optimize edilmesiyle, Qwen3 4B modeli 6GB VRAM sistemde kararlı çalışabilir hale geldi ve şu ana kadarki en iyi performansı sundu.
5. Gün: Veri İşleme Geliştirmeleri ve Sistematik Doğrulama
    • Geliştirme: PDF okuyucu modülü tamamen yenilendi. Sadece düz metin okumak yerine; metinleri, tabloları ve görselleri ayrıştırarak bağımsız şekilde inceleyen ve bağlam oluşturan hibrit bir yapıya geçildi.
    • Değerlendirme (Evaluation): Sistematik doğruluk ölçümü için Qasper veri seti kullanıldı. Seçilen 10 metin ve soru-cevap çifti üzerinden oluşturulan 30 soruluk set ile 5 farklı model (Qwen 2.5 3B, Qwen3 4B, IBM Granite 3.1 2B, Phi-4-mini, Llama3.2 3B) test edildi. Çıktıların objektif değerlendirmesi (LLM-as-a-judge) için Grok API kullanılarak puanlama yapıldı.
6. Gün: Gerçek Hayat Stres Testleri
    • Geliştirme: Sistem, 6 farklı gerçek hayat belgesiyle test edildi: Bioinformatics ders notları, ResNet makalesi, LSTM makalesi, TUSAŞ halka açık el kitabı, telefon kamerasıyla çekilmiş "Attention is All You Need" makale fotoğrafı ve JAX dokümantasyon ekran görüntüsü.
    • Değerlendirme: Bu karmaşık belgeler üzerinden tarafsız ve zorlayıcı sorular üretmek için Gemini Pro kullanıldı. Üretilen sorular yerel sisteme soruldu ve alınan cevaplar tekrar Grok API üzerinden puanlanarak final doğruluk metrikleri oluşturuldu.

Proje Retrospektifi (Özet Değerlendirme)
    • Problemi nasıl parçaladınız? Proje dört ana modüle ayrıldı: Veri çıkarma/işleme (OCR, PDF parsing), Veri depolama ve getirme (SQL, RAG, Semantic Chunking), Yerel Model Yönetimi (FastAPI, Custom int4 loader) ve Kullanıcı Arayüzü (React/Vite).
    • Hangi yaklaşımları denediniz? Hangisi işe yaramadı ve neden? Streamlit ile hızlı prototipleme denendi ancak OCR ve yerel LLM'in aynı thread/yapı üzerinde çalışması performansı çökerttiği için vazgeçildi. RAG sisteminde "Fixed-size chunking" (sabit boyutlu bölme) denendi, anlamsal bütünlüğü bozduğu ve modelin yanlış cevap vermesine yol açtığı için Semantic Chunking'e geçildi.
    • Kritik karar noktalarında hangi alternatifleri değerlendirdiniz? En kritik karar donanım kısıtı (6GB VRAM) ile model kapasitesi arasındaki dengeydi. Bulut tabanlı API'ler güvenlik kısıtları nedeniyle kullanılamadı. Açık kaynaklı modeller için INT4 quantizasyonu uygulanarak Qwen3 4B ve Qwen 2.5 3B modelleri arasında bir tercih yapıldı. 
    • Nerede takıldınız? Nasıl çözdünüz? Özellikle model bağlamı (context) dolduğunda sistemin hafıza hatası vermesi (OOM) büyük bir bloklayıcıydı. Çözüm olarak RAG parçalama (Semantic Chunker) kullanıldı.
    • Şu an bildiğinizle baştan başlasanız neyi farklı yapardınız? Streamlit adımı tamamen atlanarak projeye doğrudan React ve FastAPI mimarisiyle başlanabilirdi. RAG modeli sisteme ilk günden adapte edilmeliydi. Model bilimsel değerlendirme sürecini (Qasper veri seti ve Grok API ile LLM-as-a-judge yapısı) projenin en sonunda değil, 3. gün RAG sistemini kurar kurmaz CI/CD hattı gibi kurgulardım; böylece model denemelerinde daha hızlı ve analitik karar verebilirdim. Ayrıca, database sistemi çok temel yapıda, geliştirilecek yönleri kesinlikle var.
