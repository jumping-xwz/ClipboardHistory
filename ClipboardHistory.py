#!/usr/bin/env python3

import json
import sys
import uuid
import base64
from pathlib import Path
from datetime import datetime

MAX_DISPLAY = 100
MAX_NORMAL_ITEMS = 1000

DB_FILE = (
        Path.home()
        / "Documents"
        / "ClipboardHistory.git"
        / "history.json"
)


def init_db():
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)

    if not DB_FILE.exists():
        DB_FILE.write_text(
            json.dumps(
                {"items": []},
                ensure_ascii=False,
                indent=2
            ),
            encoding="utf-8"
        )


def load_db():
    init_db()

    try:
        return json.loads(
            DB_FILE.read_text(
                encoding="utf-8"
            )
        )
    except Exception:
        return {"items": []}


def save_db(data):
    DB_FILE.write_text(
        json.dumps(
            data,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )


def now_str():
    return datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )


def now_ts():
    return int(
        datetime.now().timestamp()
    )


def short_preview(text, length=100):
    text = text.replace("\r", "")
    text = text.replace("\n", " ↩ ")

    text = " ".join(text.split())

    if len(text) > length:
        return text[:length] + "..."

    return text


# ==================================================
# add
# ==================================================

def add(content):
    content = content.strip()

    if not content:
        print("EMPTY")
        return

    db = load_db()

    items = db["items"]

    old_favorite = False

    for item in items:
        if item["content"] == content:
            old_favorite = item.get(
                "favorite",
                False
            )
            break

    items = [
        x
        for x in items
        if x["content"] != content
    ]

    items.insert(
        0,
        {
            "id": str(uuid.uuid4())[:8],
            "timestamp": now_str(),
            "created_at": now_ts(),
            "favorite": old_favorite,
            "content": content
        }
    )

    favorites = [
        x
        for x in items
        if x["favorite"]
    ]

    normals = [
        x
        for x in items
        if not x["favorite"]
    ]

    normals = normals[:MAX_NORMAL_ITEMS]

    db["items"] = (
            favorites + normals
    )

    save_db(db)

    print("OK")


# ==================================================
# add-file
# ==================================================

def add_file(filepath):
    path = Path(filepath)

    if not path.exists():
        print("FILE_NOT_FOUND")
        return

    add(
        path.read_text(
            encoding="utf-8"
        )
    )


# ==================================================
# add-base64
# ==================================================

def add_base64(encoded):
    try:

        encoded = "".join(
            encoded.splitlines()
        )

        content = (
            base64
            .b64decode(encoded)
            .decode("utf-8")
        )

        add(content)

    except Exception as e:

        print(
            f"DECODE_ERROR: {e}"
        )


# ==================================================
# add-base64-file
# ==================================================

def add_base64_file(filepath):
    path = Path(filepath)

    if not path.exists():
        print("FILE_NOT_FOUND")
        return

    encoded = path.read_text(
        encoding="utf-8"
    )

    add_base64(encoded)


# ==================================================
# list
# ==================================================

def list_items():
    db = load_db()

    for item in db["items"]:
        star = (
            "★"
            if item["favorite"]
            else " "
        )

        print(
            f"{item['id']} | "
            f"{star} | "
            f"{item['timestamp']} | "
            f"{short_preview(item['content'])}"
        )


# ==================================================
# list-json
# ==================================================

def list_json():
    db = load_db()

    result = []

    for item in db["items"]:
        result.append(
            {
                "id": item["id"],
                "favorite": item["favorite"],
                "timestamp": item["timestamp"],
                "preview": short_preview(
                    item["content"]
                )
            }
        )

    print(
        json.dumps(
            result,
            ensure_ascii=False
        )
    )


# ==================================================
# menu
# ==================================================

def menu():
    db = load_db()

    result = []

    for index, item in enumerate(
            db["items"][:MAX_DISPLAY],
            start=1
    ):

        preview = item["content"]

        preview = preview.replace("\r", "")
        preview = preview.replace("\n", " ")
        preview = " ".join(preview.split())

        if len(preview) > 30:
            preview = preview[:30] + "..."

        prefix = (
            "📌 "
            if item["favorite"]
            else ""
        )

        result.append(f"{prefix}[{index}] {preview}")
    print("\n".join(result))


# ==================================================
# menu-json
# ==================================================

