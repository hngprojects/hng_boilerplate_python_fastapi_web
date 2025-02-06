from fastapi import APIRouter, Response
import subprocess


test_rout = APIRouter(prefix='/all', tags=['Tests'])

@test_rout.get("/run-tests")
async def run_tests():
    # Run pytest and capture the output
    result = subprocess.run(['pytest', '--maxfail=1', '--disable-warnings', '--tb=short'], 
                            capture_output=True, text=True)
    # Return the output as the response
    return Response(content=result.stdout, media_type="text/plain")

