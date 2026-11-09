"""
CapCut PC Automation Bridge
Cung cấp API đơn giản để tự động hóa tạo và chỉnh sửa dự án CapCut PC (Desktop).
"""

import os
import sys
import json
import uuid
import time
import shutil
import subprocess
from typing import Optional, List, Dict, Any, Union

import pycapcut as pc
from pycapcut import (
    ScriptFile,
    TrackType,
    VideoSegment,
    AudioSegment,
    TextSegment,
    Timerange,
    TextStyle,
    TextBorder,
    TextBackground,
    SEC,
)

DEFAULT_ROOT_META_PATH = r"C:\Users\PC\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft\root_meta_info.json"
DEFAULT_DRAFTS_FOLDER = r"C:\Users\PC\AppData\Local\CapCut Drafts"
CAPCUT_EXE_PATH = r"C:\Users\PC\AppData\Local\CapCut\CapCut.exe"


def get_capcut_drafts_path() -> str:
    """Lấy đường dẫn thư mục lưu trữ dự án CapCut từ cấu hình hệ thống."""
    if os.path.exists(DEFAULT_ROOT_META_PATH):
        try:
            with open(DEFAULT_ROOT_META_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                all_drafts = data.get("all_draft_store", [])
                if all_drafts:
                    for d in all_drafts:
                        r_path = d.get("draft_root_path")
                        if r_path and os.path.exists(r_path):
                            return r_path
                root_path = data.get("root_path")
                if root_path and os.path.exists(root_path):
                    return root_path
        except Exception:
            pass
    return DEFAULT_DRAFTS_FOLDER


class CapCutProject:
    """Quản lý một dự án CapCut PC."""

    def __init__(
        self,
        name: str,
        width: int = 1920,
        height: int = 1080,
        fps: int = 30,
        allow_replace: bool = True,
    ):
        self.name = name
        self.width = width
        self.height = height
        self.fps = fps
        self.allow_replace = allow_replace
        self.drafts_folder = get_capcut_drafts_path()
        self.project_dir = os.path.join(self.drafts_folder, name)
        self.content_file = os.path.join(self.project_dir, "draft_content.json")
        self.meta_file = os.path.join(self.project_dir, "draft_meta_info.json")
        self.draft_id = str(uuid.uuid4()).upper()

        # Giữ lại draft_id cũ nếu dự án đã tồn tại
        if os.path.exists(self.meta_file):
            try:
                with open(self.meta_file, "r", encoding="utf-8") as f:
                    old_meta = json.load(f)
                    if old_meta.get("draft_id"):
                        self.draft_id = old_meta.get("draft_id")
            except Exception:
                pass

        self.current_video_time_us = 0
        self.current_audio_time_us = 0
        self.max_duration_us = 0

        self._init_project()

    def _init_project(self):
        """Khởi tạo cấu trúc thư mục và ScriptFile của dự án."""
        if os.path.exists(self.project_dir):
            if not self.allow_replace:
                raise FileExistsError(f"Dự án '{self.name}' đã tồn tại và allow_replace=False")
            try:
                if os.path.exists(self.content_file):
                    os.remove(self.content_file)
            except Exception:
                pass
        else:
            os.makedirs(self.project_dir, exist_ok=True)

        self.script = ScriptFile(self.width, self.height, self.fps)
        self.script.save_path = self.content_file

        # Tạo sẵn track video chính
        self.main_video_track = "main_video_track"
        self.script.add_track(TrackType.video, self.main_video_track)

    def _add_segment_safe(
        self,
        segment: Any,
        track_type: TrackType,
        base_name: str,
        preferred_track: Optional[str] = None,
    ) -> str:
        """
        Thêm segment vào track an toàn, tự động xếp tầng lớp (layer) nếu bị trùng đè thời gian.
        """
        # Nếu có track chỉ định ưu tiên
        if preferred_track:
            if preferred_track not in self.script.tracks:
                self.script.add_track(track_type, preferred_track)
            try:
                self.script.tracks[preferred_track].add_segment(segment)
                return preferred_track
            except pc.exceptions.SegmentOverlap:
                pass

        # Tìm trong các track hiện có cùng type xem track nào không bị trùng
        for name, tr in list(self.script.tracks.items()):
            if tr.track_type == track_type:
                try:
                    tr.add_segment(segment)
                    return name
                except pc.exceptions.SegmentOverlap:
                    continue

        # Nếu tất cả các track cùng type đều bị trùng, tạo thêm một track layer mới
        existing_count = len([t for t in self.script.tracks.values() if t.track_type == track_type])
        new_track_name = f"{base_name}_{existing_count + 1}"
        self.script.add_track(track_type, new_track_name)
        self.script.tracks[new_track_name].add_segment(segment)
        return new_track_name

    def add_video(
        self,
        file_path: str,
        duration_sec: Optional[float] = None,
        start_time_sec: Optional[float] = None,
        speed: float = 1.0,
        track_name: Optional[str] = None,
    ) -> "CapCutProject":
        """
        Thêm clip video vào timeline.
        :param file_path: Đường dẫn tuyệt đối tới file video.
        :param duration_sec: Thời lượng lấy từ video (giây). Nếu None, tự động lấy toàn bộ.
        :param start_time_sec: Thời điểm bắt đầu trên timeline (giây). Nếu None, nối tiếp clip trước.
        :param speed: Tốc độ phát (1.0 là bình thường).
        :param track_name: Tên track video mong muốn.
        """
        file_path = os.path.abspath(file_path)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Không tìm thấy file video: {file_path}")

        # Tính thời điểm bắt đầu
        if start_time_sec is None:
            start_us = self.current_video_time_us
        else:
            start_us = int(start_time_sec * SEC)

        # Lấy thời lượng thực tế
        material = pc.local_materials.VideoMaterial(file_path)
        actual_duration_us = material.duration

        if duration_sec is not None:
            take_duration_us = int(duration_sec * SEC)
        else:
            take_duration_us = int(actual_duration_us / speed)

        target_timerange = Timerange(start_us, take_duration_us)
        source_timerange = Timerange(0, int(take_duration_us * speed))

        segment = VideoSegment(
            material=file_path,
            target_timerange=target_timerange,
            source_timerange=source_timerange,
            speed=speed,
        )

        used_track = self._add_segment_safe(
            segment=segment,
            track_type=TrackType.video,
            base_name="video_track",
            preferred_track=track_name or self.main_video_track,
        )

        end_time_us = start_us + take_duration_us
        if used_track == self.main_video_track:
            self.current_video_time_us = end_time_us

        self.max_duration_us = max(self.max_duration_us, end_time_us)
        return self

    def add_audio(
        self,
        file_path: str,
        duration_sec: Optional[float] = None,
        start_time_sec: Optional[float] = None,
        volume: float = 1.0,
        fade_in_sec: float = 0.0,
        fade_out_sec: float = 0.0,
        track_name: Optional[str] = None,
    ) -> "CapCutProject":
        """
        Thêm âm thanh (nhạc nền, voiceover) vào timeline.
        :param file_path: Đường dẫn tới file audio.
        :param duration_sec: Thời lượng phát (giây). Nếu None, phát hết file.
        :param start_time_sec: Thời điểm bắt đầu trên timeline (giây). Nếu None, nối tiếp.
        :param volume: Âm lượng (1.0 = 100%).
        :param fade_in_sec: Thời gian fade-in (giây).
        :param fade_out_sec: Thời gian fade-out (giây).
        :param track_name: Tên track âm thanh.
        """
        file_path = os.path.abspath(file_path)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Không tìm thấy file audio: {file_path}")

        if start_time_sec is None:
            start_us = self.current_audio_time_us
        else:
            start_us = int(start_time_sec * SEC)

        material = pc.local_materials.AudioMaterial(file_path)
        actual_duration_us = material.duration

        if duration_sec is not None:
            take_duration_us = int(duration_sec * SEC)
        else:
            take_duration_us = actual_duration_us

        target_timerange = Timerange(start_us, take_duration_us)
        source_timerange = Timerange(0, take_duration_us)

        segment = AudioSegment(
            material=file_path,
            target_timerange=target_timerange,
            source_timerange=source_timerange,
            volume=volume,
        )

        if fade_in_sec > 0 or fade_out_sec > 0:
            segment.add_fade(int(fade_in_sec * SEC), int(fade_out_sec * SEC))

        self._add_segment_safe(
            segment=segment,
            track_type=TrackType.audio,
            base_name="audio_track",
            preferred_track=track_name,
        )

        end_time_us = start_us + take_duration_us
        self.current_audio_time_us = end_time_us
        self.max_duration_us = max(self.max_duration_us, end_time_us)

        return self

    def add_text(
        self,
        text: str,
        start_time_sec: float,
        duration_sec: float,
        font_size: float = 8.0,
        text_color: tuple = (1.0, 1.0, 1.0),
        border_color: Optional[tuple] = None,
        border_width: float = 0.0,
        track_name: Optional[str] = None,
    ) -> "CapCutProject":
        """
        Thêm một đoạn chữ/tiêu đề vào video.
        """
        start_us = int(start_time_sec * SEC)
        duration_us = int(duration_sec * SEC)

        style = TextStyle(size=font_size, color=text_color)
        border = None
        if border_color and border_width > 0:
            border = TextBorder(color=border_color, width=border_width)

        segment = TextSegment(
            text=text,
            timerange=Timerange(start_us, duration_us),
            style=style,
            border=border,
        )

        self._add_segment_safe(
            segment=segment,
            track_type=TrackType.text,
            base_name="text_track",
            preferred_track=track_name,
        )

        self.max_duration_us = max(self.max_duration_us, start_us + duration_us)
        return self

    def add_subtitles_from_srt(
        self,
        srt_path: str,
        track_name: str = "subtitle_track",
    ) -> "CapCutProject":
        """
        Nhập toàn bộ phụ đề từ file .srt vào CapCut.
        """
        srt_path = os.path.abspath(srt_path)
        if not os.path.exists(srt_path):
            raise FileNotFoundError(f"Không tìm thấy file SRT: {srt_path}")

        self.script.import_srt(srt_path=srt_path, track_name=track_name)
        return self

    def add_subtitles_from_list(
        self,
        subtitles: List[Dict[str, Any]],
        track_name: str = "subtitle_track",
    ) -> "CapCutProject":
        """
        Nhập phụ đề từ danh sách dict: [{'text': '...', 'start': 0.0, 'end': 2.5}, ...]
        """
        for item in subtitles:
            text = item["text"]
            start = float(item["start"])
            end = float(item["end"])
            duration = max(0.2, end - start)
            self.add_text(
                text=text,
                start_time_sec=start,
                duration_sec=duration,
                font_size=7.5,
                text_color=(1.0, 1.0, 1.0),
                track_name=track_name,
            )
        return self

    def save(self) -> str:
        """
        Lưu dự án và tự động đăng ký với CapCut Desktop để xuất hiện ngay trên trang chủ CapCut.
        """
        now_us = int(time.time() * 1000000)
        duration = max(self.max_duration_us, 1000000)

        # 1. Lưu draft_content.json
        self.script.duration = duration
        self.script.save()

        # Cập nhật duration và ratio chính xác cho canvas_config trong draft_content.json
        try:
            with open(self.content_file, "r", encoding="utf-8") as f:
                cdata = json.load(f)
            cdata["duration"] = duration
            if self.width == 1080 and self.height == 1920:
                cdata["canvas_config"]["ratio"] = "9:16"
            elif self.width == 1920 and self.height == 1080:
                cdata["canvas_config"]["ratio"] = "16:9"
            with open(self.content_file, "w", encoding="utf-8") as f:
                json.dump(cdata, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

        # 2. Tạo draft_meta_info.json chuẩn
        template_meta_path = pc.assets.get_asset_path("DRAFT_META_TEMPLATE")
        with open(template_meta_path, "r", encoding="utf-8") as f:
            meta_data = json.load(f)

        duration = max(self.max_duration_us, 1000000)

        meta_data["draft_id"] = self.draft_id
        meta_data["draft_name"] = self.name
        meta_data["draft_fold_path"] = self.project_dir.replace("\\", "/")
        meta_data["draft_root_path"] = self.drafts_folder.replace("\\", "/")
        meta_data["tm_draft_create"] = now_us
        meta_data["tm_draft_modified"] = now_us
        meta_data["tm_duration"] = duration

        with open(self.meta_file, "w", encoding="utf-8") as f:
            json.dump(meta_data, f, ensure_ascii=False, indent=2)

        # 3. Đăng ký dự án vào root_meta_info.json của CapCut Desktop
        self._register_in_root_meta(now_us, duration)

        return self.project_dir

    def _register_in_root_meta(self, timestamp_us: int, duration_us: int):
        """Cập nhật root_meta_info.json để CapCut Desktop hiển thị ngay dự án."""
        if not os.path.exists(DEFAULT_ROOT_META_PATH):
            return

        try:
            with open(DEFAULT_ROOT_META_PATH, "r", encoding="utf-8") as f:
                root_data = json.load(f)

            all_drafts = root_data.get("all_draft_store", [])
            draft_ids = root_data.get("draft_ids", 0)

            # Loại bỏ entry cũ cùng tên nếu có
            all_drafts = [d for d in all_drafts if d.get("draft_name") != self.name]

            new_entry = {
                "cloud_draft_cover": False,
                "cloud_draft_sync": False,
                "draft_cloud_last_action_download": False,
                "draft_cloud_purchase_info": "",
                "draft_cloud_template_id": "",
                "draft_cloud_tutorial_info": "",
                "draft_cloud_videocut_purchase_info": "",
                "draft_cover": os.path.join(self.project_dir, "draft_cover.jpg").replace("\\", "/"),
                "draft_fold_path": self.project_dir.replace("\\", "/"),
                "draft_id": self.draft_id,
                "draft_is_ai_shorts": False,
                "draft_is_cloud_temp_draft": False,
                "draft_is_infinite_canvas_draft": False,
                "draft_is_invisible": False,
                "draft_is_pippit_draft": False,
                "draft_is_web_article_video": False,
                "draft_json_file": self.content_file.replace("\\", "/"),
                "draft_name": self.name,
                "draft_new_version": "",
                "draft_root_path": self.drafts_folder.replace("\\", "/"),
                "draft_timeline_materials_size": 10000,
                "draft_type": "",
                "draft_web_article_video_enter_from": "",
                "pippit_avatar_url": "",
                "pippit_extra_info": "",
                "pippit_id": "",
                "pippit_user_name": "",
                "streaming_edit_draft_ready": True,
                "tm_draft_cloud_completed": "",
                "tm_draft_cloud_entry_id": -1,
                "tm_draft_cloud_modified": 0,
                "tm_draft_cloud_parent_entry_id": -1,
                "tm_draft_cloud_space_id": -1,
                "tm_draft_cloud_user_id": -1,
                "tm_draft_create": timestamp_us,
                "tm_draft_modified": timestamp_us,
                "tm_draft_removed": 0,
                "tm_duration": duration_us,
            }

            # Chèn lên đầu danh sách
            all_drafts.insert(0, new_entry)

            if isinstance(draft_ids, list):
                draft_ids = [d_id for d_id in draft_ids if d_id != self.draft_id]
                draft_ids.insert(0, self.draft_id)
                root_data["draft_ids"] = draft_ids
            elif isinstance(draft_ids, int):
                root_data["draft_ids"] = draft_ids + 1

            root_data["all_draft_store"] = all_drafts

            with open(DEFAULT_ROOT_META_PATH, "w", encoding="utf-8") as f:
                json.dump(root_data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"[Cảnh báo] Không thể cập nhật root_meta_info.json: {e}")


def list_projects() -> List[Dict[str, Any]]:
    """Liệt kê danh sách các dự án CapCut hiện có trên máy."""
    if not os.path.exists(DEFAULT_ROOT_META_PATH):
        return []

    try:
        with open(DEFAULT_ROOT_META_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        projects = []
        for draft in data.get("all_draft_store", []):
            projects.append({
                "name": draft.get("draft_name"),
                "path": draft.get("draft_fold_path"),
                "duration_sec": round(draft.get("tm_duration", 0) / 1000000, 2),
            })
        return projects
    except Exception as e:
        print(f"Lỗi khi đọc danh sách dự án: {e}")
        return []


def open_capcut() -> bool:
    """Mở hoặc đưa cửa sổ CapCut Desktop lên phía trước."""
    try:
        # Nếu đang chạy, kích hoạt ứng dụng
        res = subprocess.run(
            ["powershell", "-Command", "Get-Process CapCut -ErrorAction SilentlyContinue"],
            capture_output=True,
            text=True,
        )
        if "CapCut" in res.stdout:
            # Dùng PowerShell kích hoạt window
            subprocess.run(
                [
                    "powershell",
                    "-Command",
                    """
                    $w = (Get-Process CapCut | Where-Object {$_.MainWindowHandle -ne 0} | Select-Object -First 1);
                    if ($w) {
                        (New-Object -ComObject WScript.Shell).AppActivate($w.Id)
                    }
                    """,
                ],
                capture_output=True,
            )
            return True
        else:
            if os.path.exists(CAPCUT_EXE_PATH):
                os.startfile(CAPCUT_EXE_PATH)
                return True
    except Exception as e:
        print(f"Không thể mở CapCut: {e}")
    return False
