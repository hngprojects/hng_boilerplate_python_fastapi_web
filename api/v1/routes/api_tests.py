import io
import sys
from fastapi import Depends, status, APIRouter, Response, Request
from fastapi.responses import JSONResponse
from api.v1.services.api_tests import PythonAPIs
from unittest import TestLoader, TextTestRunner, TestCase

test_router = APIRouter(prefix="/hng-test", tags=["Tests"])

@test_router.get("")
async def run_tests():
    loader = TestLoader()
    suite = loader.loadTestsFromTestCase(PythonAPIs)
    stream = io.StringIO()
    runner = TextTestRunner(stream=stream, verbosity=2)
    result = runner.run(suite)
    stream.seek(0)
    results = stream.read()
    response = {
        "total_tests": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "skipped": len(result.skipped),
        "test_results": results,
    }
    return JSONResponse(content=response)
