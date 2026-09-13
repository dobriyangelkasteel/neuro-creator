from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn
import requests
import os
import base64
import time
import io
import json
app = FastAPI()

PAYMENTS_FILE = "payments.json"

def load_payments():
    """Загружает статусы оплат из файла"""
    if os.path.exists(PAYMENTS_FILE):
        with open(PAYMENTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_payment(user_id: str, status: str):
    """Сохраняет статус оплаты для пользователя"""
    payments = load_payments()
    payments[user_id] = status
    with open(PAYMENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(payments, f)

def is_paid(user_id: str) -> bool:
    """Проверяет, оплачена ли генерация"""
    payments = load_payments()
    return payments.get(user_id) == "paid"

# ВСТАВЬТЕ ВАШ КЛЮЧ ОТ KREA
import os
KREA_API_KEY = os.getenv("KREA_API_KEY", "")

def upload_to_temp(image_bytes):
    """Временная функция: возвращает base64 изображения"""
    return base64.b64encode(image_bytes).decode("utf-8")

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Нейрокреатор — Оживи фото</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:opsz@14..32&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Inter', sans-serif;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            padding: 16px;
        }
        .container {
            background: rgba(255,255,255,0.07);
            backdrop-filter: blur(20px);
            border-radius: 24px;
            padding: 28px 24px;
            max-width: 700px;
            width: 100%;
            box-shadow: 0 25px 50px -12px rgba(0,0,0,0.6);
            border: 1px solid rgba(255,255,255,0.08);
        }
        h1 {
            font-size: 26px;
            font-weight: 700;
            color: #fff;
            text-align: center;
            margin-bottom: 6px;
        }
        h1 span {
            background: linear-gradient(135deg, #a78bfa, #f472b6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .subtitle {
            color: rgba(255,255,255,0.6);
            text-align: center;
            font-size: 14px;
            margin-bottom: 24px;
            border-bottom: 1px solid rgba(255,255,255,0.06);
            padding-bottom: 16px;
        }
        .upload-box {
            background: rgba(255,255,255,0.04);
            border: 2px dashed rgba(255,255,255,0.15);
            border-radius: 14px;
            padding: 20px;
            text-align: center;
            cursor: pointer;
            transition: all 0.2s;
            margin-bottom: 16px;
        }
        .upload-box:hover {
            border-color: rgba(255,255,255,0.3);
            background: rgba(255,255,255,0.07);
        }
        .upload-box input { display: none; }
        .upload-label {
            display: inline-block;
            background: rgba(255,255,255,0.08);
            color: #fff;
            padding: 10px 22px;
            border-radius: 60px;
            font-size: 14px;
            cursor: pointer;
            border: 1px solid rgba(255,255,255,0.06);
        }
        .file-name {
            color: rgba(255,255,255,0.4);
            font-size: 12px;
            margin-top: 8px;
        }
        .form-group { margin-bottom: 14px; }
        .form-group label {
            display: block;
            color: rgba(255,255,255,0.8);
            font-size: 13px;
            margin-bottom: 5px;
        }
        input[type="text"], select {
            width: 100%;
            padding: 11px 14px;
            border-radius: 12px;
            border: 1px solid rgba(255,255,255,0.1);
            background: rgba(255,255,255,0.05);
            color: #fff;
            font-size: 13px;
            font-family: 'Inter', sans-serif;
            outline: none;
        }
        select option { background: #1a1a2e; }
        .btn-primary {
            background: linear-gradient(135deg, #6366f1, #8b5cf6);
            color: #fff;
            border: none;
            padding: 15px 20px;
            border-radius: 60px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            width: 100%;
            margin-top: 8px;
            box-shadow: 0 8px 20px -6px rgba(99, 102, 241, 0.4);
            transition: all 0.2s;
        }
        .btn-primary:hover { transform: translateY(-2px); }
        .btn-primary:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }
        .spinner {
            border: 3px solid rgba(255,255,255,0.08);
            border-top: 3px solid #8b5cf6;
            border-radius: 50%;
            width: 44px;
            height: 44px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
        .status-text {
            color: rgba(255,255,255,0.7);
            font-size: 14px;
            text-align: center;
            margin-top: 8px;
        }
        .error-text {
            color: #fca5a5;
            background: rgba(220, 38, 38, 0.15);
            padding: 12px;
            border-radius: 12px;
            font-size: 14px;
            text-align: center;
            margin-top: 16px;
        }
        .video-wrapper {
            margin-top: 20px;
            animation: fadeUp 0.5s ease;
        }
        @keyframes fadeUp {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        video {
            width: 100%;
            border-radius: 16px;
            box-shadow: 0 12px 30px -8px rgba(0,0,0,0.5);
            background: #000;
        }
        .btn-download {
            display: inline-block;
            background: linear-gradient(135deg, #10b981, #059669);
            color: #fff;
            padding: 12px 24px;
            border-radius: 60px;
            text-decoration: none;
            font-size: 14px;
            font-weight: 600;
            margin-top: 14px;
            text-align: center;
            width: 100%;
        }
        #result { margin-top: 20px; }
        @media (max-width: 480px) {
            .container { padding: 20px 16px; }
            h1 { font-size: 22px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>✨ <span>Нейрокреатор</span></h1>
        <p class="subtitle">Оживите любое фото за пару минут с помощью ИИ</p>

        <div class="upload-box" onclick="document.getElementById('fileInput').click()">
            <input type="file" id="fileInput" accept="image/*">
            <span class="upload-label">📸 Выбрать фото</span>
            <div id="fileName" class="file-name">Файл не выбран</div>
        </div>

        <div class="form-group">
            <label>🎬 Промпт (что должно происходить в видео)</label>
            <input type="text" id="prompt" value="gentle camera movement, subtle smile, soft lighting" placeholder="Опишите движение">
        </div>

        <div class="form-group">
            <label>⏱️ Длительность</label>
            <select id="duration">
                <option value="5" selected>5 секунд</option>
                <option value="10">10 секунд</option>
            </select>
        </div>

        <div class="form-group">
            <label>📐 Пропорции</label>
            <select id="aspectRatio">
                <option value="16:9" selected>16:9 (горизонтальное)</option>
                <option value="9:16">9:16 (вертикальное)</option>
                <option value="1:1">1:1 (квадрат)</option>
            </select>
        </div>

        <button class="btn-primary" id="submitBtn" onclick="generateVideo()">🎬 Оживить фото</button>

        <div id="result"></div>

        <!-- БЛОК С РЕКВИЗИТАМИ ДЛЯ ЮKASSA -->
        <div style="margin-top: 24px; padding: 16px; background: rgba(255,255,255,0.04); border-radius: 12px; border: 1px solid rgba(255,255,255,0.06); text-align: center;">
            <p style="color: rgba(255,255,255,0.5); font-size: 12px; line-height: 1.6;">
                <strong style="color: rgba(255,255,255,0.7);">Самозанятый:</strong> Харисов Адель Алмазович<br>
                <strong style="color: rgba(255,255,255,0.7);">ИНН:</strong> 164815873478<br>
                <strong style="color: rgba(255,255,255,0.7);">Email:</strong> adel.samazov@mail.ru
            </p>
        </div>
    </div>

    <script>
        let currentVideoUrl = null;

        document.getElementById('fileInput').addEventListener('change', function(e) {
            document.getElementById('fileName').textContent = e.target.files[0]?.name || 'Файл не выбран';
        });

        async function generateVideo() {
            const file = document.getElementById('fileInput').files[0];
            if (!file) {
                alert('📸 Сначала выберите фото!');
                return;
            }

            const resultDiv = document.getElementById('result');
            const submitBtn = document.getElementById('submitBtn');
            submitBtn.disabled = true;

            resultDiv.innerHTML = `
                <div class="spinner"></div>
                <p class="status-text" id="statusText">📤 Загружаем фото...</p>
            `;

            const formData = new FormData();
            formData.append('file', file);
            formData.append('prompt', document.getElementById('prompt').value);
            formData.append('duration', document.getElementById('duration').value);
            formData.append('aspect_ratio', document.getElementById('aspectRatio').value);

            try {
                const response = await fetch('/generate', {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();

                if (!response.ok) {
                    throw new Error(data.error || 'Ошибка генерации');
                }

                pollStatus(data.job_id);

            } catch (error) {
                resultDiv.innerHTML = `<p class="error-text">❌ ${error.message}</p>`;
                submitBtn.disabled = false;
            }
        }

        async function pollStatus(jobId) {
            const resultDiv = document.getElementById('result');
            let attempts = 0;
            const maxAttempts = 120;

            const interval = setInterval(async () => {
                attempts++;
                
                if (attempts > maxAttempts) {
                    clearInterval(interval);
                    resultDiv.innerHTML = `<p class="error-text">⏱️ Время ожидания истекло</p>`;
                    document.getElementById('submitBtn').disabled = false;
                    return;
                }

                try {
                    const response = await fetch(`/status/${jobId}`);
                    const data = await response.json();
                    
                    document.getElementById('statusText').textContent = 
                        `⏳ Генерация... (${attempts * 5} сек)`;

                    if (data.status === 'completed') {
                        clearInterval(interval);
                        resultDiv.innerHTML = `
                            <div class="video-wrapper">
                                <video src="${data.video_url}" controls autoplay loop></video>
                                <a href="${data.video_url}" download class="btn-download">⬇️ Скачать видео</a>
                            </div>
                        `;
                        document.getElementById('submitBtn').disabled = false;
                    } else if (data.status === 'failed') {
                        clearInterval(interval);
                        resultDiv.innerHTML = `<p class="error-text">❌ Ошибка генерации: ${data.error || 'неизвестная'}</p>`;
                        document.getElementById('submitBtn').disabled = false;
                    }
                } catch (error) {
                    console.error('Ошибка опроса:', error);
                }
            }, 5000);
        }
    </script>
</body>
</html>
    """

@app.post("/generate")
async def generate(
    file: UploadFile = File(...),
    prompt: str = Form("gentle camera movement"),
    duration: int = Form(5),
    aspect_ratio: str = Form("16:9")
):
    try:
        # 1. Читаем загруженное фото
        image_data = await file.read()
        print(f"📸 Фото загружено: {len(image_data)} байт")
        
        # 2. Преобразуем в base64 data URI
        image_base64 = base64.b64encode(image_data).decode("utf-8")
        image_data_uri = f"data:image/jpeg;base64,{image_base64}"
        print(f"🔢 Base64 размер: {len(image_data_uri)} символов")
        
        # 3. Отправляем запрос в Krea
        url = "https://api.krea.ai/generate/video/kling/kling-2.5"
        headers = {
            "Authorization": f"Bearer {KREA_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "start_image": image_data_uri,
            "prompt": prompt,
            "duration": duration,
            "aspect_ratio": aspect_ratio
        }
        
        print(f"📤 Отправляем в Krea...")
        print(f"   prompt: {prompt}")
        print(f"   duration: {duration}")
        print(f"   aspect_ratio: {aspect_ratio}")
        
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        
        print(f"📥 Статус Krea: {response.status_code}")
        print(f"📄 Ответ Krea: {response.text[:500]}")
        
        if response.status_code != 200:
            return JSONResponse(
                status_code=response.status_code,
                content={"error": f"Ошибка Krea ({response.status_code}): {response.text}"}
            )
        
        data = response.json()
        job_id = data.get("job_id")
        print(f"🆔 Job ID: {job_id}")
        
        return JSONResponse(content={"job_id": job_id})
    
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"❌ ОШИБКА: {error_trace}")
        return JSONResponse(status_code=500, content={"error": str(e), "trace": error_trace})

@app.get("/status/{job_id}")
async def status(job_id: str):
    try:
        url = f"https://api.krea.ai/jobs/{job_id}"
        headers = {"Authorization": f"Bearer {KREA_API_KEY}"}
        
        response = requests.get(url, headers=headers, timeout=30)
        data = response.json()
        
        status = data.get("status")
        
        if status in ["completed", "succeeded"]:
            video_url = data.get("result", {}).get("urls", [None])[0]
            return JSONResponse(content={
                "status": "completed",
                "video_url": video_url
            })
        elif status == "failed":
            return JSONResponse(content={
                "status": "failed",
                "error": data.get("error", "Неизвестная ошибка")
            })
        else:
            return JSONResponse(content={"status": status or "processing"})
    
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
# ===== ВЕБХУК ДЛЯ ЮKASSA =====
from fastapi import Request

@app.post("/yookassa-webhook")
async def yookassa_webhook(request: Request):
    """
    Принимает уведомления от ЮKassa о статусе платежа.
    """
    try:
        event_json = await request.json()
        event = event_json.get("event")
        
        if event == "payment.succeeded":
            payment_object = event_json.get("object", {})
            user_id = payment_object.get("metadata", {}).get("user_id")
            
            if user_id:
                save_payment(user_id, "paid")
                print(f"✅ Оплата прошла для пользователя: {user_id}")
            else:
                print("⚠️ В уведомлении нет user_id (metadata)")
        
        return {"status": "ok"}
    
    except Exception as e:
        print(f"❌ Ошибка в вебхуке: {e}")
        return {"status": "ok"}
        
    if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)