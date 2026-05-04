import uvicorn
import csv
from datetime import datetime
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, HTMLResponse
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key='my_lab_secret_123')

pages = Jinja2Templates(directory='templates')

def verify_credentials(user, pwd):
    try:
        with open('users.csv', 'r', encoding='utf-8') as f:
            data = csv.reader(f)
            for row in data:
                if row and row[0] == user and row[1] == pwd:
                    return True
    except:
        print('Ошибка: файл users.csv не найден')
    return False

def add_log_entry(user, message):
    now = datetime.now().strftime('%H:%M:%S | %d.%m.%Y')
    with open('logs.csv', 'a', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([now, user, message])

@app.exception_handler(403)
async def error_403(request: Request, exc: Exception):
    return pages.TemplateResponse(
        request=request, name='403.html', context={'request': request}, status_code=403
    )

@app.exception_handler(404)
async def error_404(request: Request, exc: Exception):
    return pages.TemplateResponse(
        request=request, name='404.html', context={'request': request}, status_code=404
    )

@app.get('/', response_class=HTMLResponse)
async def main_page(request: Request):
    current_user = request.session.get('user')
    if not current_user:
        raise HTTPException(status_code=403)
    add_log_entry(current_user, 'Открыл главную страницу')
    return pages.TemplateResponse(
        request=request, name='index.html', context={'request': request, 'username': current_user}
    )

@app.get('/login', response_class=HTMLResponse)
async def login_get(request: Request):
    return pages.TemplateResponse(request=request, name='login.html', context={'request': request})

@app.post('/login')
async def login_post(request: Request, username: str = Form(...), password: str = Form(...)):
    if verify_credentials(username, password):
        request.session['user'] = username
        add_log_entry(username, 'Успешно залогинился')
        return RedirectResponse(url='/', status_code=302)
    else:
        add_log_entry(username, 'Пытался войти с неверным паролем')
        return pages.TemplateResponse(
            request=request, 
            name='login.html', 
            context={'request': request, 'error': 'Неверный логин или пароль'}
        )

@app.get('/logout')
async def sign_out(request: Request):
    user = request.session.get('user', 'Unknown')
    add_log_entry(user, 'Вышел из аккаунта')
    request.session.clear()
    return RedirectResponse(url='/login')

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='127.0.0.1',
        port=8000,
        ssl_keyfile='key.pem',
        ssl_certfile='cert.pem',
        reload=True
    )
