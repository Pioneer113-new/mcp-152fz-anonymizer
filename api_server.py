import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends, Security, status
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig
from analyzer_setup import create_analyzer_engine
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api_server")

# Load environment variables
load_dotenv()
API_KEY = os.getenv("API_KEY")

# Define security scheme
api_key_header = APIKeyHeader(name="X-API-Token", auto_error=False)


async def get_api_key(api_key_header: str = Security(api_key_header)):
    if not API_KEY:
        # If API_KEY is not set on server, log warning or fail.
        # For safety, let's fail if auth is required but not configured.
        logger.error("API_KEY environment variable is not set!")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server configuration error: API_KEY missing",
        )
    if api_key_header == API_KEY:
        return api_key_header
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing API Key",
    )


app = FastAPI(
    title="152-FZ Anonymizer API",
    description="REST API for anonymizing Russian personal data suitable for n8n/Zapier integrations.",
    version="1.0.0",
)

# Initialize engines at startup
logger.info("Initializing Presidio engines...")
analyzer = create_analyzer_engine()
anonymizer = AnonymizerEngine()
logger.info("Engines ready.")


class AnonymizeRequest(BaseModel):
    text: str


class AnonymizeResponse(BaseModel):
    anonymized_text: str


class AuditResponse(BaseModel):
    entities: list


@app.post("/anonymize", response_model=AnonymizeResponse)
async def anonymize(request: AnonymizeRequest, token: str = Depends(get_api_key)):
    """
    Anonymize input text replacing PII with placeholders.
    """
    try:
        results = analyzer.analyze(text=request.text, language="ru")

        # Reuse the same operators as in main.py
        operators = {
            # --- Standard PII ---
            "RU_PASSPORT": OperatorConfig("replace", {"new_value": "<PASSPORT_RF>"}),
            "RU_SNILS": OperatorConfig("replace", {"new_value": "<SNILS>"}),
            "RU_INN": OperatorConfig("replace", {"new_value": "<INN>"}),
            "PERSON": OperatorConfig("replace", {"new_value": "<PERSON>"}),
            "PHONE_NUMBER": OperatorConfig("replace", {"new_value": "<PHONE>"}),
            "EMAIL_ADDRESS": OperatorConfig("replace", {"new_value": "<EMAIL>"}),
            "ORGANIZATION": OperatorConfig("replace", {"new_value": "<ORG>"}),
            "LOCATION": OperatorConfig("replace", {"new_value": "<LOC>"}),
            "RU_DRIVER_LICENSE": OperatorConfig(
                "replace", {"new_value": "<DRIVER_LICENSE>"}
            ),
            "RU_OMS": OperatorConfig("replace", {"new_value": "<OMS>"}),
            "RU_VEHICLE_PLATE": OperatorConfig("replace", {"new_value": "<CAR_PLATE>"}),
            "TG_CHAT_ID": OperatorConfig("replace", {"new_value": "<TG_CHAT_ID>"}),
            # --- Extended PII ---
            "IP_ADDRESS": OperatorConfig("replace", {"new_value": "<IP>"}),
            "IBAN_CODE": OperatorConfig("replace", {"new_value": "<BANK_ACCOUNT>"}),
            "CRYPTO": OperatorConfig("replace", {"new_value": "<WALLET>"}),
            "CREDIT_CARD": OperatorConfig("replace", {"new_value": "<BANK_CARD>"}),
            "CVV": OperatorConfig("replace", {"new_value": "<CVV>"}),
            "MAC_ADDRESS": OperatorConfig("replace", {"new_value": "<MAC>"}),
            "EME_IMEI": OperatorConfig("replace", {"new_value": "<IMEI>"}),
            "GPS_COORDS": OperatorConfig("replace", {"new_value": "<GEO>"}),
            "DATE_TIME": OperatorConfig("replace", {"new_value": "<DATE>"}),
            "RU_INT_PASSPORT": OperatorConfig(
                "replace", {"new_value": "<PASSPORT_INT>"}
            ),
            # --- Spacy Mappings ---
            "NORP": OperatorConfig("replace", {"new_value": "<GROUP>"}),
            "FAC": OperatorConfig("replace", {"new_value": "<LOC>"}),
            "GPE": OperatorConfig("replace", {"new_value": "<LOC>"}),
            "DEFAULT": OperatorConfig("replace", {"new_value": "<ANONYMIZED>"}),
        }

        anonymized_result = anonymizer.anonymize(
            text=request.text, analyzer_results=results, operators=operators
        )

        return AnonymizeResponse(anonymized_text=anonymized_result.text)

    except Exception as e:
        logger.error(f"Error processing request: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/audit", response_model=AuditResponse)
async def audit(request: AnonymizeRequest, token: str = Depends(get_api_key)):
    """
    Return detected entities without modifying text.
    Requires X-API-Token header.
    """
    results = analyzer.analyze(text=request.text, language="ru")
    report = []
    for res in results:
        report.append(
            {
                "entity_type": res.entity_type,
                "start": res.start,
                "end": res.end,
                "score": res.score,
            }
        )
    return AuditResponse(entities=report)


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
