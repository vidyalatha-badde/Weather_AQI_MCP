from fastmcp import FastMCP
from transformers import pipeline

# Initialize the MCP LLM Server
mcp = FastMCP("LLM-Inference", host="0.0.0.0", port=8002)

try:
    generator = pipeline(
        "text-generation",
        model="Qwen/Qwen2.5-3B-Instruct",
        device=0,  # Remove or set to -1 if you want CPU only
        max_new_tokens=512,
    )
except Exception as e:
    print(f"Failed to load the text generation model: {str(e)} Please download it first using the CLI command( refer README)\n")
    generator = None  # fallback, so your server doesn't crash

@mcp.tool()
async def safety_guidelines(weather_report: str, aqi_report: str) -> str:
    """
    Generate personalized outdoor safety and health guidelines
    based on the provided weather and air quality reports.

    This tool uses a language model to analyze the input data
    and provides an overall outdoor safety level.

    Args:
        weather_report (str): A detailed weather report for the location.
        aqi_report (str): The Air Quality Index (AQI) report for the same location.

    Returns:
        str: A formatted string containing the AI-generated safety advice,
        covering outdoor safety, health risks, precautions, and
        recommendations for sensitive groups.
    """
    if generator is None:
        return "The language model could not be initialized. Please check your model path and device setup."

    prompt = f"""
You are a health assistant. Given this weather and air quality:

Weather Report:
{weather_report}

AQI Report:
{aqi_report}

Provide:
1. Overall outdoor safety level. Can I go for parasailing based on the weather report?
2. Health risks.
3. Precautions.
4. Special advice for sensitive groups.
"""

    try:
        output = generator(
            prompt,
            do_sample=True,
            temperature=0.7
        )
        if not output or "generated_text" not in output[0]:
            return "Failed to generate safety guidelines. The model returned no valid output."

        result = output[0]["generated_text"]
        return result.strip()

    except Exception as e:
        return f"Model pipeline error: {str(e)}"
    except Exception as e:
        return f"Unexpected error during text generation: {str(e)}"

if __name__ == "__main__":
    mcp.run("sse")
