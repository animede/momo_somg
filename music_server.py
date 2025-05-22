
# music_server.py
from fastapi import FastAPI, Request, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import io, base64, json
from openai_chat import  AsyncOpenAI
from create_image_world import create_image
from music import music_generation, generate_song

app = FastAPI()
app.mount('/static', StaticFiles(directory='static'), name='static')
audio_out_path="/home/animede/ACE-Step/"

a_client =AsyncOpenAI(
    #base_url="http://127.0.0.1:8080/v1",
    base_url="http://39.110.248.77:64652/v1", # 27B
    #base_url="http://39.110.248.77:64650/v1", # 27B
    api_key="YOUR_OPENAI_API_KEY",  # このままでOK
    )
sdxl_url = 'http://39.110.248.77:64656'

# genre_tags.json を読み込む
with open("genre_tags.json", "r", encoding="utf-8") as f:
     genre_tags = json.load(f)

@app.get('/')
async def read_index():
    return FileResponse('templates/index.html')

@app.post('/generate_lyrics')
async def generate(request: Request, user_input: str = Form(...)):
    success, lyrics_dict, music_world, _ = await music_generation(user_input,genre_tags)
    if not success:
        return JSONResponse({ 'err': '音楽生成に失敗しました' }, status_code=500)
    print("music_world=",music_world)
    result=True
    return JSONResponse({"result":result,"lyrics_dict": lyrics_dict, "music_world":music_world})

@app.post('/generate_music')
async def generate_music(request: Request,lyrics_dict: str = Form(...), infer_step: int = Form(27), guidance_scale: float = Form(15), gomega_scale: float = Form(10), music_world: str = Form(...)):
    music_world = json.loads(music_world.replace(" ", ""))
    print("music_world=",music_world)
    lyrics_dict = json.loads(lyrics_dict.replace(" ", ""))
    print("lyrics_dict=",lyrics_dict)
    # ① 音楽生成の結果を取得
    #generate_song から bytes が返ってくる想定
    audio_bytes = generate_song(lyrics_dict,infer_step,guidance_scale,gomega_scale)
    # ③ イメージ画像を生成
    pil_image = await create_image(sdxl_url,a_client, music_world, "text2image", "t2i")
    buf = io.BytesIO()
    pil_image.save(buf, format='PNG')
    image_base64 = 'data:image/png;base64,' + __import__('base64').b64encode(buf.getvalue()).decode()
    # ④ 音声も Base64 にエンコード（Data URI スキーム）
    audio_base64 = 'data:audio/wav;base64,' + base64.b64encode(audio_bytes).decode()
    # ⑤ JSON でまとめて返却
    return JSONResponse({
        'lyrics_json': json.dumps(lyrics_dict, ensure_ascii=False, indent=2),
        'image_base64': image_base64,
        'audio_base64': audio_base64,
    })

if __name__ == '__main__':
    import uvicorn
    uvicorn.run('music_server:app', host='0.0.0.0', port=8000, reload=True)
