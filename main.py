from util.disposable_pool import DisposablePool
from util.hsr import HSR
from util.settings import settings
from model.response import BaseResponse, BaseResponseWithUUID
from model.request import SearchRequest, BookRequest
from model.train import Train

from fastapi import FastAPI, Request, status
from fastapi.exceptions import HTTPException
from pyvirtualdisplay import Display
from uuid import UUID


app = FastAPI()
hsr_pool = DisposablePool()

# 因為 server 沒有 GUI 介面可以開啟瀏覽器
# 可以透過 pyvirtualdisplay 結合 xvfb 開啟虛擬顯示器
# 要先安裝 xvfb 才可以使用
# 在 Ubuntu 可以 `sudo apt install xvfb`
display = Display(visible=False, size=(1600, 900))
display.start()


@app.get("/")
def check_if_the_server_is_fine(request: Request) -> BaseResponse[None]:
    return BaseResponse(message=f"The server is working fine. Documentation url: {str(request.url).replace('http:', 'https:')}redoc", data=None)


@app.get("/search", description=f"提供訂票資訊，伺服器將會到高鐵網頁爬取時刻表並回傳，同時也會回傳用於訂票的 `session_id`，其有效時間有 {settings.session_dispose_sec} 秒，僅能使用一次。")
def get_hsr_time_table(search_req: SearchRequest) -> BaseResponseWithUUID[list[Train]]:
    hsr = HSR(dispose_sec=settings.session_dispose_sec)
    hsr_pool.add(hsr)
    train_list = hsr.get_time_table(search_req)
    if len(train_list) == 0:
        message = "The tickets might have been sold out or something goes wrong."
    else:
        message = "Success."
    return BaseResponseWithUUID(message=message, data=train_list, session_id=hsr.uuid)


@app.post("/book/{session_id}", description="根據 `/search` 得到的時刻表，提供欲訂購的班次 index，以及查詢的 `session_id`，伺服器將會自動完成訂票作業並回傳結果截圖的連結。")
def book_hsr_ticket(book_req: BookRequest, session_id: UUID) -> BaseResponse[str]:
    hsr: HSR = hsr_pool.get(session_id)
    if hsr == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="`session_id` is not found.")
    try:
        img_url = "https://example.com" if book_req.debug else hsr.book_ticket(
            book_req)
    except:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED,
                            detail="`session_id` has expired or time table is unavailable.")
    return BaseResponse(message="Success.", data=img_url)
