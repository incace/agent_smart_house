# Agentic IoT Control System (OpenClaw + MCP + Home Assistant)

## 🏗 Архитектура системы

```text
[ Пользователь ] 
       |
[ Интерфейс: OpenWebUI / Telegram ]
       |
[ Агент: OpenClaw ] <----------> [ LLM Backend: Router.ai (DeepSeek/Llama) ]
       |
[ MCP Server (Python/Node) ] 
       |
[ API Home Assistant ] <-------> [ Raspberry Pi 4 / Jetson ]
                                        |
                 _______________________|_______________________
                |                       |                       |
          [ ESP8266 ]             [ Датчики ]            [ Реле/Приводы ]
```

---

## 🛠 Компоненты системы

1.  **Hardware:**
    *   **Контроллер:** Raspberry Pi 4 или NVIDIA Jetson (рекомендуется для локальных вычислений).
    *   **Периферия:** ESP8266 (прошивка ESPHome или Tasmota), датчики (температура, влажность, CO2), исполнительные устройства.
2.  **IoT Platform:** Home Assistant (HA) — агрегатор всех устройств.
3.  **MCP Server:** Прослойка, преобразующая сервисы HA в "инструменты" (tools) для LLM.
4.  **Agent Logic:** OpenClaw — оркестратор работы агента.
5.  **LLM:** Модели через OpenRouter.ai.
6.  **UI:** OpenWebUI (предпочтительно) для удобного чата.

---

## 🧠 Выбор LLM (анализ Router.ai)

Для работы агента важна поддержка **Function Calling (Tool Use)** и низкая задержка.

| Модель | Стоимость ($/1M токенов) | Контекст | Параметры | Ориентация |
| :--- | :--- | :--- | :--- | :--- |
| **DeepSeek-V3** | ~$0.15 (самая низкая) | 128k | 671B (MoE) | **Лидер по цене/качеству** |
| **Llama-3.1-70B** | ~$0.60 | 128k | 70B | Стабильное следование инструкциям |
| **GPT-4o-mini** | ~$0.15 | 128k | - | Отличный Tool Use, высокая скорость |

*   **Основная:** `DeepSeek-V3` через OpenRouter — лучший выбор по стоимости и логике. 
*   **Резервная:** `GPT-4o-mini` — если требуется максимальная скорость отклика инструментов.

---

## 🚀 Инструкция по развертыванию

### Шаг 1: Подготовка Home Assistant
1. Установить HA на Raspberry Pi 4/Jetson.
2. Подключите все датчики и ESP8266.
3. Создать **Long-Lived Access Token** в профиле пользователя HA для доступа к API.

### Шаг 2: Реализация MCP-сервера
Сервер должен предоставлять список инструментов (например: `get_temperature`, `turn_on_light`).
1. Использовать Python SDK для MCP (`fastmcp` или `mcp` библиотеку).
2. Написать скрипт, который пробрасывает `states` и `services` из HA в MCP Tools.
3. Пример структуры:
   ```python
   # mcp_server_ha.py
   @app.tool()
   async def control_device(entity_id: str, action: str):
       """Управляет устройством в Home Assistant (action: turn_on, turn_off)"""
       # Вызов API HA
   ```

### Шаг 3: Настройка OpenClaw
1. Склонировать репозиторий OpenClaw.
2. В конфиге (`config.yaml`) указать адрес вашего MCP сервера.
3. Подключить LLM:
   ```yaml
   provider: openrouter
   api_key: ${OPENROUTER_API_KEY}
   model: deepseek/deepseek-chat
   ```

### Шаг 4: Развертывание интерфейса (OpenWebUI)
1. Развернуть через Docker:
   ```bash
   docker run -d -p 3000:8080 --add-host=host.docker.internal:host-gateway -v open-webui:/app/backend/data --name open-webui ghcr.io/open-webui/open-webui:main
   ```
2. В настройках подключить OpenClaw как внешний API (OpenAI-compatible).

---

## 📝 Сценарии для тестирования (Prioritized)

1.  **Сценарий «Экономия и климат» (Priority 1):**
    *   *Запрос:* «Если температура на датчике ESP8266 выше 25 градусов и в комнате кто-то есть, включи охлаждение».
    *   *Проверка:* Агент должен последовательно вызвать `get_temperature`, `get_presence` и затем `turn_on_cooler`.

2.  **Сценарий «Безопасность» (Priority 2):**
    *   *Запрос:* «Проверь состояние всех окон и, если какое-то открыто, отправь уведомление в ТГ».

3.  **Сценарий «Сложная автоматизация»:**
    *   *Запрос:* «Подготовь комнату к просмотру кино» (агент должен сам догадаться закрыть шторы, приглушить свет и включить проектор через цепочку действий).

---

## 📁 Структура репозитория
*   `/mcp-server` — исходный код MCP сервера на Python.
*   `/configs` — конфигурационные файлы для OpenClaw и HA.
*   `/scripts` — скрипты для быстрой прошивки ESP8266.
*   `docker-compose.yml` — запуск всей инфраструктуры (HA, OpenWebUI, OpenClaw) одной командой.
