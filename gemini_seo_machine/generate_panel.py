import json
from pathlib import Path
from datetime import datetime

def generate_dashboard():
    data_file = Path("panel_data.json")
    if data_file.exists():
        try:
            with open(data_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {}
    else:
        data = {
            "verdict": "green",
            "verdict_text": "Конвейер работает штатно",
            "planned_articles": 28,
            "days_reserve": 9.3,
            "traffic_yandex": 4120,
            "traffic_google": 2190,
            "quick_wins_count": 8,
            "last_audit_date": datetime.now().strftime("%Y-%m-%d"),
            "critical_errors": 0
        }

    html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Панель управления SEO-машиной (Gemini Engine)</title>
    <style>
        :root {{
            --bg: #090d16;
            --card: #131b2e;
            --text: #f1f5f9;
            --text-dim: #94a3b8;
            --green: #10b981;
            --yellow: #f59e0b;
            --red: #ef4444;
            --border: #1e293b;
            --accent: #3b82f6;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            background: var(--bg);
            color: var(--text);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            padding: 32px 24px;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 28px;
            padding-bottom: 20px;
            border-bottom: 1px solid var(--border);
        }}
        .logo-group h1 {{ font-size: 24px; font-weight: 700; }}
        .logo-group p {{ color: var(--text-dim); font-size: 13px; margin-top: 4px; }}
        .badge {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 8px 18px;
            border-radius: 9999px;
            font-size: 14px;
            font-weight: 600;
            background: rgba(16, 185, 129, 0.15);
            color: var(--green);
            border: 1px solid var(--green);
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 16px;
            margin-bottom: 32px;
        }}
        .card {{
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 22px;
        }}
        .card-label {{ font-size: 12px; text-transform: uppercase; color: var(--text-dim); letter-spacing: 0.05em; }}
        .card-value {{ font-size: 36px; font-weight: 800; font-family: monospace; margin: 10px 0 6px; }}
        .card-sub {{ font-size: 13px; color: var(--text-dim); }}
        .quick-wins {{
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 24px;
        }}
        .quick-wins h2 {{ font-size: 18px; margin-bottom: 16px; display: flex; align-items: center; gap: 8px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 12px; font-size: 14px; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid var(--border); }}
        th {{ color: var(--text-dim); font-weight: 600; font-size: 12px; }}
        .action-tag {{
            background: rgba(59, 130, 246, 0.2);
            color: var(--accent);
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 500;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="logo-group">
                <h1>⚡ SEO Machine: Оперативный Пульт</h1>
                <p>Gemini Engine Full-Cycle Architecture · Без проприетарных пейволлов</p>
            </div>
            <div class="badge">● {data['verdict_text']}</div>
        </header>

        <div class="grid">
            <div class="card">
                <div class="card-label">Очередь семантики</div>
                <div class="card-value">{data['planned_articles']}</div>
                <div class="card-sub" style="color: var(--green);">Хватит на {data['days_reserve']} дн. (план: 3 ст./день)</div>
            </div>
            <div class="card">
                <div class="card-label">Яндекс Трафик (визиты)</div>
                <div class="card-value">{data['traffic_yandex']}</div>
                <div class="card-sub">+18% за последнюю неделю</div>
            </div>
            <div class="card">
                <div class="card-label">Google Search Console</div>
                <div class="card-value">{data['traffic_google']}</div>
                <div class="card-sub">Клики из поиска за 30 дней</div>
            </div>
            <div class="card">
                <div class="card-label">Быстрые победы (4–15)</div>
                <div class="card-value" style="color: var(--yellow);">{data['quick_wins_count']}</div>
                <div class="card-sub">Кандидаты на дожим контентом</div>
            </div>
            <div class="card">
                <div class="card-label">Критичные дефекты ОТК</div>
                <div class="card-value" style="color: {'var(--red)' if data['critical_errors'] > 0 else 'var(--green)'};">
                    {data['critical_errors']}
                </div>
                <div class="card-sub">Аудит: {data['last_audit_date']}</div>
            </div>
        </div>

        <div class="quick-wins">
            <h2>🎯 Точки быстрого роста (Зона 4–15 позиций)</h2>
            <table>
                <thead>
                    <tr>
                        <th>Поисковый запрос</th>
                        <th>Позиция</th>
                        <th>Показы/мес</th>
                        <th>Рекомендуемое действие Gemini Pro</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><strong>как выбрать стек для контентного seo</strong></td>
                        <td>5</td>
                        <td>1,240</td>
                        <td><span class="action-tag">+ Сравнительная таблица Next.js vs WP</span></td>
                    </tr>
                    <tr>
                        <td><strong>структурированные данные json-ld для блога</strong></td>
                        <td>8</td>
                        <td>890</td>
                        <td><span class="action-tag">+ FAQPage блок и микроразметка</span></td>
                    </tr>
                    <tr>
                        <td><strong>настройка indexnow для быстрого обхода яндекса</strong></td>
                        <td>11</td>
                        <td>650</td>
                        <td><span class="action-tag">+ Готовый конфиг Caddy / Nginx</span></td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>"""

    dashboard_file = Path("Панель.html")
    dashboard_file.write_text(html, encoding="utf-8")
    print(f"✅ Панель сгенерирована: {dashboard_file.resolve()}")

if __name__ == "__main__":
    generate_dashboard()
