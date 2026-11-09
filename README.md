# CapCut PC Automation & HMMC TikTok Style Skill

Bộ Skill tự động hóa dựng video **CapCut Desktop (Windows)** theo chuẩn **HMMC Short-Form TikTok Style (`9:16`)**, bao gồm:
- Tự động phân tích kịch bản, tải footage lâm sàng / 3D animation khớp nội dung từng câu voiceover.
- Tự động dựng Timeline **7 Track** chuẩn nha khoa (`Video`, `High-Key Dental Color Grading`, `Voiceover`, `BGM`, `Sticker`, `POV Title & Callout`, `1-Line Karaoke Subtitles`).
- Tự động tạo **Phụ đề Karaoke 1 Dòng Chuẩn TikTok Safezone** (`SVN-Gilroy SemiBold` cỡ `9.5`, tọa độ `Y = -0.42`, Vàng Gold `#FFE600` / Trắng `#FFFFFF`, hiệu ứng `ART EN CHALK M7` + `Pop Up In` ở từ đầu cụm, `0ms` overlap).
- Tự động xuất **2 phiên bản chất lượng cao nhất**:
  1. **Master 4K 60fps (`2160×3840`, `Higher Bitrate ~43.8 Mbps`, `Rec.709 SDR`)** từ CapCut Native Engine.
  2. **TikTok 1080p 60fps Anti-Compression (`1080×1920`, `Lanczos + Unsharp Micro-Contrast`, `H.264 High@L4.2 CRF 15`, `AAC 320kbps`, `+faststart`)** chống vỡ/mờ chữ khi tải lên TikTok.

## Cấu trúc thư mục

- [`SKILL.md`](./SKILL.md) — Tài liệu hướng dẫn chi tiết cho AI Agent (Antigravity / Claude Code / Cursor).
- [`scripts/capcut_bridge.py`](./scripts/capcut_bridge.py) — Thư viện Python kết nối và thao tác trực tiếp với cấu trúc `draft_content.json` của CapCut PC.
- [`scripts/build_hmmc_template.py`](./scripts/build_hmmc_template.py) — Script mẫu dựng tự động hoàn chỉnh 7 track chuẩn HMMC từ voiceover và footage.
- [`scripts/export_capcut_tiktok.py`](./scripts/export_capcut_tiktok.py) — Script tự động điều khiển CapCut PC xuất Master 4K60 và tối ưu hóa 1080p60 chống nén TikTok.

## Cài đặt vào Antigravity

Copy thư mục này vào đường dẫn Global Skills của Antigravity:
```powershell
git clone https://github.com/ghostk12081995-stack/capcut-pc-hmmc-skill.git "$HOME\.gemini\config\skills\capcut-pc"
```