def menu_json():
    db = load_db()

    result = []

    for item in db["items"][:MAX_DISPLAY]:

        preview = item["content"]

        preview = preview.replace("\n", " ")
        preview = " ".join(preview.split())

        if len(preview) > 30:
            preview = preview[:30] + "..."

        result.append(preview)

    print(
        json.dumps(
            result,
            ensure_ascii=False
        )
    )


# ==================================================
# menu-with-id
# ==================================================

def menu_with_id():
    db = load_db()

    result = []

    for index, item in enumerate(
            db["items"][:MAX_DISPLAY],
            start=1
    ):

        preview = item["content"]

        preview = preview.replace("\r", "")
        preview = preview.replace("\n", " ")
        preview = " ".join(preview.split())

        if len(preview) > 30:
            preview = preview[:30] + "..."

        prefix = (
            "📌 "
            if item["favorite"]
            else ""
        )

        result.append(f"{prefix}[{index}] {preview}")
    print("\n".join(result))


# ==================================================
# get
# ==================================================

def get_item(item_id):
    db = load_db()

    for item in db["items"]:

        if item["id"] == item_id:
            print(
                item["content"],
                end=""
            )

            return

    print("NOT_FOUND")


# ==================================================
# favorite
# ==================================================

def toggle_favorite(item_id):
    db = load_db()

    found = False
    favorite_status = False

    for item in db["items"]:

        if item["id"] == item_id:
            item["favorite"] = (
                not item["favorite"]
            )

            favorite_status = item[
                "favorite"
            ]

            found = True

            break

    if not found:
        print("NOT_FOUND")

        return

    favorites = [
        x
        for x in db["items"]
        if x["favorite"]
    ]

    normals = [
        x
        for x in db["items"]
        if not x["favorite"]
    ]

    db["items"] = (
            favorites + normals
    )

    save_db(db)

    if favorite_status:
        print("FAVORITED")
    else:
        print("UNFAVORITED")


# ==================================================
# favorites-menu
# ==================================================

def favorites_menu():
    db = load_db()

    result = []

    favorites = [
                    item
                    for item in db["items"]
                    if item["favorite"]
                ][:MAX_DISPLAY]

    for index, item in enumerate(
            favorites,
            start=1
    ):

        preview = item["content"]

        preview = preview.replace("\r", "")
        preview = preview.replace("\n", " ")
        preview = " ".join(preview.split())

        if len(preview) > 30:
            preview = preview[:30] + "..."

        result.append(
            f"📌 [{index}] {preview}"
        )

    print("\n".join(result))


# ==================================================
# favorites-id
# ==================================================

def favorites_id(index):
    db = load_db()

    try:
        index = int(index)
    except ValueError:
        print("NOT_FOUND")
        return

    favorites = [
                    item
                    for item in db["items"]
                    if item["favorite"]
                ][:MAX_DISPLAY]

    if index < 1 or index > len(favorites):
        print("NOT_FOUND")
        return

    print(
        favorites[index - 1]["id"]
    )


# ==================================================
# delete
# ==================================================

def delete_item(item_id):
    db = load_db()

    before = len(db["items"])

    db["items"] = [
        x
        for x in db["items"]
        if x["id"] != item_id
    ]

    deleted = before - len(db["items"])

    if deleted == 0:
        print("NOT_FOUND")
        return

    save_db(db)

    print("DELETED")


# ==================================================
# search
# ==================================================

def search(keyword):
    db = load_db()

    keyword = keyword.lower()

    for item in db["items"]:

        if keyword in (
                item["content"]
                        .lower()
        ):
            star = (
                "★"
                if item["favorite"]
                else " "
            )

            print(
                f"{item['id']} | "
                f"{star} | "
                f"{item['timestamp']} | "
                f"{short_preview(item['content'])}"
            )


# ==================================================
# search-json
# ==================================================

def search_json(keyword):
    db = load_db()

    keyword = keyword.lower()

    result = []

    for item in db["items"]:

        if keyword in (
                item["content"]
                        .lower()
        ):
            result.append(
                {
                    "id": item["id"],
                    "favorite": item["favorite"],
                    "timestamp": item["timestamp"],
                    "preview": short_preview(
                        item["content"]
                    )
                }
            )

    print(
        json.dumps(
            result,
            ensure_ascii=False
        )
    )


# ==================================================
# search-items
# ==================================================

def search_items(keyword):
    db = load_db()

    keyword = keyword.lower()

    return [
               item
               for item in db["items"]
               if keyword in item["content"].lower()
           ][:MAX_DISPLAY]


# ==================================================
# search-menu
# ==================================================

