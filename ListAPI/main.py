import uuid
from fastapi import FastAPI, Body, HTTPException, status
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import date

app = FastAPI()

# Добавьте CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Счетчик для генерации кодов
contract_counter = 1

class ContractModel(BaseModel):
    id: Optional[str] = None
    code: str  # Добавлено поле для шифра документа
    name: str
    labor: int
    employeeName: str
    post: str
    issueDate: date
    finalDate: date

class Contract:
    def __init__(self, name, labor, employeeName, post, issueDate, finalDate):
        global contract_counter
        self.name = name
        self.labor = labor
        self.employeeName = employeeName
        self.post = post
        self.issueDate = issueDate
        self.finalDate = finalDate
        self.id = str(uuid.uuid4())
        # Генерация шифра документа в формате К-001
        self.code = f"К-{contract_counter:03d}"
        contract_counter += 1

# База данных
acts = [
    Contract("Подготовка договора", 8, "Иванов И.И.", "Юрист", date(2023, 1, 1), date(2023, 1, 3)),
    Contract("Проведение переговоров", 16, "Петров А.А.", "Менеджер отдела", date(2023, 1, 5), date(2023, 1, 10)),
    Contract("Анализ договорных рисков", 24, "Сидоров О.О.", "Руководитель", date(2023, 1, 12), date(2023, 1, 18))
]

def find_contract(id):
    for contract in acts:
        if contract.id == id:
            return contract
    return None

def find_contract_by_code(code):
    for contract in acts:
        if contract.code == code:
            return contract
    return None

@app.get("/")
def main():
    return FileResponse("public/index.html")

@app.get("/api/contracts", response_model=List[ContractModel])
def get_contracts():
    return acts

@app.get("/api/contracts/{code}", response_model=ContractModel)
def get_contract(code: str):
    contract = find_contract_by_code(code)
    if not contract:
        raise HTTPException(status_code=404, detail="Контракт не найден")
    return contract

@app.post("/api/contracts", response_model=ContractModel)
def create_contract(data=Body()):
    contract = Contract(data["name"], data["labor"], data["employeeName"],
                       data["post"], data["issueDate"], data["finalDate"])
    acts.append(contract)
    return contract

@app.put("/api/contracts", response_model=ContractModel)
def update_contract(data=Body()):
    contract = find_contract_by_code(data["code"])
    if not contract:
        raise HTTPException(status_code=404, detail="Контракт не найден")
    contract.name = data["name"]
    contract.labor = data["labor"]
    contract.employeeName = data["employeeName"]
    contract.post = data["post"]
    contract.issueDate = data["issueDate"]
    contract.finalDate = data["finalDate"]
    return contract

@app.delete("/api/contracts/{code}")
def delete_contract(code: str):
    contract = find_contract_by_code(code)
    if not contract:
        raise HTTPException(status_code=404, detail="Контракт не найден")
    acts.remove(contract)
    return {"message": "Контракт удален", "code": code}