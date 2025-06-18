import aiohttp
import asyncio
import logging
import json
import base64
from typing import List, Optional, Dict, Union

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.types import Tool, TextContent
from yarl import URL

# ✅ サーバー名
server = Server("e-gov-laws-mcp")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "https://elaws.e-gov.go.jp/api/2"

# ✅ APIごとの許可クエリパラメータ（https://laws.e-gov.go.jp/api/2/redoc より）
ALLOWED_PARAMS = {
    "list_laws": ["law_num", "law_title", "law_title_kana", "asof", "promulgation_date_from", "promulgation_date_to", "order"],
    "search_laws": ["law_num", "law_title", "law_title_kana", "asof", "promulgation_date_from", "promulgation_date_to", "order"]
}

def resolve_law_identifier(args: dict, allow_revision_id: bool = True) -> Optional[str]:
    if allow_revision_id and "law_revision_id" in args:
        return args["law_revision_id"]
    if "law_id" in args:
        return args["law_id"]
    if "law_num" in args:
        return args["law_num"]
    return None

@server.list_tools()
async def list_tools() -> List[Tool]:
    return [
        Tool(
            name="list_laws",
            description="指定条件に該当する法令データの一覧を取得します。最大件数は limit（最大500）で指定可能。",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "default": 100},
                    "queryParameters": {
                        "type": "object",
                        "properties": {
                            "law_num": {
                                "type": "string"},
                                "description": "法令番号（部分一致）。例： 昭和二十二年政令第十六号"
                            },
                            "law_num_era": {
                                "type": "string",
                                "enum": ["Meiji", "Taisho", "Showa", "Heisei", "Reiwa"],
                                "description": "法令番号の元号（Meiji: 明治, Taisho: 大正, Showa: 昭和, Heisei: 平成, Reiwa: 令和）"
                            },
                            "law_title": {
                                "type": "string",
                                "description": "法令名又は法令略称（部分一致）"
                            },
                            "law_title_kana": {
                                "type": "string",
                                "description": "法令名読み（部分一致）"
                            },
                            "asof": {
                                "type": "string",
                                "format": "date",
                                "description": "法令の時点。例： 2023-07-01"
                            },
                            "promulgation_date_from": {
                                "type": "string",
                                "format": "date",
                                "description": "公布日（指定値を含む、それ以後）。例： 2023-07-01"
                            },
                            "promulgation_date_to": {
                                "type": "string",
                                "format": "date",
                                "description": "公布日（指定値を含む、それ以前）。例： 2023-07-01"
                            }
                        },
                        "additionalProperties": False
                    }
                }
            }
        ),
        Tool(
            name="search_laws",
            description="キーワードで法令を検索します。keyword: 検索文字列（例：建築基準法）",
            inputSchema={
                "type": "object",
                "properties": {
                    "keyword": {"type": "string"},
                    "limit": {"type": "integer", "default": 10},
                    "queryParameters": {
                        "type": "object",
                        "properties": {
                            "law_num": {
                                "type": "string"},
                                "description": "法令番号（部分一致）。例： 昭和二十二年政令第十六号"
                            },
                            "law_num_era": {
                                "type": "string",
                                "enum": ["Meiji", "Taisho", "Showa", "Heisei", "Reiwa"],
                                "description": "法令番号の元号（Meiji: 明治, Taisho: 大正, Showa: 昭和, Heisei: 平成, Reiwa: 令和）"
                            },
                            "law_title": {
                                "type": "string",
                                "description": "法令名又は法令略称（部分一致）"
                            },
                            "law_title_kana": {
                                "type": "string",
                                "description": "法令名読み（部分一致）"
                            },
                            "asof": {
                                "type": "string",
                                "format": "date",
                                "description": "法令の時点。例： 2023-07-01"
                            },
                            "promulgation_date_from": {
                                "type": "string",
                                "format": "date",
                                "description": "公布日（指定値を含む、それ以後）。例： 2023-07-01"
                            },
                            "promulgation_date_to": {
                                "type": "string",
                                "format": "date",
                                "description": "公布日（指定値を含む、それ以前）。例： 2023-07-01"
                            }
                        },
                        "additionalProperties": False
                    }
                },
                "required": ["keyword"]
            }
        ),
        Tool(
            name="get_law",
            description="法令本文を取得します。law_id, law_num, law_revision_id のいずれかを指定してください。",
            inputSchema={
                "type": "object",
                "properties": {
                    "law_id": {
                        "type": "string"},
                        "description": "法令ID。例： 322CO0000000016"
                    },
                    "law_num": {
                        "type": "string"},
                        "description": "法令番号。例： 昭和二十二年政令第十六号"
                    },
                    "law_revision_id": {"type": "string"}
                }
            }
        ),
        Tool(
            name="get_law_versions",
            description="法令の履歴一覧を取得します。law_id または law_num を指定してください。",
            inputSchema={
                "type": "object",
                "properties": {
                    "law_id": {
                        "type": "string"},
                        "description": "法令ID。例： 322CO0000000016"
                    },
                    "law_num": {
                        "type": "string"},
                        "description": "法令番号。例： 昭和二十二年政令第十六号"
                    }
                }
            }
        ),
        Tool(
            name="get_law_file",
            description="法令本文ファイルを取得します（Base64）。law_id, law_num, law_revision_id のいずれかを指定してください。",
            inputSchema={
                "type": "object",
                "properties": {
                    "law_id": {"type": "string"},
                    "law_num": {"type": "string"},
                    "law_revision_id": {"type": "string"}
                }
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> List[TextContent]:
    try:
        if name == "list_laws":
            result = await list_laws(**arguments)
        elif name == "search_laws":
            result = await search_laws(**arguments)
        elif name == "get_law":
            result = await get_law(**arguments)
        elif name == "get_law_versions":
            result = await get_law_versions(**arguments)
        elif name == "get_law_file":
            result = await get_law_file(**arguments)
        else:
            result = {"error": f"Unknown tool name: {name}"}
    except Exception as e:
        result = {"error": str(e)}
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]

def clean_query(name: str, query: Optional[Dict[str, Union[str, int]]]) -> Dict[str, Union[str, int]]:
    allow = ALLOWED_PARAMS.get(name, [])
    return {k: v for k, v in (query or {}).items() if k in allow and v is not None}

async def list_laws(limit: int = 100, queryParameters: Optional[Dict[str, Union[str, int]]] = None):
    url = f"{BASE_URL}/laws"
    params = {"limit": limit}
    params.update(clean_query("list_laws", queryParameters))
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            return await resp.json()

async def search_laws(keyword: str, limit: int = 10, queryParameters: Optional[Dict[str, Union[str, int]]] = None):
    url = f"{BASE_URL}/keyword"
    params = {"keyword": keyword, "limit": limit}
    params.update(clean_query("search_laws", queryParameters))
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            return await resp.json()

async def get_law(**kwargs):
    law_key = resolve_law_identifier(kwargs)
    if not law_key:
        return {"error": "law_id, law_num, または law_revision_id のいずれかを指定してください。"}
    url = f"{BASE_URL}/law_data/{law_key}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            return await resp.json()

async def get_law_versions(**kwargs):
    law_key = resolve_law_identifier(kwargs, allow_revision_id=False)
    if not law_key:
        return {"error": "law_id または law_num を指定してください。"}
    url = f"{BASE_URL}/law_versions/{law_key}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            return await resp.json()

async def get_law_file(**kwargs):
    law_key = resolve_law_identifier(kwargs)
    if not law_key:
        return {"error": "law_id, law_num, または law_revision_id のいずれかを指定してください。"}
    url = f"{BASE_URL}/law_file/json/{law_key}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            raw = await resp.read()
            encoded = base64.b64encode(raw).decode("utf-8")
            return {
                "filename": f"{law_key}.json",
                "content_type": resp.headers.get("Content-Type", "application/json"),
                "data_base64": encoded
            }

async def main():
    from mcp.server.stdio import stdio_server
    async with stdio_server() as (r, w):
        await server.run(
            r, w,
            InitializationOptions(
                server_name="e-gov-laws-mcp",
                server_version="1.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())