def search_menu(keyword):
    items = search_items(keyword)

    if not items:
        print("NOT_FOUND")

        return

    result = []

    for index, item in enumerate(
            items,
            start=1
    ):

        preview = item["content"]

        preview = preview.replace("\r", "")
        preview = preview.replace("\n", " ")

        preview = " ".join(
            preview.split()
        )

        if len(preview) > 30:
            preview = (
                    preview[:30]
                    + "..."
            )

        result.append(
            f"[{index}] {preview}"
        )

    print(
        "\n".join(result)
    )


# ==================================================
# search-id
# ==================================================

def search_id(keyword, index):
    items = search_items(keyword)

    if not items:
        print("NOT_FOUND")

        return

    try:

        index = int(index)

    except ValueError:

        print("NOT_FOUND")

        return

    if (
            index < 1
            or
            index > len(items)
    ):
        print("NOT_FOUND")

        return

    print(
        items[index - 1]["id"]
    )


# ==================================================
# menu-id
# ==================================================

def menu_id(index):
    db = load_db()

    try:
        index = int(index)
    except ValueError:
        print("NOT_FOUND")
        return

    items = db["items"][:MAX_DISPLAY]

    if index < 1 or index > len(items):
        print("NOT_FOUND")
        return

    print(
        items[index - 1]["id"]
    )


# ==================================================
# stats
# ==================================================

def stats():
    db = load_db()

    total = len(db["items"])

    favorites = sum(
        1
        for x in db["items"]
        if x["favorite"]
    )

    normals = total - favorites

    if total > 0:

        max_length = max(
            len(x["content"])
            for x in db["items"]
        )

        avg_length = int(
            sum(
                len(x["content"])
                for x in db["items"]
            ) / total
        )

    else:

        max_length = 0
        avg_length = 0

    result = {
        "total": total,
        "favorites": favorites,
        "normals": normals,
        "avg_length": avg_length,
        "max_length": max_length
    }

    print(
        json.dumps(
            result,
            ensure_ascii=False
        )
    )


# ==================================================
# stats-text
# ==================================================

def stats_text():
    db = load_db()

    items = db["items"]

    total = len(items)

    favorites = sum(
        1
        for x in items
        if x.get("favorite", False)
    )

    normals = total - favorites

    # ----------------------------------------------
    # 基本统计
    # ----------------------------------------------

    if total > 0:

        total_length = sum(
            len(x.get("content", ""))
            for x in items
        )

        avg_length = int(
            total_length / total
        )

        max_length = max(
            len(x.get("content", ""))
            for x in items
        )

        favorite_percent = (
                favorites / total * 100
        )

    else:

        avg_length = 0
        max_length = 0
        favorite_percent = 0

    # ----------------------------------------------
    # 时间统计
    # ----------------------------------------------

    now = now_ts()

    last7 = sum(
        1
        for x in items
        if (
                x.get("created_at", 0)
                and
                now - x.get("created_at", 0)
                <= 7 * 86400
        )
    )

    last30 = sum(
        1
        for x in items
        if (
                x.get("created_at", 0)
                and
                now - x.get("created_at", 0)
                <= 30 * 86400
        )
    )

    # ----------------------------------------------
    # 最早 / 最新记录
    # ----------------------------------------------

    timestamps = [
        x.get("created_at", 0)
        for x in items
        if x.get("created_at", 0)
    ]

    if timestamps:

        oldest_timestamp = min(
            timestamps
        )

        newest_timestamp = max(
            timestamps
        )

        oldest = datetime.fromtimestamp(
            oldest_timestamp
        ).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        newest = datetime.fromtimestamp(
            newest_timestamp
        ).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    else:

        oldest = "-"
        newest = "-"

    # ----------------------------------------------
    # 数据库大小
    # ----------------------------------------------

    if DB_FILE.exists():

        db_size_bytes = DB_FILE.stat().st_size

    else:

        db_size_bytes = 0

    db_size_mb = (
            db_size_bytes
            / 1024
            / 1024
    )

    # ----------------------------------------------
    # 导出目录
    # ----------------------------------------------

    export_dir = (
            Path(__file__).resolve().parent
            / "export-md"
    )

    export_count = 0
    export_size_bytes = 0

    if export_dir.exists():

        for file in export_dir.iterdir():

            if (
                    file.is_file()
                    and file.suffix.lower() == ".md"
            ):

                export_count += 1

                try:

                    export_size_bytes += (
                        file.stat().st_size
                    )

                except OSError:

                    pass

    export_size_mb = (
            export_size_bytes
            / 1024
            / 1024
    )

    # ----------------------------------------------
    # 输出
    # ----------------------------------------------

    print(
        f"""📊 剪贴板统计

记录
总记录：{total}
收藏：{favorites}
普通记录：{normals}
收藏占比：{favorite_percent:.1f}%

时间
最近7天新增：{last7}
最近30天新增：{last30}
最早记录：{oldest}
最新记录：{newest}

内容
平均长度：{avg_length} 字符
最长记录：{max_length} 字符

存储
数据库大小：{db_size_mb:.2f} MB
导出文件：{export_count} 个
导出目录大小：{export_size_mb:.2f} MB
"""
    )


