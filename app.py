import os
from flask import Flask, request, redirect, render_template_string, abort
import string
import random
import re

app = Flask(__name__)
NOTES_DIR = 'notes'
os.makedirs(NOTES_DIR, exist_ok=True)

def generate_id(length=5):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

NOTE_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Online Notepad</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
    <style>
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            margin: 0;
            font-family: 'Roboto', sans-serif;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .container {
            background: rgba(255, 255, 255, 0.85);
            border-radius: 24px;
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.25);
            padding: 3rem 2.5rem 2.5rem 2.5rem;
            max-width: 700px;
            width: 100%;
            margin: 2rem;
            display: flex;
            flex-direction: column;
            align-items: center;
            backdrop-filter: blur(8px);
            border: 1.5px solid rgba(118, 75, 162, 0.12);
            transition: box-shadow 0.3s;
        }
        .container:hover {
            box-shadow: 0 12px 40px 0 rgba(31, 38, 135, 0.32);
        }
        .header-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            width: 100%;
            margin-bottom: 2rem;
        }
        h1 {
            color: #4f3ca7;
            font-weight: 700;
            letter-spacing: 1px;
            font-size: 2.2rem;
            text-shadow: 0 2px 8px rgba(118, 75, 162, 0.08);
            margin: 0;
        }
        .save-btn {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            color: #fff;
            border: none;
            border-radius: 10px;
            padding: 0.7rem 1.5rem;
            font-size: 1.08rem;
            font-weight: 500;
            cursor: pointer;
            transition: background 0.2s, box-shadow 0.2s, transform 0.1s;
            box-shadow: 0 2px 8px rgba(118, 75, 162, 0.10);
            margin-left: 1.2rem;
        }
        .save-btn:hover {
            background: linear-gradient(90deg, #764ba2 0%, #667eea 100%);
            transform: translateY(-2px) scale(1.04);
            box-shadow: 0 4px 16px rgba(118, 75, 162, 0.16);
        }
        form {
            width: 100%;
            display: flex;
            flex-direction: column;
            align-items: stretch;
        }
        .textarea-wrapper {
            position: relative;
            width: 100%;
        }
        textarea {
            width: 100%;
            min-height: 320px;
            max-height: 60vh;
            border-radius: 16px;
            border: 1.5px solid #bdbdbd;
            padding: 0.7rem 1.1rem 0.7rem 1.1rem;
            font-size: 1.18rem;
            font-family: 'Roboto', monospace;
            resize: vertical;
            margin-bottom: 1.2rem;
            background: rgba(247, 247, 250, 0.95);
            box-shadow: 0 2px 8px rgba(118, 75, 162, 0.04);
            transition: border 0.2s, box-shadow 0.2s;
            box-sizing: border-box;
        }
        textarea:focus {
            border: 1.5px solid #764ba2;
            outline: none;
            box-shadow: 0 4px 16px rgba(118, 75, 162, 0.10);
        }
        .copy-icon {
            position: absolute;
            top: 12px;
            right: 18px;
            width: 28px;
            height: 28px;
            background: none;
            border: none;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            opacity: 0.7;
            transition: opacity 0.2s;
            z-index: 2;
        }
        .copy-icon:hover {
            opacity: 1;
        }
        .copy-tooltip {
            position: absolute;
            top: -30px;
            right: 0;
            background: #4f3ca7;
            color: #fff;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 0.95rem;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.2s;
            z-index: 3;
        }
        .copy-icon.copied + .copy-tooltip {
            opacity: 1;
        }
        .share-link {
            margin-top: 2rem;
            background: rgba(247, 247, 250, 0.95);
            padding: 1rem 1.2rem;
            border-radius: 10px;
            font-size: 1.05rem;
            color: #4f3ca7;
            word-break: break-all;
            box-shadow: 0 1px 4px rgba(118, 75, 162, 0.07);
        }
        a {
            color: #764ba2;
            text-decoration: underline;
            transition: color 0.2s;
        }
        a:hover {
            color: #4f3ca7;
        }
        @media (max-width: 800px) {
            .container {
                padding: 1.5rem 0.5rem 1rem 0.5rem;
                max-width: 98vw;
            }
            textarea {
                font-size: 1rem;
                min-height: 180px;
            }
            .header-row {
                flex-direction: column;
                align-items: flex-start;
                gap: 0.7rem;
            }
            .save-btn {
                margin-left: 0;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <form method="post">
            <div class="header-row">
                <h1>📝 Online Notepad</h1>
                <button type="submit" class="save-btn">Save</button>
            </div>
            <div class="textarea-wrapper">
                <textarea id="note-textarea" name="content" rows="18" cols="80">{{ content.strip() if content else '' }}</textarea>
                <button type="button" class="copy-icon" onclick="copyText(this)" title="Copy to clipboard" tabindex="-1">
                    <svg viewBox="0 0 24 24" fill="none" width="22" height="22" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
                </button>
                <span class="copy-tooltip" id="copy-tooltip">Copied!</span>
            </div>
        </form>
        {% if note_id %}
        <div class="share-link">
            Shareable link: <a href="/{{ note_id }}">{{ request.url_root }}{{ note_id }}</a>
        </div>
        {% endif %}
    </div>
    <script>
        function copyText(btn) {
            const textarea = document.getElementById('note-textarea');
            textarea.select();
            textarea.setSelectionRange(0, 99999); // For mobile devices
            try {
                document.execCommand('copy');
            } catch (err) {
                navigator.clipboard.writeText(textarea.value);
            }
            // Show tooltip
            const tooltip = document.getElementById('copy-tooltip');
            btn.classList.add('copied');
            tooltip.style.opacity = 1;
            setTimeout(() => {
                btn.classList.remove('copied');
                tooltip.style.opacity = 0;
            }, 1200);
        }
    </script>
</body>
</html>
'''

def save_note(note_id, content):
    with open(os.path.join(NOTES_DIR, f"{note_id}.txt"), 'w', encoding='utf-8') as f:
        f.write(content)

def load_note(note_id):
    path = os.path.join(NOTES_DIR, f"{note_id}.txt")
    if not os.path.exists(path):
        return None
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        content = request.form.get('content', '')
        content = re.sub(r'^[\s\n]+|[\s\n]+$', '', content)
        note_id = generate_id()
        save_note(note_id, content)
        return redirect(f'/{note_id}')
    return render_template_string(NOTE_TEMPLATE, content='', note_id=None, request=request)

@app.route('/<note_id>', methods=['GET', 'POST'])
def note(note_id):
    if request.method == 'POST':
        content = request.form.get('content', '')
        content = re.sub(r'^[\s\n]+|[\s\n]+$', '', content)
        save_note(note_id, content)
    content = load_note(note_id)
    if content is None:
        abort(404)
    return render_template_string(NOTE_TEMPLATE, content=content.strip() if content else '', note_id=note_id, request=request)

if __name__ == '__main__':
    app.run(debug=True) 