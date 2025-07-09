from fastmcp import FastMCP
from transformers import pipeline

# Initialize the MCP LLM Server
mcp = FastMCP("AQI-LLM", host="0.0.0.0", port=8004)

generator = pipeline(
    "text-generation",
    model="Qwen/Qwen2.5-3B-Instruct", 
    device=0,  # Use 0 if you have GPU support, otherwise remove this argument
    max_new_tokens=512,
)

@mcp.tool()
async def safety_guidelines(weather_report: str, aqi_report: str) -> str:
    """
    Generate personalized outdoor safety and health guidelines
    based on the provided weather and air quality reports.

    This tool uses a language model to analyze the input data
    and provides an overall outdoor safety level

    Args:
        weather_report (str): A detailed weather report for the location.
        aqi_report (str): The Air Quality Index (AQI) report for the same location.

    Returns:
        str: A formatted string containing the AI-generated safety advice,
        covering outdoor safety, health risks, precautions, and
        recommendations for sensitive groups.
    """
    prompt = f"""
                You are a health assistant. Given this weather and air quality:

                Weather Report:
                {weather_report}

                AQI Report:
                {aqi_report}

                Provide:
                1. Overall outdoor safety level. can i go for parasailing based on the weather report?
                2. Health risks.
                3. Precautions.
                4. Special advice for sensitive groups.
            """
    output = generator(prompt, do_sample=True, temperature=0.7)
    result = output[0]["generated_text"]
    return result
    
if __name__ == "__main__":
    mcp.run("sse")