# ==================================================
# clear
# ==================================================

def clear():
    db = load_db()

    db["items"] = [
        x
        for x in db["items"]
        if x["favorite"]
    ]

    save_db(db)

    print("OK")


# ==================================================
# clear-export
# ==================================================

def clear_export():
    export_dir = (
            Path(__file__).resolve().parent
            / "export-md"
    )

    if not export_dir.exists():
        print("NO_EXPORTS")

        return

    deleted = 0

    for file in export_dir.iterdir():

        if (
                file.is_file()
                and file.suffix.lower() == ".md"
        ):

            try:

                file.unlink()

                deleted += 1

            except OSError as e:

                print(
                    f"DELETE_ERROR: {file.name}: {e}"
                )

    print(
        f"DELETED: {deleted}"
    )


# ==================================================
# export-md
# ==================================================

def export_md():
    db = load_db()

    export_dir = (
            Path(__file__).resolve().parent
            / "export-md"
    )

    export_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    filename = (
        f"clipboard_export_{timestamp}.md"
    )

    md_file = export_dir / filename

    lines = []

    for item in db["items"]:
        lines.append(
            f"# {item['timestamp']}"
        )

        lines.append("")

        lines.append(
            item["content"]
        )

        lines.append("")
        lines.append("---")
        lines.append("")

    md_file.write_text(
        "\n".join(lines),
        encoding="utf-8"
    )

    print(md_file)


# ==================================================
# help
# ==================================================

def show_help():
    print(
        """
        Clipboard History 2.2

        Commands:

        add
        add-file FILE

        add-base64 BASE64
        add-base64-file FILE

        list
        list-json

        menu
        menu-json
        menu-with-id
        menu-id

        get ID

        search KEYWORD
        search-json KEYWORD
        search-menu KEYWORD
        search-id KEYWORD INDEX


        favorite ID
        favorites-menu
        favorites-id

        delete ID

        stats
        stats_text

        clear
        clear-export

        export-md
        """
    )


# ==================================================
# main
# ==================================================

def main():
    init_db()

    if len(sys.argv) < 2:
        show_help()
        return

    cmd = sys.argv[1]

    if cmd == "add":

        add(sys.stdin.read())

    elif cmd == "add-file":

        add_file(sys.argv[2])

    elif cmd == "add-base64":

        add_base64(sys.argv[2])

    elif cmd == "add-base64-file":

        add_base64_file(
            sys.argv[2]
        )

    elif cmd == "list":

        list_items()

    elif cmd == "list-json":

        list_json()
    elif cmd == "menu":
        menu()

    elif cmd == "menu-json":
        menu_json()

    elif cmd == "menu-with-id":
        menu_with_id()

    elif cmd == "get":

        get_item(sys.argv[2])

    elif cmd == "search":

        search(sys.argv[2])

    elif cmd == "search-json":

        search_json(
            sys.argv[2]
        )
    elif cmd == "search-menu":

        search_menu(
            sys.argv[2]
        )

    elif cmd == "search-id":

        search_id(
            sys.argv[2],
            sys.argv[3]
        )

    elif cmd == "menu-id":

        menu_id(
            sys.argv[2]
        )
    elif cmd == "favorite":

        toggle_favorite(
            sys.argv[2]
        )
    elif cmd == "favorites-menu":

        favorites_menu()

    elif cmd == "favorites-id":

        favorites_id(
            sys.argv[2]
        )

    elif cmd == "delete":

        delete_item(
            sys.argv[2]
        )

    elif cmd == "stats":

        stats()
    elif cmd == "stats-text":

        stats_text()

    elif cmd == "clear":

        clear()
    elif cmd == "clear-export":

        clear_export()

    elif cmd == "export-md":

        export_md()

    else:

        show_help()


if __name__ == "__main__":
    main()
