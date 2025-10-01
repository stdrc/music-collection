import requests
import json
import os
from datetime import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()


class AppleMusicAPI:
    def __init__(self, developer_token: str, user_token: str):
        self.developer_token = developer_token
        self.user_token = user_token
        self.base_url = "https://api.music.apple.com"
        self.headers = {
            "Authorization": f"Bearer {developer_token}",
            "Music-User-Token": user_token,
            "Content-Type": "application/json",
        }

    def make_request(self, path: str) -> Dict[str, Any]:
        """发送请求到 Apple Music API"""
        url = f"{self.base_url}{path}"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"API请求失败: {e}")
        except json.JSONDecodeError as e:
            raise Exception(f"JSON解析错误: {e}")

    def get_library_albums(self, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """获取用户音乐库中的专辑"""
        path = f"/v1/me/library/albums?limit={limit}&offset={offset}&include=artists"
        try:
            return self.make_request(path)
        except Exception as e:
            print(f"获取专辑失败: {e}")
            raise

    def get_all_library_albums(self) -> List[Dict[str, Any]]:
        """获取所有专辑并按添加时间排序"""
        all_albums = []
        offset = 0
        limit = 100
        has_more = True

        print("开始获取所有专辑...")

        while has_more:
            try:
                response = self.get_library_albums(limit, offset)
                albums = response.get("data", [])

                if albums:
                    all_albums.extend(albums)
                    offset += limit
                    print(f"已获取 {len(all_albums)} 张专辑...")

                    has_more = len(albums) == limit
                else:
                    has_more = False

            except Exception as e:
                print(f"获取专辑时出错: {e}")
                break

        # 按添加时间排序（newest first）
        all_albums.sort(
            key=lambda album: self._parse_date(
                album.get("attributes", {}).get("dateAdded", "1970-01-01T00:00:00Z")
            ),
            reverse=True,
        )

        return all_albums

    def _parse_date(self, date_string: str) -> datetime:
        """解析日期字符串"""
        try:
            # Apple Music API 返回的日期格式通常是 ISO 8601
            return datetime.fromisoformat(date_string.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            return datetime(1970, 1, 1)

    def _get_artwork_base_url(self, artwork: Dict[str, Any]) -> str:
        """获取专辑封面的基础URL（去掉尺寸参数用于比较）"""
        if not artwork or not artwork.get("url"):
            return ""
        # 移除 {w} 和 {h} 参数，获得基础URL用于比较
        return artwork.get("url", "").replace("{w}", "").replace("{h}", "")

    def merge_consecutive_duplicates(
        self, albums: List[Dict[str, Any]]
    ) -> tuple[List[Dict[str, Any]], int]:
        """合并连续的重复专辑（基于封面URL）"""
        if not albums:
            return [], 0

        merged_albums = []
        removed_count = 0
        i = 0

        while i < len(albums):
            current_album = albums[i]
            current_artwork = self._get_artwork_base_url(
                current_album.get("attributes", {}).get("artwork", {})
            )

            # 查找连续的相同封面专辑
            j = i + 1
            while j < len(albums):
                next_album = albums[j]
                next_artwork = self._get_artwork_base_url(
                    next_album.get("attributes", {}).get("artwork", {})
                )

                # 比较封面URL是否相同
                if current_artwork and next_artwork and current_artwork == next_artwork:
                    j += 1
                    removed_count += 1
                else:
                    break

            # 只保留第一个（最早添加的）
            merged_albums.append(current_album)

            # 如果找到了重复的，记录日志
            if j > i + 1:
                attrs = current_album.get("attributes", {})
                print(
                    f'合并重复专辑: "{attrs.get("name", "")}" - {attrs.get("artistName", "")} (移除 {j - i - 1} 个重复)'
                )

            # 跳到下一个不同的专辑
            i = j

        return merged_albums, removed_count

    def save_albums_to_file(
        self, albums: List[Dict[str, Any]], filename: str = "albums.json"
    ) -> List[Dict[str, Any]]:
        """保存专辑数据到文件"""
        # 合并重复专辑
        merged_albums, removed_count = self.merge_consecutive_duplicates(albums)
        print(
            f"原始专辑数: {len(albums)}, 合并后: {len(merged_albums)}, 移除重复: {removed_count}"
        )

        processed_albums = []

        for album in merged_albums:
            attributes = album.get("attributes", {})
            artwork = attributes.get("artwork", {})
            artwork_url = (
                artwork.get("url", "").replace("{w}", "300").replace("{h}", "300")
                if artwork.get("url")
                else ""
            )

            release_date = attributes.get("releaseDate", "")
            year = release_date[:4] if release_date else ""

            # 获取流派信息
            genre_names = attributes.get("genreNames", [])
            # 如果有多个流派，用逗号分隔；如果没有，留空
            genres = ", ".join(genre_names) if genre_names else ""

            processed_album = {
                "album_name": attributes.get("name", ""),
                "album_thumbnail": artwork_url,
                "artist_name": attributes.get("artistName", ""),
                "url": attributes.get("url", ""),
                "year": year,
                "genres": genres,
            }
            processed_albums.append(processed_album)

        # 保存到文件
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(processed_albums, f, ensure_ascii=False, indent=4)

        print(f"已保存 {len(processed_albums)} 张专辑到 {filename}")
        return processed_albums


def main():
    """主函数"""
    developer_token = os.getenv("AM_DEVELOPER_TOKEN")
    user_token = os.getenv("AM_USER_TOKEN")

    if not developer_token or not user_token:
        print("❌ 错误: 缺少必要的环境变量 AM_DEVELOPER_TOKEN 或 AM_USER_TOKEN")
        return

    try:
        api = AppleMusicAPI(developer_token, user_token)
        print("正在获取你的 Apple Music 专辑库...")

        albums = api.get_all_library_albums()
        print(f"✅ 成功获取 {len(albums)} 张专辑")

        api.save_albums_to_file(albums)

    except Exception as e:
        print(f"❌ 出错: {e}")


if __name__ == "__main__":
    main()
