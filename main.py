from fastapi import FastAPI
from routes.route import router
from routes.userroute import userrouter
from routes.productroute import productrouter
from routes.wishlistroute import wishlistrouter
from routes.cartroute import cartrouter
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(userrouter)
app.include_router(productrouter)
app.include_router(wishlistrouter)
app.include_router(cartrouter)


# handler = Mangum(app)