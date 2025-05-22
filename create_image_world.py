from openai_chat import chat_req
import requests
import json
import pickle
import requests

#---------------------  Create Image world-------------------文章の世界観を描く
async def create_image(url,a_client,text, mode, generate_mode, num_inference_steps=20, guidance_scale=8.0):
    print("text=",text)
    print("mode=",mode)
    print("generate_mode=",generate_mode)
    # textが辞書型の場合、文字列に変換
    if isinstance(text, dict):
        text = json.dumps(text, ensure_ascii=False)
    if mode=="outline":
        #text=text.split("### 物語の要約")[1].split("#")[0]
        print("++++++++++++++++++++++++++++++++############## 要約=",text)
        role="あなたは賢いAIです。userの要求や質問に正しく答えること"
        user_msg="以下の文章から想像する世界観をStableDiffusionのプロンプトに変えてください。masterpiece, best qualityは使うこと。\
            promptにはキャラクタを描いてはいけません、文章の世界観のみを描くこと。prompt_2には必要に応じて場面に登場するキャラクタを設定しても良い。 \
            キャラクタを描く場合は中央に大きくならないよいうに構図に配慮すること\
            回答はjeson形式で、キーはprompt、prompt_2、negative_prompt、negative_prompt_2の4種類だけです。解説は不要です。文章="+text
    elif mode=="text2image":
        role="あなたは賢いAIです。userの要求や質問に正しく答えること"
        user_msg="以下の文章から想像する画像をStableDiffusionのプロンプトに変えてください。masterpiece, best qualityは使うこと。\
            promptにはキャラクタを描いてはいけません、文章の世界観のみを描くこと。prompt_2には必要に応じて場面に登場するキャラクタを設定しても良い。 \
            キャラクタを描く場合は中央に大きくならないよいうに構図に配慮すること\
            回答はjeson形式で、キーはprompt、prompt_2、negative_prompt、negative_prompt_2の4種類だけです。解説は不要です。文章="+text
    response_json= await chat_req(a_client,user_msg,role)
    # JSON 文字列を辞書に変換
    print("response_json=",response_json)
    # Markdown のコードブロックのマーカーを除去
    if response_json.startswith("```"):
            response_json = "\n".join(response_json.splitlines()[1:])
            response_json = response_json.rsplit("```", 1)[0].strip()
            data = json.loads(response_json)
            # prompt と negative_prompt を取り出す
            prompt = data["prompt"]
            try:
                prompt_2= data["prompt_2"]
                negative_prompt = data["negative_prompt"]
                negative_prompt_2 = data["negative_prompt_2"]
            except:
                prompt_2=""
                negative_prompt=""
                negative_prompt_2=""
            print("Prompt:", prompt)
            print("Negative Prompt:", negative_prompt)
            print("Prompt_2:", prompt_2)
            print("Negative Prompt_2:", negative_prompt_2)
            # 画像生成
            np2=False,#negative_prompt_2は使わない
            pt2=True,#prompt_2は使う
            gen_mode="t2i"#画像生成モードはi2i
            image= await generate_image(url,pt2,np2,gen_mode,prompt,prompt_2,negative_prompt,negative_prompt_2,num_inference_steps=num_inference_steps,guidance_scale=guidance_scale)
            # 画像オブジェクトを直接返す
            return image
    else:
            print("Invalid response format")
            return {"result": "No image generated"}

async def generate_image(url,pt2,np2,gen_mode,prompt,prompt_2,negative_prompt,negative_prompt_2,num_inference_steps=20,guidance_scale=8.0):
    # 汎用画像生成のためのリクエストを作成
    #np2はnegative_prompt_2の利用・停止を示すフラグ
    #pt2はprompt_2の利用・停止を示すフラグ
    if pt2==False:
        prompt_2=""
    if np2==False:
        negative_prompt_2=""
    print("Prompt:", prompt)
    print("Negative Prompt:", negative_prompt)
    print("Prompt_2:", prompt_2)
    print("Negative Prompt_2:", negative_prompt_2)
    data= {
        "pipeline":gen_mode,#t2i, i2i
        "prompt":prompt,
        "prompt_2":prompt_2,
        "negative_prompt":negative_prompt,
        "negative_prompt_2":negative_prompt_2,
        "freeu":False,
        #"freeu_list":[0.9, 0.2,1.2,1.4],
        "num_inference_steps":num_inference_steps,
        "guidance_scale":guidance_scale,  
        "auto_seed":False,
        #"seed":50,
        "height":976,
        "width":1296, 
        #"height":776,
        #"width":1024, 
        #"height":768,
        }
    image = await request_imag(url,data)
    return image[0]

# API サーバrequest モジュール
async def request_imag(url,data,files=None):
    response = requests.post(url +"/generate/", data=data ,files=files) # POSTリクエストを送信
    print(response)
    # レスポンスを表示 
    if response.status_code == 200:
        print("get data OK")
        image_data = response.content
        image =(pickle.loads(image_data))#元の形式にpickle.loadsで復元
    else:
        image=[]
        print("リクエストが失敗しました。ステータスコード:", response.status_code)
    return  image
