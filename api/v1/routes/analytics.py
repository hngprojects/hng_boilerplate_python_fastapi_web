from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, HTTPException
from sqlalchemy.orm import Session
from api.db.database import get_db
from api.v1.services.analytics import AnalyticsService
from api.v1.schemas.analytics import SummaryResponse, ChartResponse, BarChartResponse, PieChartResponse, RealtimeUpdate
from api.utils.dependencies import get_current_user
from api.v1.models import User
import asyncio

router = APIRouter()

@router.get("/summary", response_model=SummaryResponse)
async def get_summary(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        summary_data = AnalyticsService.get_summary(db)
        return {
            "status": True,
            "status_code": 200,
            **summary_data
        }
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail={
                "status": False,
                "status_code": 404,
                "error": "ResourceNotFound",
                "message": "The summary data could not be found.",
                "details": {
                    "resource": "Summary",
                    "error": str(e)
                }
            }
        )

@router.get("/line-chart-data", response_model=ChartResponse)
async def get_line_chart_data(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        chart_data = AnalyticsService.get_line_chart_data(db)
        return {
            "status": True,
            "status_code": 200,
            **chart_data
        }
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail={
                "status": False,
                "status_code": 404,
                "error": "DataFetchError",
                "message": "There was an error fetching the line chart data.",
                "details": {
                    "chart_type": "line",
                    "error": str(e)
                }
            }
        )

@router.get("/bar-chart-data", response_model=BarChartResponse)
async def get_bar_chart_data(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        chart_data = AnalyticsService.get_bar_chart_data(db)
        return {
            "status": True,
            "status_code": 200,
            **chart_data,
            "data": chart_data["data"],
            "labels": chart_data["categories"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail={
                "status": False,
                "status_code": 404,
                "error": "DataFetchError",
                "message": "There was an error fetching the bar chart data.",
                "details": {
                    "chart_type": "bar",
                    "error": str(e)
                }
            }
        )

@router.get("/pie-chart-data", response_model=PieChartResponse)
async def get_pie_chart_data(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        chart_data = AnalyticsService.get_pie_chart_data(db)
        return {
            "status": True,
            "status_code": 200,
            **chart_data,
            "labels": chart_data["segments"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail={
                "status": False,
                "status_code": 404,
                "error": "DataFetchError",
                "message": "There was an error fetching the pie chart data.",
                "details": {
                    "chart_type": "pie",
                    "error": str(e)
                }
            }
        )

@router.websocket("/realtime")
async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):
    await websocket.accept()
    try:
        while True:
            active_now = AnalyticsService.get_active_users_count(db)
            await websocket.send_json(RealtimeUpdate(
                status=True,
                status_code=200,
                type="update",
                data={
                    "metric": "active_users",
                    "value": active_now
                }
            ).dict())
            await asyncio.sleep(5)  # Update every 5 seconds
    except WebSocketDisconnect:
        await websocket.close(code=1000)
    except Exception as e:
        await websocket.send_json(RealtimeUpdate(
            status=False,
            status_code=500,
            type="error",
            data={
                "error": "WebSocketConnectionError",
                "message": "Failed to establish a WebSocket connection for real-time updates.",
                "details": {
                    "connection": "WebSocket",
                    "error": str(e)
                }
            }
        ).dict())
        await websocket.close(code=1000)