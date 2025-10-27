"""
A2A Agent Development Kit - Auto Server Generator
에이전트를 FastAPI 서버로 자동 변환
"""
from fastapi import FastAPI, HTTPException
from typing import Dict
import asyncio
from datetime import datetime

from ..a2a_protocol import (
    AgentCard, CreateTaskRequest, CreateTaskResponse,
    GetTaskStatusResponse, Task, TaskInput, TaskOutput
)
from .agent import A2AAgent


class A2AServer:
    """
    A2A Agent를 FastAPI 서버로 자동 변환
    
    Usage:
        agent = MyAgent()
        server = A2AServer(agent, port=8001)
        server.run()
    """
    
    def __init__(self, agent: A2AAgent, port: int = 8000, host: str = "0.0.0.0"):
        self.agent = agent
        self.port = port
        self.host = host
        self.app = FastAPI(
            title=agent.name,
            description=agent.description,
            version=agent.version
        )
        
        # Task 저장소
        self.tasks_db: Dict[str, Task] = {}
        
        # 라우트 자동 등록
        self._register_routes()
    
    def _register_routes(self):
        """A2A 표준 엔드포인트 자동 등록"""
        
        @self.app.get("/.well-known/agent.json")
        async def get_agent_card():
            """Agent Card 반환"""
            card_dict = self.agent.get_agent_card()
            # URL 추가
            card_dict["url"] = f"http://localhost:{self.port}"
            return card_dict
        
        @self.app.post("/tasks")
        async def create_task(request: CreateTaskRequest) -> CreateTaskResponse:
            """Task 생성"""
            task = Task(
                status="submitted",
                input=request.input,
                metadata=request.metadata or {}
            )
            self.tasks_db[task.id] = task
            
            # 비동기로 작업 처리
            asyncio.create_task(self._process_task(task.id))
            
            return CreateTaskResponse(taskId=task.id, status=task.status)
        
        @self.app.get("/tasks/{task_id}")
        async def get_task_status(task_id: str) -> GetTaskStatusResponse:
            """Task 상태 조회"""
            if task_id not in self.tasks_db:
                raise HTTPException(status_code=404, detail="Task not found")
            
            return GetTaskStatusResponse(task=self.tasks_db[task_id])
        
        @self.app.get("/health")
        async def health_check():
            """서버 상태 확인"""
            return {
                "status": "ok",
                "agent": self.agent.agent_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        @self.app.get("/")
        async def root():
            """루트 엔드포인트"""
            return {
                "name": self.agent.name,
                "version": self.agent.version,
                "protocol": "A2A v1.0",
                "agent_card": "/.well-known/agent.json",
                "skills": [s.name for s in self.agent.get_skills()]
            }
    
    async def _process_task(self, task_id: str):
        """Task 처리"""
        if task_id not in self.tasks_db:
            return
        
        task = self.tasks_db[task_id]
        
        try:
            task.status = "working"
            task.updatedAt = datetime.utcnow()
            
            # 입력 데이터 추출
            input_data = task.input.data or {}
            
            # 스킬 이름 결정 (metadata 또는 첫 번째 스킬 사용)
            skill_name = task.metadata.get("skill")
            if not skill_name:
                skills = self.agent.get_skills()
                if skills:
                    skill_name = skills[0].name
            
            if not skill_name:
                raise ValueError("No skill specified and no default skill available")
            
            # 스킬 실행
            result = self.agent.execute_skill(skill_name, **input_data)
            
            # 결과 저장
            task.output = TaskOutput(text=str(result))
            task.status = "completed"
            task.updatedAt = datetime.utcnow()
            
        except Exception as e:
            task.status = "failed"
            task.metadata["error"] = str(e)
            task.updatedAt = datetime.utcnow()
    
    def run(self, **uvicorn_kwargs):
        """서버 실행"""
        import uvicorn
        import sys
        
        if sys.platform == 'win32':
            sys.stdout.reconfigure(encoding='utf-8')
        
        print(f"🚀 Starting {self.agent.name} on http://{self.host}:{self.port}")
        print(f"📋 Agent Card: http://localhost:{self.port}/.well-known/agent.json")
        print(f"🎯 Skills: {', '.join([s.name for s in self.agent.get_skills()])}")
        print()
        
        uvicorn.run(
            self.app,
            host=self.host,
            port=self.port,
            log_level=uvicorn_kwargs.get("log_level", "info"),
            **{k: v for k, v in uvicorn_kwargs.items() if k != "log_level"}
        )

