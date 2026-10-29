import os, re, time, logging
import requests
from ddgs import DDGS
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

log = logging.getLogger("agent")
MODEL_NAME = os.environ.get("MODEL_NAME", "openai/gpt-oss-120b")

def wiki_search(topic, n=6):
    r = requests.get(
        "https://en.wikipedia.org/w/api.php",
        params={"action": "query", "list": "search", "srsearch": topic,
                "format": "json", "srlimit": n},
        headers={"User-Agent": "mlops-lab/1.0"}, timeout=15)
    items = r.json().get("query", {}).get("search", [])
    return "\n\n".join(
        f"[{i}] {it['title']}\n{re.sub(r'<[^>]+>', '', it['snippet'])}"
        for i, it in enumerate(items, 1))

def search_web(topic, n=6):
    for backend in ["auto", "brave", "yahoo", "duckduckgo"]:
        try:
            res = DDGS().text(topic, max_results=n, backend=backend)
            if res:
                return "\n\n".join(
                    f"[{i}] {r.get('title','')}\n{r.get('body','')}"
                    for i, r in enumerate(res, 1))
        except Exception as e:
            log.warning("search backend %s failed: %s", backend, e)
    try:
        return wiki_search(topic, n)
    except Exception as e:
        log.error("wikipedia fallback failed: %s", e)
        return ""

def clean_to_three_bullets(text):
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    bullets = ["- " + l.strip().lstrip("-•* ").strip()
               for l in text.splitlines()
               if l.strip().startswith(("-", "•", "*"))]
    return "\n".join(bullets[:3])

PROMPT = ChatPromptTemplate.from_messages([
    ("system", "You are a research assistant. Using ONLY the search results, "
               "output EXACTLY three bullet points starting with '- ', one "
               "sentence each (max 30 words). No other text."),
    ("human", "Topic: {topic}\n\nSearch results:\n{results}\n\nThree-bullet brief:"),
])

def research_brief(topic):
    start = time.time()
    log.info("topic received: %s", topic)
    try:
        results = search_web(topic)
        if not results:
            return "Search returned no results. Please try again."
        llm = ChatGroq(model=MODEL_NAME, temperature=0.2, max_tokens=1000)
        chain = PROMPT | llm | StrOutputParser()
        brief = clean_to_three_bullets(chain.invoke({"topic": topic, "results": results}))
        log.info("done in %.2f s", time.time() - start)
        return brief or "The model returned no bullets. Please try again."
    except Exception as e:
        log.exception("error while processing '%s'", topic)
        return f"Error: {e}"