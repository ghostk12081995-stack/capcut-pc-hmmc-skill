import json
import uuid
import os
import sys
import shutil
import time
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')

PROJECT_NAME = "261109 HMMC T69"
DRAFT_DIR = os.path.join(r"C:\Users\PC\AppData\Local\CapCut Drafts", PROJECT_NAME)
DRAFT_PATH = os.path.join(DRAFT_DIR, "draft_content.json")
META_PATH = os.path.join(DRAFT_DIR, "draft_meta_info.json")
ROOT_META_PATH = r"C:\Users\PC\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft\root_meta_info.json"

PROJ_DIR = r"D:\Hoàng\Tháng 11\261109 HMMC T69"
SRT_PATH = os.path.join(PROJ_DIR, "261109_HMMC_T69_Subtitles.srt")
BGM_PATH = r"D:\Hoàng\BGM\Corporate - envato_X5EX6PL\Short 01.20.mp3"

FONT_PATH = "C:/Users/PC/AppData/Local/Microsoft/Windows/Fonts/SVN-Gilroy SemiBold.otf"
ANIM_POP_UP_IN_PATH = "C:/Users/PC/AppData/Local/CapCut/User Data/Cache/effect/7646374911761452306/e6d2a3fe1dcda847f8e71fcbd559a9ef"
ANIM_POP_UP_IN_ID = "7646374911761452306"
TEXT_EFFECT_PATH = "C:/Users/PC/AppData/Local/CapCut/User Data/Cache/effect/7528350137333189941/a387bca7253535c9ddca49b830339276"
TEXT_EFFECT_ID = "7528350137333189941"
ADJUST_BUNDLE_PATH = "C:/Users/PC/AppData/Local/CapCut/User Data/Cache/effect/7501974767453474064/20cd8db6531c21bf7e4053026d20e395"
LUMI_HUB_PATH = f"{ADJUST_BUNDLE_PATH}/lumi_hub_path"

TOTAL_DURATION_US = 46833333  # 46.833s

# 1. Backup original draft
backup_path = os.path.join(DRAFT_DIR, "draft_content.json.original_bak")
if not os.path.exists(backup_path):
    shutil.copy2(DRAFT_PATH, backup_path)
    print(f"Backed up original draft to: {backup_path}")
else:
    # Always start clean from original backup so we don't duplicate materials
    shutil.copy2(backup_path, DRAFT_PATH)

with open(DRAFT_PATH, "r", encoding="utf-8") as f:
    draft = json.load(f)

# Ensure material lists exist
for k in [
    "videos", "audios", "texts", "stickers", "material_animations",
    "effects", "hsl", "placeholders", "speeds", "placeholder_infos",
    "canvases", "sound_channel_mappings", "material_colors", "vocal_separations",
    "audio_fades"
]:
    if k not in draft["materials"]:
        draft["materials"][k] = []

# ==============================================================================
# PART 1: LOAD WHISPER WORDS & BUILD KARAOKE 1-LINE SUBTITLES
# ==============================================================================
with open(r"C:\Users\PC\.gemini\antigravity\brain\55d5d63a-e3bd-4e5e-9917-86afb4b04259\scratch\t69_transcripts.json", "r", encoding="utf-8") as f:
    trans_data = json.load(f)

words = []
for seg in trans_data:
    t_offset = seg["timeline_start"] - seg["src_start"]
    for w in seg["words"]:
        words.append({
            "word": w["word"],
            "t_start": round(t_offset + w["start"], 3),
            "t_end": round(t_offset + w["end"], 3),
        })

assert len(words) == 194, f"Expected 194 words, got {len(words)}"

CHUNKS_SPEC = [
    # Segment 0 (0.000s -> 8.000s)
    (0, ["Có", "nhiều", "bạn"], 0, 3),
    (1, ["đang", "niềng", "răng"], 3, 6),
    (2, ["thắc", "mắc", "với", "bác", "sĩ", "là:"], 6, 12),
    (3, ["'Ủa,", "em", "niềng"], 12, 15),
    (4, ["để", "răng", "đều", "lại"], 15, 19),
    (5, ["mà", "sao", "bác", "sĩ"], 19, 23),
    (6, ["còn", "gắn", "thêm"], 23, 26),
    (7, ["cái", "lò", "xo"], 26, 29),
    (8, ["để", "đẩy", "hai", "răng"], 29, 33),
    (9, ["ra", "xa", "thế", "ạ?'"], 33, 37),

    # Segment 1 (8.000s -> 9.700s)
    (10, ["Nghe", "hơi", "ngược", "đời"], 37, 41),
    (11, ["đúng", "không?"], 41, 43),

    # Segment 2 (9.700s -> 20.567s)
    (12, ["Nhưng", "thực", "ra,"], 43, 46),
    (13, ["có", "những", "trường", "hợp"], 46, 50),
    (14, ["răng", "mọc", "chen", "chúc", "quá,"], 50, 55),
    (15, ["không", "còn", "đủ", "chỗ"], 55, 59),
    (16, ["trên", "cung", "hàm."], 59, 62),
    (17, ["Ví", "dụ", "như", "một", "chiếc"], 62, 67),
    (18, ["răng", "nanh", "mọc", "cao,"], 67, 71),
    (19, ["muốn", "đưa", "nó"], 71, 74),
    (20, ["về", "đúng", "hàng"], 74, 77),
    (21, ["thì", "trước", "tiên"], 77, 80),
    (22, ["phải", "tạo", "được"], 80, 83),
    (23, ["khoảng", "trống", "đã."], 83, 86),

    # Segment 3 (20.567s -> 23.433s)
    (24, ["Và", "đây", "chính", "là"], 86, 90),
    (25, ["nhiệm", "vụ", "của", "chiếc"], 90, 94),
    (26, ["lò", "xo", "nhỏ", "này."], 94, 98),

    # Segment 4 (23.433s -> 32.000s)
    (27, ["Bác", "sĩ", "sẽ", "đặt"], 98, 102),
    (28, ["lò", "xo", "trên", "dây", "cung,"], 102, 107),
    (29, ["giữa", "hai", "mắc", "cài."], 107, 111),
    (30, ["Khi", "bị", "nén", "lại,"], 111, 115),
    (31, ["lò", "xo", "có", "xu", "hướng"], 115, 120),
    (32, ["giãn", "ra,", "tạo", "lực", "nhẹ"], 120, 125),
    (33, ["để", "mở", "dần"], 125, 128),
    (34, ["khoảng", "trống"], 128, 130),
    (35, ["giữa", "các", "răng."], 130, 133),

    # Segment 5 (32.000s -> 37.200s)
    (36, ["Khi", "đã", "có", "đủ", "chỗ,"], 133, 138),
    (37, ["bác", "sĩ", "mới", "tiếp", "tục"], 138, 143),
    (38, ["điều", "chỉnh", "để", "đưa"], 143, 147),
    (39, ["chiếc", "răng", "lệch"], 147, 150),
    (40, ["về", "vị", "trí", "mong", "muốn."], 150, 155),

    # Segment 6 (37.200s -> 41.133s)
    (41, ["Vậy", "nên", "đừng", "thấy"], 155, 159),
    (42, ["bác", "sĩ", "cố", "tình"], 159, 163),
    (43, ["đẩy", "hai", "răng", "ra", "xa"], 163, 168),
    (44, ["mà", "lo", "lắng", "nhé."], 168, 172),

    # Segment 7 (41.133s -> 46.833s)
    (45, ["Đôi", "khi,", "muốn", "các", "răng"], 172, 177),
    (46, ["đứng", "ngay", "ngắn"], 177, 180),
    (47, ["cạnh", "nhau", "thì"], 180, 183),
    (48, ["trước", "hết", "phải", "tạo"], 183, 187),
    (49, ["đủ", "chỗ", "cho", "từng"], 187, 191),
    (50, ["chiếc", "răng", "đã!"], 191, 194),
]

