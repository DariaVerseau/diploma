#!/usr/bin/env python3
"""
Тестирование веб-сервиса обработки изображений
Запуск: python test.py
"""

import requests
import time
import io
import psutil
import os
from PIL import Image

API_URL = "http://localhost:8080/api/v1"

class TestService:
    def __init__(self):
        self.token = None
        self.image_id = None
        self.test_email = f"test_{int(time.time())}@example.com"
        self.test_password = "test123456"

    def get_memory_usage(self):
        """Возвращает текущее потребление оперативной памяти процессом в МБ"""
        process = psutil.Process(os.getpid())
        memory_mb = process.memory_info().rss / 1024 / 1024
        return round(memory_mb, 2)

    def log_memory(self, operation_name):
        """Выводит потребление памяти после операции"""
        memory_mb = self.get_memory_usage()
        print(f"   Потребление RAM: {memory_mb} МБ")

    def test_health(self):
        print("\n Health check...")
        resp = requests.get("http://localhost:8080/health", timeout=5)
        assert resp.status_code == 200
        print("  API Gateway работает")

    def test_register(self):
        print("\n Регистрация...")
        resp = requests.post(
            f"{API_URL}/register",
            json={"email": self.test_email, "password": self.test_password}
        )
        assert resp.status_code == 201
        print("  Регистрация успешна")

    def test_login(self):
        print("\n Логин...")
        resp = requests.post(
            f"{API_URL}/login",
            json={"email": self.test_email, "password": self.test_password}
        )
        assert resp.status_code == 200
        self.token = resp.json().get("token")
        print("  Логин успешен")

    def test_upload_image(self):
        print("\n Загрузка изображения...")
        img = Image.new('RGB', (800, 600), color='red')
        buf = io.BytesIO()
        img.save(buf, format='JPEG')
        buf.seek(0)
        
        resp = requests.post(
            f"{API_URL}/images",
            files={"image": ("test.jpg", buf, "image/jpeg")},
            data={"title": "Тестовое изображение"},
            headers={"Authorization": f"Bearer {self.token}"}
        )
        
        assert resp.status_code == 201, f"Ошибка: {resp.status_code}, {resp.text}"
        self.image_id = resp.json().get("id")
        print(f"  Изображение загружено, id={self.image_id}")

    def test_get_gallery(self):
        print("\n Получение галереи...")
        resp = requests.get(
            f"{API_URL}/images",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        assert resp.status_code == 200
        print("  Галерея получена")

    def test_upscale_2x(self):
        print("\n Увеличение разрешения (в 2 раза)...")
        start = time.time()
        resp = requests.post(
            f"{API_URL}/ml/upscale",
            data={"image_id": self.image_id, "scale": "2"},
            headers={"Authorization": f"Bearer {self.token}"},
            timeout=120
        )
        elapsed = time.time() - start
        assert resp.status_code == 200
        print(f"   Время выполнения: {elapsed:.2f} сек")
        self.log_memory("upscale_2x")

    def test_upscale_4x(self):
        print("\n Увеличение разрешения (в 4 раза)...")
        start = time.time()
        resp = requests.post(
            f"{API_URL}/ml/upscale",
            data={"image_id": self.image_id, "scale": "4"},
            headers={"Authorization": f"Bearer {self.token}"},
            timeout=120
        )
        elapsed = time.time() - start
        assert resp.status_code == 200
        print(f"   Время выполнения: {elapsed:.2f} сек")
        self.log_memory("upscale_4x")

    def test_style_transfer(self):
        print("\n Перенос стиля...")
        start = time.time()
        resp = requests.post(
            f"{API_URL}/ml/style_transfer",
            data={"image_id": self.image_id, "style": "vangogh"},
            headers={"Authorization": f"Bearer {self.token}"},
            timeout=120
        )
        elapsed = time.time() - start
        assert resp.status_code == 200
        print(f"   Время выполнения: {elapsed:.2f} сек")
        self.log_memory("style_transfer")

    def test_enhance(self):
        print("\n Восстановление портретов...")
        start = time.time()
        resp = requests.post(
            f"{API_URL}/ml/enhance",
            data={"image_id": self.image_id, "fidelity_weight": "0.7", "postprocess": "true"},
            headers={"Authorization": f"Bearer {self.token}"},
            timeout=120
        )
        elapsed = time.time() - start
        assert resp.status_code == 200
        print(f"   Время выполнения: {elapsed:.2f} сек")
        self.log_memory("enhance")

    def test_postprocess(self):
        print("\n Классическая постобработка...")
        start = time.time()
        resp = requests.post(
            f"{API_URL}/ml/postprocess",
            data={"image_id": self.image_id, "sharpness": "1.25", "contrast": "1.12"},
            headers={"Authorization": f"Bearer {self.token}"},
            timeout=120
        )
        elapsed = time.time() - start
        assert resp.status_code == 200
        print(f"   Время выполнения: {elapsed:.2f} сек")
        self.log_memory("postprocess")

    def test_unauthorized(self):
        print("\n Доступ без токена...")
        resp = requests.get(f"{API_URL}/images")
        assert resp.status_code == 401
        print("  Доступ запрещён")

    def run(self):
        print("=" * 60)
        print("ТЕСТИРОВАНИЕ ВЕБ-СЕРВИСА")
        print("=" * 60)

        try:
            self.test_health()
            self.test_register()
            self.test_login()
            self.test_upload_image()
            self.test_get_gallery()
            self.test_upscale_2x()
            self.test_upscale_4x()
            self.test_style_transfer()
            self.test_enhance()
            self.test_postprocess()
            self.test_unauthorized()

            print("\n" + "=" * 60)
            print("ВСЕ ТЕСТЫ ПРОЙДЕНЫ")
            print("=" * 60)

        except AssertionError as e:
            print(f"\nТЕСТ НЕ ПРОЙДЕН: {e}")
        except Exception as e:
            print(f"\nОШИБКА: {e}")

if __name__ == "__main__":
    TestService().run()