# Register effect: ART EN CHALK M7
effect_inst_id = str(uuid.uuid4()).upper()
draft["materials"]["effects"].append({
    "id": effect_inst_id,
    "effect_id": TEXT_EFFECT_ID,
    "resource_id": TEXT_EFFECT_ID,
    "third_resource_id": "0",
    "name": "ART EN CHALK  M7 - Chalk With Background",
    "report_name": "",
    "type": "text_effect",
    "sub_type": "none",
    "path": TEXT_EFFECT_PATH,
    "value": 1.0,
    "visible": True,
    "item_effect_type": 0,
    "category_id": "panel-text-flower_fav",
    "category_name": "Favorites",
    "category_key": "",
    "sub_category_id": "",
    "sub_category_name": "",
    "platform": "all",
    "apply_target_type": 0,
    "source_platform": 1,
    "version": "",
    "adjust_params": [],
    "time_range": None,
    "formula_id": "",
    "enable_skin_tone_correction": False,
    "algorithm_artifact_path": "",
    "intensity_key": "",
    "face_adjust_params": [],
    "exclusion_group": [],
    "panel_id": "",
    "bloom_params": None,
    "request_id": "",
    "color_match_info": {
        "target_feature_path": "",
        "source_feature_path": "",
        "target_image_path": "",
        "reference_id": "",
        "reference_name": "",
        "custom_reference_id": "",
        "custom_target_image_path": "",
        "custom_target_feature_path": ""
    },
    "multi_language_current": "",
    "lumi_hub_path": "",
    "covering_relation_change": 0,
    "beauty_face_auto_preset_id": "",
    "beauty_body_auto_preset_id": "",
    "beauty_face_auto_retouch_info": {"face_id": [], "beauty_face_auto_retouch_id": ""},
    "smart_color_mode": 0,
    "is_from_intelligent_quality": False,
    "transparent_params": "",
    "is_aigc_filter": False,
    "aigc_current_artifact_path": ""
})

anim_empty_id = str(uuid.uuid4()).upper()
draft["materials"]["material_animations"].append({
    "id": anim_empty_id,
    "type": "sticker_animation",
    "animations": [],
    "multi_language_current": "none"
})

TRANSFORM_X = 0.0
TRANSFORM_Y = -0.42
FONT_SIZE = 9.5

subtitle_segments = []

for chunk_idx, disp_words, start_mapped_idx, end_mapped_idx in CHUNKS_SPEC:
    mapped_slice = words[start_mapped_idx:end_mapped_idx]
    full_text = " ".join(disp_words)

    word_char_ranges = []
    curr_char = 0
    for w in disp_words:
        w_start = curr_char
        w_end = w_start + len(w)
        word_char_ranges.append((w_start, w_end))
        curr_char = w_end + 1

    word_timings = []
    for w in mapped_slice:
        word_timings.append((int(round(w["t_start"] * 1000000)), int(round(w["t_end"] * 1000000))))

    chunk_start_us = word_timings[0][0]
    chunk_end_us = word_timings[-1][1]

    if chunk_idx < len(CHUNKS_SPEC) - 1:
        next_mapped_start = int(round(words[CHUNKS_SPEC[chunk_idx + 1][2]]["t_start"] * 1000000))
        gap = next_mapped_start - chunk_end_us
        if 0 < gap < 250000:
            chunk_end_us = next_mapped_start
            word_timings[-1] = (word_timings[-1][0], chunk_end_us)

    capcut_words = {"start_time": [], "end_time": [], "text": []}
    for i, w in enumerate(disp_words):
        t_start_ms = max(0, int((word_timings[i][0] - chunk_start_us) / 1000))
        t_end_ms = max(t_start_ms + 10, int((word_timings[i][1] - chunk_start_us) / 1000))
        capcut_words["start_time"].append(t_start_ms)
        capcut_words["end_time"].append(t_end_ms)
        capcut_words["text"].append(w)
        if i < len(disp_words) - 1:
            capcut_words["start_time"].append(t_end_ms)
            capcut_words["end_time"].append(t_end_ms)
            capcut_words["text"].append(" ")

    anim_entrance_id = str(uuid.uuid4()).upper()
    draft["materials"]["material_animations"].append({
        "id": anim_entrance_id,
        "type": "sticker_animation",
        "animations": [{
            "id": ANIM_POP_UP_IN_ID,
            "type": "in",
            "start": 0,
            "duration": 250000,
            "path": ANIM_POP_UP_IN_PATH,
            "platform": "all",
            "resource_id": ANIM_POP_UP_IN_ID,
            "third_resource_id": "0",
            "source_platform": 1,
            "name": "Pop Up In",
            "category_id": "ruchang_fav",
            "category_name": "Favorites",
            "panel": "",
            "material_type": "sticker",
            "anim_adjust_params": None,
            "request_id": ""
        }],
        "multi_language_current": "none"
    })

    for word_idx, w in enumerate(disp_words):
        c_start, c_end = word_char_ranges[word_idx]
        seg_start_us = word_timings[word_idx][0]
        if word_idx < len(disp_words) - 1:
            seg_end_us = word_timings[word_idx + 1][0]
        else:
            seg_end_us = word_timings[word_idx][1]
        seg_duration_us = max(10000, seg_end_us - seg_start_us)

        styles = []
        if c_start > 0:
            styles.append({
                "fill": {"content": {"render_type": "solid", "solid": {"color": [1.0, 1.0, 1.0]}}},
                "font": {"path": FONT_PATH, "id": ""},
                "size": FONT_SIZE,
                "strokes": [{"content": {"render_type": "solid", "solid": {"color": [0.0, 0.0, 0.0]}}, "width": 0.08}],
                "range": [0, c_start]
            })
        styles.append({
            "fill": {"content": {"render_type": "solid", "solid": {"color": [1.0, 0.88, 0.0]}}},
            "font": {"path": FONT_PATH, "id": ""},
            "size": FONT_SIZE,
            "strokes": [{"content": {"render_type": "solid", "solid": {"color": [0.0, 0.0, 0.0]}}, "width": 0.08}],
            "range": [c_start, c_end]
        })
        if c_end < len(full_text):
            styles.append({
                "fill": {"content": {"render_type": "solid", "solid": {"color": [1.0, 1.0, 1.0]}}},
                "font": {"path": FONT_PATH, "id": ""},
                "size": FONT_SIZE,
                "strokes": [{"content": {"render_type": "solid", "solid": {"color": [0.0, 0.0, 0.0]}}, "width": 0.08}],
                "range": [c_end, len(full_text)]
            })

        text_content_json = json.dumps({"text": full_text, "styles": styles}, ensure_ascii=False)
        base_content_json = json.dumps({
            "styles": [{
                "fill": {"alpha": 1.0, "content": {"render_type": "solid", "solid": {"alpha": 1.0, "color": [1.0, 1.0, 1.0]}}},
                "font": {"id": "", "path": FONT_PATH},
                "range": [0, len(full_text)],
                "size": FONT_SIZE
            }],
            "text": full_text
        }, ensure_ascii=False)

        text_mat_id = str(uuid.uuid4()).upper()
        draft["materials"]["texts"].append({
            "recognize_task_id": "",
            "id": text_mat_id,
            "name": "",
            "recognize_text": full_text,
            "recognize_model": "",
            "punc_model": "",
            "type": "subtitle",
            "content": text_content_json,
            "base_content": base_content_json,
            "words": capcut_words,
            "current_words": {"start_time": [], "end_time": [], "text": []},
            "global_alpha": 1.0,
            "combo_info": {"text_templates": []},
            "caption_template_info": {"resource_id": "", "third_resource_id": "", "resource_name": "", "category_id": "", "category_name": "", "effect_id": "", "request_id": "", "path": "", "is_new": False, "source_platform": 0},
            "layer_weight": 1,
            "letter_spacing": 0.0,
            "text_curve": None,
            "text_loop_on_path": False,
            "offset_on_path": 0.0,
            "enable_path_typesetting": False,
            "text_exceeds_path_process_type": 0,
            "text_typesetting_paths": None,
            "text_typesetting_paths_file": "",
            "text_typesetting_path_index": 0,
            "line_spacing": 0.02,
            "has_shadow": True,
            "shadow_color": "#000000",
            "shadow_alpha": 0.6,
            "shadow_smoothing": 0.45,
            "shadow_distance": 4.0,
            "shadow_point": {"x": 0.636, "y": -0.636},
            "shadow_angle": -45.0,
            "shadow_thickness_projection_enable": False,
            "shadow_thickness_projection_angle": 0.0,
            "shadow_thickness_projection_distance": 0.0,
            "border_alpha": 1.0,
            "border_color": "#000000",
            "border_width": 0.08,
            "border_mode": 0,
            "style_name": "",
            "text_color": "#FFFFFF",
            "text_alpha": 1.0,
            "font_name": "",
            "font_title": "none",
            "font_size": FONT_SIZE,
            "font_path": FONT_PATH,
            "font_id": "",
            "font_resource_id": "",
            "initial_scale": 1.0,
            "font_url": "",
            "typesetting": 0,
            "alignment": 1,
            "line_feed": 1,
            "use_effect_default_color": False,
            "is_rich_text": False,
            "shape_clip_x": False,
            "shape_clip_y": False,
            "ktv_color": "#FFE600",
            "text_to_audio_ids": [],
            "bold_width": 0.0,
            "italic_degree": 0,
            "underline": False,
            "underline_width": 0.05,
            "underline_offset": 0.22,
            "sub_type": 0,
            "check_flag": 7,
            "text_size": 30,
            "font_category_name": "",
            "font_source_platform": 0,
            "font_third_resource_id": "",
            "font_category_id": "",
            "add_type": 1,
            "operation_type": 0,
            "recognize_type": 0,
            "fonts": [],
            "background_color": "",
            "background_alpha": 1.0,
            "background_style": 0,
            "background_round_radius": 0.0,
            "background_width": 0.14,
            "background_height": 0.14,
            "background_vertical_offset": 0.0,
            "background_horizontal_offset": 0.0,
            "background_fill": "",
            "single_char_bg_enable": False,
            "single_char_bg_color": "",
            "single_char_bg_alpha": 1.0,
            "single_char_bg_round_radius": 0.3,
            "single_char_bg_width": 0.0,
            "single_char_bg_height": 0.0,
            "single_char_bg_vertical_offset": 0.0,
            "single_char_bg_horizontal_offset": 0.0,
            "font_team_id": "",
            "tts_auto_update": False,
            "text_preset_resource_id": "",
            "group_id": "vi-VN_karaoke_sub",
            "preset_id": "",
            "preset_name": "",
            "preset_category": "",
            "preset_category_id": "",
            "preset_index": 0,
            "preset_has_set_alignment": False,
            "force_apply_line_max_width": False,
            "language": "vi-VN",
            "relevance_segment": [],
            "original_size": [],
            "fixed_width": -1.0,
            "fixed_height": -1.0,
            "autoAdaptCanvasEnabled": False,
            "line_max_width": 0.80,
            "oneline_cutoff": False,
            "cutoff_postfix": "",
            "subtitle_template_original_fontsize": 0.0,
            "subtitle_keywords": {"range": []},
            "inner_padding": -1.0,
            "multi_language_current": "none",
            "source_from": "",
            "is_lyric_effect": False,
            "lyric_group_id": "",
            "lyrics_template": {"resource_id": "", "resource_name": "", "panel": "", "effect_id": "", "path": "", "category_id": "", "category_name": "", "request_id": ""},
            "is_batch_replace": False,
            "is_words_linear": False,
            "ssml_content": "",
            "subtitle_keywords_config": None,
            "sub_template_id": -1,
            "translate_original_text": "",
            "adjust_params": []
        })

        anim_ref = anim_entrance_id if word_idx == 0 else anim_empty_id
        seg_id = str(uuid.uuid4()).upper()
        subtitle_segments.append({
            "id": seg_id,
            "source_timerange": None,
            "target_timerange": {"start": seg_start_us, "duration": seg_duration_us},
            "render_timerange": {"start": 0, "duration": 0},
            "desc": "",
            "state": 0,
            "speed": 1.0,
            "is_loop": False,
            "is_tone_modify": False,
            "reverse": False,
            "intensifies_audio": False,
            "cartoon": False,
            "volume": 1.0,
            "last_nonzero_volume": 1.0,
            "clip": {
                "scale": {"x": 1.0, "y": 1.0},
                "rotation": 0.0,
                "rotation3d": [],
                "transform": {"x": TRANSFORM_X, "y": TRANSFORM_Y},
                "flip": {"vertical": False, "horizontal": False},
                "alpha": 1.0
            },
            "uniform_scale": {"on": True, "value": 1.0},
            "material_id": text_mat_id,
            "extra_material_refs": [anim_ref, effect_inst_id, effect_inst_id],
            "render_index": 14000 + len(subtitle_segments),
            "keyframe_refs": [],
            "enable_lut": False,
            "enable_adjust": False,
            "enable_hsl": False,
            "visible": True,
            "group_id": "",
            "enable_color_curves": True,
            "enable_hsl_curves": True,
            "track_render_index": 5,
            "hdr_settings": None,
            "hdr_vivid_settings": None,
            "enable_color_wheels": True,
            "track_attribute": 0,
            "is_placeholder": False,
            "template_id": "",
            "enable_smart_color_adjust": False,
            "template_scene": "default",
            "common_keyframes": [],
            "caption_info": None,
            "responsive_layout": {"enable": False, "target_follow": "", "size_layout": 0, "horizontal_pos_layout": 0, "vertical_pos_layout": 0},
            "enable_color_match_adjust": False,
            "enable_color_correct_adjust": False,
            "enable_adjust_mask": False,
            "raw_segment_id": "",
            "lyric_keyframes": None,
            "enable_video_mask": True,
            "digital_human_template_group_id": "",
            "color_correct_alg_result": "",
            "source": "segmentsourcenormal",
            "enable_mask_stroke": False,
            "enable_mask_shadow": False,
            "enable_color_adjust_pro": False,
            "segment_color_tag": ""
        })

print(f"Created {len(subtitle_segments)} 1-line karaoke segments across {len(CHUNKS_SPEC)} chunks.")

# Export SRT file
def fmt_srt(us):
    ms = (us // 1000) % 1000
    sec = (us // 1000000) % 60
    mn = (us // 60000000) % 60
    hr = us // 3600000000
    return f"{hr:02d}:{mn:02d}:{sec:02d},{ms:03d}"

srt_lines = []
for chunk_idx, disp_words, start_mapped_idx, end_mapped_idx in CHUNKS_SPEC:
    mapped_slice = words[start_mapped_idx:end_mapped_idx]
    c_start = int(round(mapped_slice[0]["t_start"] * 1000000))
    c_end = int(round(mapped_slice[-1]["t_end"] * 1000000))
    if chunk_idx < len(CHUNKS_SPEC) - 1:
        next_mapped_start = int(round(words[CHUNKS_SPEC[chunk_idx + 1][2]]["t_start"] * 1000000))
        gap = next_mapped_start - c_end
        if 0 < gap < 250000:
            c_end = next_mapped_start
    chunk_text = " ".join(disp_words)
    srt_lines.append(f"{chunk_idx + 1}\n{fmt_srt(c_start)} --> {fmt_srt(c_end)}\n{chunk_text}\n")

with open(SRT_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(srt_lines))
print(f"Exported SRT file: {SRT_PATH}")

# ==============================================================================
# PART 2: TRACK 0 — MAIN VIDEO FOOTAGE MONTAGE (0.00s -> 46.833s)
# ==============================================================================
with open(r"C:\Users\PC\.gemini\antigravity\brain\55d5d63a-e3bd-4e5e-9917-86afb4b04259\scratch\t69_video_meta.json", "r", encoding="utf-8") as f:
    video_meta = json.load(f)

video_mats = {}
for fname, meta in video_meta.items():
    fpath = os.path.join(PROJ_DIR, fname).replace("\\", "/")
    mat_id = str(uuid.uuid4()).upper()
    video_mats[fname] = {
        "id": mat_id,
        "unique_id": "",
        "type": "video",
        "duration": meta["dur_us"],
        "path": fpath,
        "media_path": "",
        "local_id": "",
        "has_audio": True,
        "reverse_path": "",
        "intensifies_path": "",
        "reverse_intensifies_path": "",
        "intensifies_audio_path": "",
        "cartoon_path": "",
        "width": meta["w"],
        "height": meta["h"],
        "category_id": "",
        "category_name": "local",
        "material_id": "",
        "material_name": fname,
        "material_url": "",
        "crop": {"upper_left_x": 0.0, "upper_left_y": 0.0, "upper_right_x": 1.0, "upper_right_y": 0.0, "lower_left_x": 0.0, "lower_left_y": 1.0, "lower_right_x": 1.0, "lower_right_y": 1.0},
        "crop_ratio": "free",
        "audio_fade": None,
        "crop_scale": 1.0,
        "extra_type_option": 0,
        "stable": {"stable_level": 2, "matrix_path": "", "time_range": {"start": 0, "duration": 0}},
        "matting": {"flag": 0, "path": "", "interactiveTime": [], "has_use_quick_brush": False, "strokes": [], "has_use_quick_eraser": False, "expansion": 0, "feather": 0, "reverse": False, "custom_matting_id": "", "enable_matting_stroke": False, "is_clould": False, "mask_video_path": "", "cloud_product_fps": 0.0},
        "source": 0,
        "source_platform": 0,
        "formula_id": "",
        "check_flag": 62978047,
        "video_algorithm": {"algorithms": [], "time_range": None, "path": "", "gameplay_configs": [], "ai_in_painting_config": [], "complement_frame_config": None, "motion_blur_config": None, "deflicker": None, "noise_reduction": None, "quality_enhance": None, "super_resolution": None, "ai_background_configs": [], "smart_complement_frame": None, "aigc_generate": None, "aigc_generate_list": [], "mouth_shape_driver": None, "ai_expression_driven": None, "ai_motion_driven": None, "image_interpretation": None, "story_video_modify_video_config": {"task_id": "", "is_overwrite_last_video": False, "tracker_task_id": ""}, "skip_algorithm_index": []},
        "is_unified_beauty_mode": False,
        "is_set_beauty_mode": False,
        "object_locked": None,
        "smart_motion": None,
        "multi_camera_info": None,
        "freeze": None,
        "picture_from": "none",
        "picture_set_category_id": "",
        "picture_set_category_name": "",
        "team_id": "",
        "local_material_id": str(uuid.uuid4()).lower(),
        "origin_material_id": "",
        "request_id": "",
        "has_sound_separated": False,
        "is_text_edit_overdub": False,
        "is_ai_generate_content": False,
        "aigc_type": "none",
        "is_copyright": False,
        "aigc_history_id": "",
        "aigc_item_id": "",
        "local_material_from": "",
        "smart_match_info": None,
        "beauty_face_preset_infos": [],
        "beauty_body_preset_id": "",
        "beauty_face_auto_preset": {"preset_id": "", "name": "", "rate_map": "", "scene": ""},
        "beauty_face_auto_preset_infos": [],
        "beauty_body_auto_preset": None,
        "live_photo_timestamp": -1,
        "live_photo_cover_path": "",
        "content_feature_info": None,
        "corner_pin": None,
        "surface_trackings": [],
        "video_mask_stroke": {"resource_id": "", "path": "", "type": "", "color": "", "size": 0.0, "alpha": 0.0, "distance": 0.0, "texture": 0.0, "horizontal_shift": 0.0, "vertical_shift": 0.0},
        "video_mask_shadow": {"resource_id": "", "path": "", "color": "", "alpha": 0.0, "blur": 0.0, "distance": 0.0, "angle": 0.0}
    }
    draft["materials"]["videos"].append(video_mats[fname])

# 10 Video Clips across 0.00s -> 46.833333s
clips_plan = [
    # 1. Hook (0.00s - 8.00s): Zoom cận cảnh chiếc lò xo nằm trên dây cung mắc cài đẩy 2 răng
    {
        "file": "Scene1_Open_Coil_Spring_Installation_3D.mp4",
        "src_start": 28000000,
        "src_dur": 8000000,
        "tgt_start": 0,
        "tgt_dur": 8000000,
        "scale": 2.4,
        "trans_x": 0.05,
        "trans_y": 0.02,
    },
    # 2. Câu hỏi nghịch lý (8.00s - 9.70s): "Nghe hơi ngược đời đúng không?" -> Cận cảnh lâm sàng lò xo mở khoảng
    {
        "file": "Scene1_High_Canine_Open_Coil_Spring_CloseUp.mp4",
        "src_start": 10000000,
        "src_dur": 1700000,
        "tgt_start": 8000000,
        "tgt_dur": 1700000,
        "scale": 2.2,
        "trans_x": 0.0,
        "trans_y": 0.0,
    },
    # 3A. Răng chen chúc (9.70s - 15.00s): "Nhưng thực ra, có những trường hợp răng mọc chen chúc quá, không còn đủ chỗ trên cung hàm."
    {
        "file": "Scene2_High_Canines_And_Braces_3D.mp4",
        "src_start": 18500000,
        "src_dur": 5300000,
        "tgt_start": 9700000,
        "tgt_dur": 5300000,
        "scale": 2.3,
        "trans_x": 0.0,
        "trans_y": 0.0,
    },
    # 3B. Răng nanh mọc cao thiếu chỗ (15.00s - 20.567s): "Ví dụ như một chiếc răng nanh mọc cao, muốn đưa nó về đúng hàng thì trước tiên phải tạo được khoảng trống đã."
    {
        "file": "Scene1_Creating_Space_Impacted_Canine_Coil_Spring.mp4",
        "src_start": 7000000,
        "src_dur": 5566667,
        "tgt_start": 15000000,
        "tgt_dur": 5566667,
        "scale": 2.4,
        "trans_x": 0.10,
        "trans_y": 0.0,
    },
    # 4. Nhiệm vụ của chiếc lò xo nhỏ (20.567s - 23.433s): "Và đây chính là nhiệm vụ của chiếc lò xo nhỏ này."
    {
        "file": "Scene3_Open_Coil_Spring_Clinical_Orthodontics.mp4",
        "src_start": 54000000,
        "src_dur": 2866666,
        "tgt_start": 20566667,
        "tgt_dur": 2866666,
        "scale": 2.3,
        "trans_x": 0.0,
        "trans_y": 0.0,
    },
    # 5A. Bác sĩ đặt lò xo trên dây cung (23.433s - 27.30s): "Bác sĩ sẽ đặt lò xo trên dây cung, giữa hai mắc cài. Khi bị nén lại..."
    {
        "file": "Scene1_High_Canine_Open_Coil_Spring_CloseUp.mp4",
        "src_start": 63000000,
        "src_dur": 3866667,
        "tgt_start": 23433333,
        "tgt_dur": 3866667,
        "scale": 2.3,
        "trans_x": 0.0,
        "trans_y": 0.0,
    },
    # 5B. Animation lò xo giãn mở khoảng (27.30s - 32.00s): "...lò xo có xu hướng giãn ra, tạo lực nhẹ để mở dần khoảng trống giữa các răng."
    {
        "file": "Scene3_Open_Coil_Creating_Space_3D.mp4",
        "src_start": 4500000,
        "src_dur": 4700000,
        "tgt_start": 27300000,
        "tgt_dur": 4700000,
        "scale": 2.4,
        "trans_x": 0.05,
        "trans_y": 0.0,
    },
    # 6. Khi đã có đủ chỗ, đưa răng lệch về vị trí (32.00s - 37.20s): "Khi đã có đủ chỗ, bác sĩ mới tiếp tục điều chỉnh để đưa chiếc răng lệch về vị trí mong muốn."
    {
        "file": "Scene1_Creating_Space_Impacted_Canine_Coil_Spring.mp4",
        "src_start": 14500000,
        "src_dur": 5200000,
        "tgt_start": 32000000,
        "tgt_dur": 5200000,
        "scale": 2.4,
        "trans_x": 0.10,
        "trans_y": 0.0,
    },
    # 7. Lời khuyên bác sĩ & Timelapse (37.20s - 41.133s): "Vậy nên đừng thấy bác sĩ cố tình đẩy hai răng ra xa mà lo lắng nhé."
    {
        "file": "Scene4_Moving_Canine_Braces_TimeLapse.mp4",
        "src_start": 1000000,
        "src_dur": 3933333,
        "tgt_start": 37200000,
        "tgt_dur": 3933333,
        "scale": 2.2,
        "trans_x": 0.0,
        "trans_y": 0.0,
    },
    # 8A. Câu kết Điểm nhấn Animation 3 bước - Bước 1: Răng thiếu chỗ (41.133s - 43.033s)
    {
        "file": "Scene1_Creating_Space_Impacted_Canine_Coil_Spring.mp4",
        "src_start": 9500000,
        "src_dur": 1900000,
        "tgt_start": 41133333,
        "tgt_dur": 1900000,
        "scale": 2.4,
        "trans_x": 0.10,
        "trans_y": 0.0,
    },
    # 8B. Câu kết Điểm nhấn Animation 3 bước - Bước 2: Lò xo tạo khoảng (43.033s - 44.933s)
    {
        "file": "Scene1_Creating_Space_Impacted_Canine_Coil_Spring.mp4",
        "src_start": 13200000,
        "src_dur": 1900000,
        "tgt_start": 43033333,
        "tgt_dur": 1900000,
        "scale": 2.4,
        "trans_x": 0.10,
        "trans_y": 0.0,
    },
    # 8C. Câu kết Điểm nhấn Animation 3 bước - Bước 3: Đưa răng vào hàng (44.933s - 46.833s)
    {
        "file": "Scene1_Creating_Space_Impacted_Canine_Coil_Spring.mp4",
        "src_start": 18200000,
        "src_dur": 1900000,
        "tgt_start": 44933333,
        "tgt_dur": 1900000,
        "scale": 2.4,
        "trans_x": 0.0,
        "trans_y": 0.0,
    },
]

video_segments = []
for idx, clip in enumerate(clips_plan):
    mat = video_mats[clip["file"]]
    mat_id = mat["id"]
    seg_id = str(uuid.uuid4()).upper()

    speed_id = str(uuid.uuid4()).upper()
    draft["materials"]["speeds"].append({"id": speed_id, "type": "speed", "mode": 0, "speed": 1.0, "curve_speed": None})

    placeholder_id = str(uuid.uuid4()).upper()
    draft["materials"]["placeholder_infos"].append({"id": placeholder_id, "type": "placeholder_info", "meta_type": "none", "res_path": "", "res_text": "", "error_path": "", "error_text": ""})

    canvas_id = str(uuid.uuid4()).upper()
    draft["materials"]["canvases"].append({"id": canvas_id, "type": "canvas_color", "color": "", "blur": 0.0, "image": "", "album_image": "", "image_id": "", "image_name": "", "source_platform": 0, "team_id": ""})

    sound_channel_id = str(uuid.uuid4()).upper()
    draft["materials"]["sound_channel_mappings"].append({"id": sound_channel_id, "type": "", "audio_channel_mapping": 0, "is_config_open": False})

    material_color_id = str(uuid.uuid4()).upper()
    draft["materials"]["material_colors"].append({"id": material_color_id, "is_color_clip": False, "is_gradient": False, "solid_color": "", "gradient_colors": [], "gradient_percents": [], "gradient_angle": 90.0, "width": 0.0, "height": 0.0})

    vocal_sep_id = str(uuid.uuid4()).upper()
    draft["materials"]["vocal_separations"].append({"id": vocal_sep_id, "type": "vocal_separation", "choice": 0, "removed_sounds": [], "time_range": None, "production_path": "", "final_algorithm": "", "enter_from": ""})

    video_segments.append({
        "id": seg_id,
        "source_timerange": {"start": clip["src_start"], "duration": clip["src_dur"]},
        "target_timerange": {"start": clip["tgt_start"], "duration": clip["tgt_dur"]},
        "render_timerange": {"start": 0, "duration": 0},
        "desc": "",
        "state": 0,
        "speed": 1.0,
        "is_loop": False,
        "is_tone_modify": False,
        "reverse": False,
        "intensifies_audio": False,
        "cartoon": False,
        "volume": 0.0,
        "last_nonzero_volume": 1.0,
        "clip": {
            "scale": {"x": clip["scale"], "y": clip["scale"]},
            "rotation": 0.0,
            "transform": {"x": clip["trans_x"], "y": clip["trans_y"]},
            "flip": {"vertical": False, "horizontal": False},
            "alpha": 1.0
        },
        "uniform_scale": {"on": True, "value": clip["scale"]},
        "material_id": mat_id,
        "extra_material_refs": [speed_id, placeholder_id, canvas_id, sound_channel_id, material_color_id, vocal_sep_id],
        "render_index": 0,
        "keyframe_refs": [],
        "enable_lut": True,
        "enable_adjust": True,
        "enable_hsl": True,
        "visible": True,
        "group_id": "",
        "enable_color_curves": True,
        "enable_hsl_curves": True,
        "track_render_index": 0,
        "hdr_settings": {"mode": 1, "intensity": 1.0, "nits": 1000},
        "enable_color_wheels": True,
        "track_attribute": 1,
        "is_placeholder": False,
        "template_id": "",
        "enable_smart_color_adjust": True,
        "template_scene": "default",
        "common_keyframes": [],
        "caption_info": None,
        "responsive_layout": {"enable": False, "target_follow": "", "size_layout": 0, "horizontal_pos_layout": 0, "vertical_pos_layout": 0},
        "enable_color_match_adjust": False,
        "enable_color_correct_adjust": False,
        "enable_adjust_mask": True,
        "raw_segment_id": "",
        "lyric_keyframes": None,
        "enable_video_mask": True,
        "digital_human_template_group_id": "",
        "color_correct_alg_result": "",
        "source": "segmentsourcenormal",
        "enable_mask_stroke": False,
        "enable_mask_shadow": False,
        "enable_color_adjust_pro": False
    })

track_video = {
    "attribute": 1,
    "flag": 0,
    "id": str(uuid.uuid4()).upper(),
    "is_default_name": True,
    "name": "",
    "segments": video_segments,
    "type": "video"
}

# ==============================================================================
# PART 3: TRACK 1 — HIGH KEY NHA KHOA COLOR ADJUSTMENT LAYER
# ==============================================================================
adjust_extra_refs = []
hsl_configs = [
    (3, 5, -18, 14, "#FFF2F224", "Yellows (Răng sứ: Khử ố vàng -18%, bắt sáng răng +14%)"),
    (2, -2, -4, 8, "#FFFFB044", "Oranges (Nền da sứ: Hồng đào, căng mọng dewy +8%)"),
    (1, 0, 10, 4, "#FFE64444", "Reds (Môi má: Tươi hồng tự nhiên +10%)")
]
for c_type, h_val, s_val, l_val, hex_col, lbl in hsl_configs:
    hsl_id = str(uuid.uuid4()).upper()
    draft["materials"]["hsl"].append({
        "id": hsl_id,
        "constant_material_id": str(uuid.uuid4()).upper(),
        "hsl_color_type": c_type,
        "hue": h_val,
        "saturation": s_val,
        "lightness": l_val,
        "interacting": False,
        "version": "1",
        "path": ADJUST_BUNDLE_PATH,
        "type": "hsl",
        "lumi_hub_path": LUMI_HUB_PATH,
        "custom_color": hex_col,
        "resource_id": "7501974767453474064",
        "source_platform": 1
    })
    adjust_extra_refs.append(hsl_id)

effect_sliders = [
    ("brightness", 0.05, "v2"),
    ("contrast", 0.22, "v3"),
    ("highlight", -0.18, "v3"),
    ("shadow", 0.02, "v3"),
    ("white", 0.12, "v1"),
    ("black", -0.14, "v1"),
    ("temperature", 0.03, "v3"),
    ("sharpen", 0.14, "v1"),
    ("clear", -0.04, "v1")
]
for eff_type, eff_val, ver in effect_sliders:
    eff_id = str(uuid.uuid4()).upper()
    draft["materials"]["effects"].append({
        "adjust_params": [],
        "algorithm_artifact_path": "",
        "apply_target_type": 0,
        "beauty_body_auto_preset_id": "",
        "beauty_face_auto_preset_id": "",
        "beauty_face_auto_retouch_info": {"beauty_face_auto_retouch_id": "", "face_id": []},
        "bloom_params": None,
        "category_id": "",
        "category_key": "",
        "category_name": "",
        "color_match_info": {"source_feature_path": "", "target_feature_path": "", "target_image_path": ""},
        "covering_relation_change": 0,
        "effect_id": "7501974767453474064",
        "enable_skin_tone_correction": False,
        "exclusion_group": [],
        "face_adjust_params": [],
        "formula_id": "",
        "id": eff_id,
        "intensity_key": "",
        "item_effect_type": 0,
        "lumi_hub_path": LUMI_HUB_PATH,
        "multi_language_current": "",
        "name": "",
        "panel_id": "",
        "path": ADJUST_BUNDLE_PATH,
        "platform": "all",
        "report_name": "",
        "request_id": "",
        "resource_id": "7501974767453474064",
        "smart_color_mode": 0,
        "source_platform": 1,
        "sub_category_id": "",
        "sub_category_name": "",
        "sub_type": "none",
        "third_resource_id": "",
        "time_range": None,
        "type": eff_type,
        "value": eff_val,
        "version": ver,
        "visible": True
    })
    adjust_extra_refs.append(eff_id)

smart_eff_id = str(uuid.uuid4()).upper()
draft["materials"]["effects"].append({
    "id": smart_eff_id,
    "effect_id": "7501974767453474064",
    "resource_id": "7501974767453474064",
    "third_resource_id": "",
    "name": "color-adjustment",
    "report_name": "",
    "type": "smart_color_adjust",
    "sub_type": "none",
    "path": ADJUST_BUNDLE_PATH,
    "value": 0.80,
    "visible": True,
    "item_effect_type": 0,
    "category_id": "",
    "category_name": "",
    "category_key": "",
    "sub_category_id": "",
    "sub_category_name": "",
    "platform": "all",
    "apply_target_type": 0,
    "source_platform": 1,
    "version": "",
    "adjust_params": [],
    "time_range": None,
    "formula_id": "",
    "enable_skin_tone_correction": True,
    "algorithm_artifact_path": "",
    "intensity_key": "",
    "face_adjust_params": [],
    "exclusion_group": [],
    "panel_id": "",
    "bloom_params": None,
    "request_id": "",
    "color_match_info": {"target_feature_path": "", "source_feature_path": "", "target_image_path": ""},
    "multi_language_current": "",
    "lumi_hub_path": LUMI_HUB_PATH,
    "covering_relation_change": 0,
    "beauty_face_auto_preset_id": "",
    "beauty_body_auto_preset_id": "",
    "beauty_face_auto_retouch_info": {"face_id": [], "beauty_face_auto_retouch_id": ""},
    "smart_color_mode": 0
})
adjust_extra_refs.append(smart_eff_id)

adj_placeholder_id = str(uuid.uuid4()).upper()
draft["materials"]["placeholders"].append({
    "id": adj_placeholder_id,
    "name": "Chỉnh màu: High Key Nha Khoa — Răng Trắng Sáng & Da Tươi Tắn",
    "type": "adjust",
    "material_resource_id": ""
})

adjust_segment = {
    "id": str(uuid.uuid4()).upper(),
    "source_timerange": None,
    "target_timerange": {"start": 0, "duration": TOTAL_DURATION_US},
    "render_timerange": {"start": 0, "duration": 0},
    "desc": "",
    "state": 0,
    "speed": 1.0,
    "is_loop": False,
    "is_tone_modify": False,
    "reverse": False,
    "intensifies_audio": False,
    "cartoon": False,
    "volume": 1.0,
    "last_nonzero_volume": 1.0,
    "clip": None,
    "uniform_scale": None,
    "material_id": adj_placeholder_id,
    "extra_material_refs": adjust_extra_refs,
    "render_index": 0,
    "keyframe_refs": [],
    "enable_lut": True,
    "enable_adjust": True,
    "enable_hsl": True,
    "visible": True,
    "group_id": "",
    "enable_color_curves": True,
    "enable_hsl_curves": True,
    "track_render_index": 1,
    "hdr_settings": None,
    "hdr_vivid_settings": None,
    "enable_color_wheels": True,
    "track_attribute": 0,
    "is_placeholder": False,
    "template_id": "",
    "enable_smart_color_adjust": True,
    "template_scene": "default",
    "common_keyframes": [],
    "caption_info": None,
    "responsive_layout": {"enable": False, "target_follow": "", "size_layout": 0, "horizontal_pos_layout": 0, "vertical_pos_layout": 0},
    "enable_color_match_adjust": False,
    "enable_color_correct_adjust": False,
    "enable_adjust_mask": True,
    "raw_segment_id": "",
    "lyric_keyframes": None,
    "enable_video_mask": True,
    "digital_human_template_group_id": "",
    "color_correct_alg_result": "",
    "source": "segmentsourcenormal",
    "enable_mask_stroke": False,
    "enable_mask_shadow": False,
    "enable_color_adjust_pro": False,
    "segment_color_tag": ""
}

track_adjust = {
    "attribute": 0,
    "flag": 0,
    "id": str(uuid.uuid4()).upper(),
    "is_default_name": False,
    "name": "Chỉnh màu: High Key Nha Khoa — Răng Trắng Sáng & Da Tươi Tắn",
    "segments": [adjust_segment],
    "type": "adjust"
}

# ==============================================================================
# PART 4: TRACK 2 (VOICEOVER) & TRACK 3 (BGM)
# ==============================================================================
voice_track = [t for t in draft["tracks"] if t["type"] == "audio"][0]

bgm_mat_id = str(uuid.uuid4()).upper()
draft["materials"]["audios"].append({
    "app_id": 0,
    "category_id": "",
    "category_name": "local",
    "check_flag": 1,
    "duration": TOTAL_DURATION_US,
    "effect_id": "",
    "formula_id": "",
    "id": bgm_mat_id,
    "intensifies_path": "",
    "local_material_id": str(uuid.uuid4()).lower(),
    "music_id": "",
    "name": "Short 01.20.mp3",
    "path": BGM_PATH.replace("\\", "/"),
    "query": "",
    "request_id": "",
    "resource_id": "",
    "search_id": "",
    "source_platform": 0,
    "team_id": "",
    "text_id": "",
    "tone_category_id": "",
    "tone_category_name": "",
    "tone_effect_id": "",
    "tone_effect_name": "",
    "tone_speaker": "",
    "tone_type": "",
    "type": "music",
    "video_id": "",
    "wave_points": []
})

bgm_fade_id = str(uuid.uuid4()).upper()
draft["materials"]["audio_fades"].append({
    "id": bgm_fade_id,
    "fade_in_duration": 1000000,
    "fade_out_duration": 2000000,
    "type": "audio_fade"
})

bgm_segment = {
    "id": str(uuid.uuid4()).upper(),
    "source_timerange": {"start": 0, "duration": TOTAL_DURATION_US},
    "target_timerange": {"start": 0, "duration": TOTAL_DURATION_US},
    "render_timerange": {"start": 0, "duration": 0},
    "desc": "",
    "state": 0,
    "speed": 1.0,
    "is_loop": False,
    "is_tone_modify": False,
    "reverse": False,
    "intensifies_audio": False,
    "cartoon": False,
    "volume": 0.18,
    "last_nonzero_volume": 1.0,
    "clip": None,
    "uniform_scale": None,
    "material_id": bgm_mat_id,
    "extra_material_refs": [bgm_fade_id],
    "render_index": 0,
    "keyframe_refs": [],
    "enable_lut": False,
    "enable_adjust": False,
    "enable_hsl": False,
    "visible": True,
    "group_id": "",
    "enable_color_curves": True,
    "enable_hsl_curves": True,
    "track_render_index": 0,
    "hdr_settings": None,
    "hdr_vivid_settings": None,
    "enable_color_wheels": True,
    "track_attribute": 0,
    "is_placeholder": False,
    "template_id": "",
    "enable_smart_color_adjust": False,
    "template_scene": "default",
    "common_keyframes": [],
    "caption_info": None,
    "responsive_layout": {"enable": False, "target_follow": "", "size_layout": 0, "horizontal_pos_layout": 0, "vertical_pos_layout": 0},
    "enable_color_match_adjust": False,
    "enable_color_correct_adjust": False,
    "enable_adjust_mask": False,
    "raw_segment_id": "",
    "lyric_keyframes": None,
    "enable_video_mask": True,
    "digital_human_template_group_id": "",
    "color_correct_alg_result": "",
    "source": "segmentsourcenormal",
    "enable_mask_stroke": False,
    "enable_mask_shadow": False,
    "enable_color_adjust_pro": False,
    "segment_color_tag": ""
}

track_bgm = {
    "attribute": 0,
    "flag": 0,
    "id": str(uuid.uuid4()).upper(),
    "is_default_name": False,
    "name": "BGM (Corporate Upbeat)",
    "segments": [bgm_segment],
    "type": "audio"
}

# ==============================================================================
# PART 5: TRACK 4 — STICKER EMPHASIS IN HOOK (0.80s -> 4.50s)
# ==============================================================================
sticker_mat_id = str(uuid.uuid4()).upper()
sticker_speed_id = str(uuid.uuid4()).upper()
draft["materials"]["speeds"].append({"id": sticker_speed_id, "type": "speed", "mode": 0, "speed": 1.0, "curve_speed": None})

draft["materials"]["stickers"].append({
    "id": sticker_mat_id,
    "unique_id": "",
    "type": "sticker",
    "path": "C:/Users/PC/AppData/Local/CapCut/User Data/Cache/artistEffect/7496729827391606069/9afb22b9ed4215179bd4f63c0716b0c1",
    "icon_url": "",
    "preview_cover_url": "",
    "sticker_id": "7496729827391606069",
    "resource_id": "7496729827391606069",
    "name": "Emphasis Stickers Circle & Arrow EN",
    "category_id": "1212",
    "category_name": "Trending",
    "platform": "all",
    "unicode": "",
    "source_platform": 1,
    "formula_id": "",
    "check_flag": 1,
    "team_id": "",
    "request_id": "",
    "combo_info": {"text_templates": []},
    "sub_type": 0,
    "radius": {"top_left": 0.0, "top_right": 0.0, "bottom_left": 0.0, "bottom_right": 0.0},
    "global_alpha": 1.0,
    "background_color": "",
    "background_alpha": 1.0,
    "border_line_style": 0,
    "border_width": 0.0,
    "border_color": "",
    "has_shadow": False,
    "shadow_color": "",
    "shadow_alpha": 0.8,
    "shadow_smoothing": 0.0,
    "shadow_distance": 0.0,
    "shadow_point": {"x": 0.0, "y": 0.0},
    "shadow_angle": 0.0,
    "shape_param": {"shape_type": 0, "roundness": [], "custom_points": [], "shape_size": []},
    "original_size": [280, 280],
    "update_params": "",
    "aigc_type": "none",
    "sequence_type": False,
    "cycle_setting": True,
    "shape_fill_render_style": {
        "color": {
            "solid": {"color": "#FFFFFF", "alpha": 1.0},
            "gradient": {"color": [], "alpha": [], "percent": [], "angle": 90.0, "mode": "all", "style": "linear"},
            "texture": {"path": "", "flip": [], "scale": 1.0, "alpha": 1.0, "angle": 90.0, "blend": "no", "range": 4, "fill": "tile", "resource_id": "", "effect_id": "", "play_speed": 1.0},
            "render_type": "solid"
        },
        "alpha": 1.0
    },
    "shape_fill_use_flower_color": False,
    "multi_language_current": "none",
    "corner_pin": None
})

sticker_seg = {
    "id": str(uuid.uuid4()).upper(),
    "source_timerange": None,
    "target_timerange": {"start": 800000, "duration": 3700000},
    "render_timerange": {"start": 0, "duration": 0},
    "desc": "",
    "state": 0,
    "speed": 1.0,
    "is_loop": False,
    "is_tone_modify": False,
    "reverse": False,
    "intensifies_audio": False,
    "cartoon": False,
    "volume": 1.0,
    "last_nonzero_volume": 1.0,
    "clip": {
        "scale": {"x": 0.85, "y": 0.85},
        "rotation": 0.0,
        "transform": {"x": 0.02, "y": -0.04},
        "flip": {"vertical": False, "horizontal": False},
        "alpha": 1.0
    },
    "uniform_scale": {"on": True, "value": 0.85},
    "material_id": sticker_mat_id,
    "extra_material_refs": [sticker_speed_id],
    "render_index": 13500,
    "keyframe_refs": [],
    "enable_lut": False,
    "enable_adjust": False,
    "enable_hsl": False,
    "visible": True,
    "group_id": "",
    "enable_color_curves": True,
    "enable_hsl_curves": True,
    "track_render_index": 3,
    "hdr_settings": None,
    "enable_color_wheels": True,
    "track_attribute": 0,
    "is_placeholder": False,
    "template_id": "",
    "enable_smart_color_adjust": False,
    "template_scene": "default",
    "common_keyframes": [],
    "caption_info": None,
    "responsive_layout": {"enable": False, "target_follow": "", "size_layout": 0, "horizontal_pos_layout": 0, "vertical_pos_layout": 0},
    "enable_color_match_adjust": False,
    "enable_color_correct_adjust": False,
    "enable_adjust_mask": False,
    "raw_segment_id": "",
    "lyric_keyframes": None,
    "enable_video_mask": True,
    "digital_human_template_group_id": "",
    "color_correct_alg_result": "",
    "source": "segmentsourcenormal",
    "enable_mask_stroke": False,
    "enable_mask_shadow": False,
    "enable_color_adjust_pro": False
}

track_sticker = {
    "attribute": 0,
    "flag": 0,
    "id": str(uuid.uuid4()).upper(),
    "is_default_name": False,
    "name": "Sticker Nhấn Mạnh Lò Xo",
    "segments": [sticker_seg],
    "type": "sticker"
}

# ==============================================================================
# PART 6: TRACK 5 — TEXT CALLOUT OVERLAY (CƠ CHẾ & 3 BƯỚC CUỐI VIDEO)
# ==============================================================================
callouts_spec = [
    ("⚡ LÒ XO GIÃN MỞ KHOẢNG TRỐNG", 27300000, 4700000, [0.0, 0.9, 1.0], "#00E5FF"),
    ("1️⃣ BƯỚC 1: RĂNG THIẾU CHỖ", 41133333, 1900000, [1.0, 0.88, 0.0], "#FFE600"),
    ("2️⃣ BƯỚC 2: LÒ XO TẠO KHOẢNG", 43033333, 1900000, [0.0, 0.9, 1.0], "#00E5FF"),
    ("3️⃣ BƯỚC 3: ĐƯA RĂNG VÀO HÀNG", 44933333, 1900000, [0.2, 1.0, 0.6], "#33FF99"),
]

callout_segments = []
for c_idx, (c_text, c_start, c_dur, rgb_col, hex_col) in enumerate(callouts_spec):
    c_style = [{
        "fill": {"content": {"render_type": "solid", "solid": {"color": rgb_col}}},
        "font": {"id": "", "path": FONT_PATH},
        "range": [0, len(c_text)],
        "size": 8.5,
        "strokes": [{"content": {"render_type": "solid", "solid": {"color": [0.0, 0.0, 0.0]}}, "width": 0.12}]
    }]
    c_content_json = json.dumps({"text": c_text, "styles": c_style}, ensure_ascii=False)
    c_mat_id = str(uuid.uuid4()).upper()
    draft["materials"]["texts"].append({
        "recognize_task_id": "",
        "id": c_mat_id,
        "name": "",
        "recognize_text": c_text,
        "recognize_model": "",
        "punc_model": "",
        "type": "text",
        "content": c_content_json,
        "base_content": c_content_json,
        "words": {"start_time": [], "end_time": [], "text": []},
        "current_words": {"start_time": [], "end_time": [], "text": []},
        "global_alpha": 1.0,
        "combo_info": {"text_templates": []},
        "caption_template_info": {"resource_id": "", "third_resource_id": "", "resource_name": "", "category_id": "", "category_name": "", "effect_id": "", "request_id": "", "path": "", "is_new": False, "source_platform": 0},
        "layer_weight": 2,
        "letter_spacing": 0.02,
        "text_curve": None,
        "text_loop_on_path": False,
        "offset_on_path": 0.0,
        "enable_path_typesetting": False,
        "text_exceeds_path_process_type": 0,
        "text_typesetting_paths": None,
        "text_typesetting_paths_file": "",
        "text_typesetting_path_index": 0,
        "line_spacing": 0.02,
        "has_shadow": True,
        "shadow_color": "#000000",
        "shadow_alpha": 0.8,
        "shadow_smoothing": 0.5,
        "shadow_distance": 5.0,
        "shadow_point": {"x": 0.636, "y": -0.636},
        "shadow_angle": -45.0,
        "shadow_thickness_projection_enable": False,
        "shadow_thickness_projection_angle": 0.0,
        "shadow_thickness_projection_distance": 0.0,
        "border_alpha": 1.0,
        "border_color": "#000000",
        "border_width": 0.12,
        "border_mode": 0,
        "style_name": "",
        "text_color": hex_col,
        "text_alpha": 1.0,
        "font_name": "",
        "font_title": "none",
        "font_size": 8.5,
        "font_path": FONT_PATH,
        "font_id": "",
        "font_resource_id": "",
        "initial_scale": 1.0,
        "font_url": "",
        "typesetting": 0,
        "alignment": 1,
        "line_feed": 1,
        "use_effect_default_color": False,
        "is_rich_text": False,
        "shape_clip_x": False,
        "shape_clip_y": False,
        "ktv_color": "",
        "text_to_audio_ids": [],
        "bold_width": 0.0,
        "italic_degree": 0,
        "underline": False,
        "underline_width": 0.05,
        "underline_offset": 0.22,
        "sub_type": 0,
        "check_flag": 7,
        "text_size": 30,
        "font_category_name": "",
        "font_source_platform": 0,
        "font_third_resource_id": "",
        "font_category_id": "",
        "add_type": 1,
        "operation_type": 0,
        "recognize_type": 0,
        "fonts": [],
        "background_color": "#081428",
        "background_alpha": 0.85,
        "background_style": 0,
        "background_round_radius": 0.35,
        "background_width": 0.22,
        "background_height": 0.22,
        "background_vertical_offset": 0.0,
        "background_horizontal_offset": 0.0,
        "background_fill": "",
        "single_char_bg_enable": False,
        "single_char_bg_color": "",
        "single_char_bg_alpha": 1.0,
        "single_char_bg_round_radius": 0.3,
        "single_char_bg_width": 0.0,
        "single_char_bg_height": 0.0,
        "single_char_bg_vertical_offset": 0.0,
        "single_char_bg_horizontal_offset": 0.0,
        "font_team_id": "",
        "tts_auto_update": False,
        "text_preset_resource_id": "",
        "group_id": "",
        "preset_id": "",
        "preset_name": "",
        "preset_category": "",
        "preset_category_id": "",
        "preset_index": 0,
        "preset_has_set_alignment": False,
        "force_apply_line_max_width": False,
        "language": "",
        "relevance_segment": [],
        "original_size": [],
        "fixed_width": -1.0,
        "fixed_height": -1.0,
        "autoAdaptCanvasEnabled": False,
        "line_max_width": 0.85,
        "oneline_cutoff": False,
        "cutoff_postfix": "",
        "subtitle_template_original_fontsize": 0.0,
        "subtitle_keywords": {"range": []},
        "inner_padding": -1.0,
        "multi_language_current": "none",
        "source_from": "",
        "is_lyric_effect": False,
        "lyric_group_id": "",
        "lyrics_template": {"resource_id": "", "resource_name": "", "panel": "", "effect_id": "", "path": "", "category_id": "", "category_name": "", "request_id": ""},
        "is_batch_replace": False,
        "is_words_linear": False,
        "ssml_content": "",
        "subtitle_keywords_config": None,
        "sub_template_id": -1,
        "translate_original_text": "",
        "adjust_params": []
    })

    c_anim_id = str(uuid.uuid4()).upper()
    draft["materials"]["material_animations"].append({
        "id": c_anim_id,
        "type": "sticker_animation",
        "animations": [{
            "id": ANIM_POP_UP_IN_ID,
            "type": "in",
            "start": 0,
            "duration": 250000,
            "path": ANIM_POP_UP_IN_PATH,
            "platform": "all",
            "resource_id": ANIM_POP_UP_IN_ID,
            "third_resource_id": "0",
            "source_platform": 1,
            "name": "Pop Up In",
            "category_id": "ruchang_fav",
            "category_name": "Favorites",
            "panel": "",
            "material_type": "sticker",
            "anim_adjust_params": None,
            "request_id": ""
        }],
        "multi_language_current": "none"
    })

    callout_segments.append({
        "id": str(uuid.uuid4()).upper(),
        "source_timerange": None,
        "target_timerange": {"start": c_start, "duration": c_dur},
        "render_timerange": {"start": 0, "duration": 0},
        "desc": "",
        "state": 0,
        "speed": 1.0,
        "is_loop": False,
        "is_tone_modify": False,
        "reverse": False,
        "intensifies_audio": False,
        "cartoon": False,
        "volume": 1.0,
        "last_nonzero_volume": 1.0,
        "clip": {
            "scale": {"x": 1.0, "y": 1.0},
            "rotation": 0.0,
            "rotation3d": [],
            "transform": {"x": 0.0, "y": 0.42},
            "flip": {"vertical": False, "horizontal": False},
            "alpha": 1.0
        },
        "uniform_scale": {"on": True, "value": 1.0},
        "material_id": c_mat_id,
        "extra_material_refs": [c_anim_id],
        "render_index": 20000 + c_idx,
        "keyframe_refs": [],
        "enable_lut": False,
        "enable_adjust": False,
        "enable_hsl": False,
        "visible": True,
        "group_id": "",
        "enable_color_curves": True,
        "enable_hsl_curves": True,
        "track_render_index": 4,
        "hdr_settings": None,
        "hdr_vivid_settings": None,
        "enable_color_wheels": True,
        "track_attribute": 0,
        "is_placeholder": False,
        "template_id": "",
        "enable_smart_color_adjust": False,
        "template_scene": "default",
        "common_keyframes": [],
        "caption_info": None,
        "responsive_layout": {"enable": False, "target_follow": "", "size_layout": 0, "horizontal_pos_layout": 0, "vertical_pos_layout": 0},
        "enable_color_match_adjust": False,
        "enable_color_correct_adjust": False,
        "enable_adjust_mask": False,
        "raw_segment_id": "",
        "lyric_keyframes": None,
        "enable_video_mask": True,
        "digital_human_template_group_id": "",
        "color_correct_alg_result": "",
        "source": "segmentsourcenormal",
        "enable_mask_stroke": False,
        "enable_mask_shadow": False,
        "enable_color_adjust_pro": False,
        "segment_color_tag": ""
    })

track_callout = {
    "attribute": 0,
    "flag": 0,
    "id": str(uuid.uuid4()).upper(),
    "is_default_name": False,
    "name": "Text Callout Overlay (3 Bước)",
    "segments": callout_segments,
    "type": "text"
}

track_subtitles = {
    "attribute": 0,
    "flag": 1,
    "id": str(uuid.uuid4()).upper(),
    "is_default_name": False,
    "name": "Subtitles Karaoke (1 Line)",
    "segments": subtitle_segments,
    "type": "text"
}

# Assemble all 7 tracks cleanly
draft["tracks"] = [
    track_video,
    track_adjust,
    voice_track,
    track_bgm,
    track_sticker,
    track_callout,
    track_subtitles
]

draft["duration"] = TOTAL_DURATION_US

with open(DRAFT_PATH, "w", encoding="utf-8") as f:
    json.dump(draft, f, ensure_ascii=False, indent=2)
print("SUCCESS: Saved draft_content.json with all 7 tracks!")

now_us = int(time.time() * 1000000)
if os.path.exists(META_PATH):
    with open(META_PATH, "r", encoding="utf-8") as f:
        mdata = json.load(f)
    mdata["tm_draft_modified"] = now_us
    mdata["tm_duration"] = TOTAL_DURATION_US
    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump(mdata, f, ensure_ascii=False, indent=2)
    print("SUCCESS: Updated draft_meta_info.json!")

if os.path.exists(ROOT_META_PATH):
    try:
        with open(ROOT_META_PATH, "r", encoding="utf-8") as f:
            root_data = json.load(f)
        for d in root_data.get("all_draft_store", []):
            if d.get("draft_name") == PROJECT_NAME:
                d["tm_draft_modified"] = now_us
                d["tm_duration"] = TOTAL_DURATION_US
                break
        with open(ROOT_META_PATH, "w", encoding="utf-8") as f:
            json.dump(root_data, f, ensure_ascii=False, indent=2)
        print("SUCCESS: Updated root_meta_info.json!")
    except Exception as e:
        print(f"Warning updating root_meta_info.json: {e}")
