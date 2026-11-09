---
name: capcut-pc
description: Automate CapCut Desktop (PC) on Windows — including the HMMC Dental TikTok Short-Form Style (7-track timeline, 1-line Safezone Karaoke subtitles, POV hook title, clinical footage sourcing & timestamp matching, High-Key Dental color adjustment, and 4K60 + 1080p60 Lanczos Anti-Compression TikTok export).
---

# CapCut PC Automation & HMMC TikTok Style Skill

Dùng skill này khi người dùng yêu cầu tạo video, dựng clip tự động, tạo phụ đề Karaoke 1 dòng chuẩn Safezone, hoặc xuất video chất lượng cao nhất trên **CapCut Desktop (Windows)**.

## 1. Đường dẫn hệ thống & Thư viện

- **Core Bridge Module:** `C:/Users/PC/.gemini/antigravity/scratch/CapCutAutomation/capcut_bridge.py`
- **HMMC Complete Builder Reference:** `C:/Users/PC/.gemini/config/skills/capcut-pc/scripts/build_hmmc_template.py`
- **CapCut Active Drafts (Primary):** `C:/Users/PC/AppData/Local/CapCut Drafts/<Ten_Du_An>`
  - Lưu ý: Nếu dự án có thư mục con `Timelines/<UUID>/draft_content.json`, phải đồng bộ cả file gốc lẫn file trong `Timelines/<UUID>/`.
- **CapCut Legacy Drafts (Secondary):** `C:/Users/PC/AppData/Local/CapCut/User Data/Projects/com.lveditor.draft/<Ten_Du_An>`
- **Quy tắc bảo toàn chỉnh sửa của người dùng (CRITICAL):**
  - Trước khi ghi đè `draft_content.json`, luôn kiểm tra `LastWriteTime`. Nếu người dùng vừa chỉnh sửa thủ công trên CapCut Desktop (thay clip hook, thêm tiêu đề POV, tinh chỉnh vị trí), tuyệt đối giữ nguyên các thay đổi đó.

---

## 2. Cấu trúc 7 Track Chuẩn Style HMMC (TikTok Nha Khoa / Kiến Thức 9:16)

Mọi tài nguyên tải về (footage, nhạc, SRT, file xuất) phải gom gọn vào **1 thư mục duy nhất** của dự án, ví dụ: `D:\Hoàng\Tháng 11\<YYMMDD HMMC TXX>`.

| Thứ tự | Track | Nội dung & Thông số chuẩn |
| :--- | :--- | :--- |
| **Track 1** | **Video (Main)** | Khung dọc `1080×1920` (hoặc `2160×3840`), `volume = 0.0` (tắt tiếng gốc).<br>• **Hook `[0.0s – 1.03s]`:** Cắt cảnh thực tế bác sĩ tại phòng khám (`DJI_*.MP4`) kết hợp tiêu đề POV.<br>• **Body:** Các cảnh cận lâm sàng / 3D animation khớp chính xác theo nội dung từng file voice (`source_start_sec` đã kiểm tra qua contact sheet, không lấy nhầm đoạn intro/outro).<br>• `scale = 1.88` (hoặc tự động lấp đầy khung dọc 9:16, che watermark góc nếu có). |
| **Track 2** | **Adjustment Layer** | Phủ toàn bộ thời lượng video (`High-Key Dental Clean`):<br>• Brightness `+6%`, Contrast `+8%`, Highlight `+10%`, Saturation `-5%`, Temp `-4%` (trắng lạnh nha khoa), Vignette `-5%`, Sharpen `+18%`. |
| **Track 3** | **Voiceover Audio** | Ghép nối tuần tự các file `1.wav` → `N.wav` trong thư mục `voice TXX`, cách nhau `0.18s` nhịp thở tự nhiên, `volume = 1.0`. |
| **Track 4** | **BGM Audio** | Nhạc nền (`Short 01.20.mp3`) phủ hết timeline, hạ nền `volume = 0.13` (`-17.7 dB`) dưới giọng đọc, `fade_out = 1.5s` ở cuối. |
| **Track 5** | **Sticker / Arrow** | Sticker mũi tên chỉ điểm cơ học (ví dụ: vị trí lò xo đẩy mở khoảng), `scale = 0.35`, animation `Pop Up In`. |
| **Track 6** | **POV Hook & Callout** | • **POV Banner đầu video / xuyên suốt:** Đặt ở vùng an toàn phía trên (`transform.y = +0.52` hoặc `+0.42`), ví dụ: `"POV: Niềng để răng đều\nsao bác sĩ lại đẩy hai răng ra xa?"`.<br>• **Text Callout giải thích cơ chế / 3 bước tổng kết:** Đặt tại `transform.y = +0.42`, cỡ chữ `11.0`, chữ Vàng Gold viền đen + nền mờ. |
| **Track 7** | **Subtitles Karaoke 1 Line** | Phụ đề chạy từng từ (Word-by-word Karaoke) nằm trên **1 dòng duy nhất** trong vùng TikTok Safezone. |

---

## 3. Quy chuẩn Phụ đề Karaoke 1 Dòng Chuẩn Safezone (TikTok / Shorts / Reels)

### 3.1. Giới hạn độ dài (Single-Line Constraint)
- **Số từ mỗi cụm (chunk):** `2 – 5 từ` (tối đa không quá 6 từ ngắn).
- **Độ dài ký tự:** `10 – 25 ký tự` (tuyệt đối $\le 25$ ký tự, ngắt cụm tại dấu câu `, . ? ! ; :`).
- **Mục tiêu:** 100% hiển thị trên **1 dòng duy nhất**, không bao giờ bị rớt dòng tự động trên khung hình dọc `9:16`.

### 3.2. Tọa độ Safezone (Vùng an toàn)
- `transform.x = 0.0` (Căn chính giữa màn hình).
- `transform.y = -0.42` (Tương đương pixel $Y \approx 1363\text{px}$ từ đỉnh màn hình `1080×1920`):
  - Nằm hoàn toàn trong vùng trong suốt của template TikTok Safezone (`Y: 115px – 1544px`).
  - Cách thanh caption/sound đỏ ở đáy $> 140\text{px}$.
  - Tránh cụm icon tương tác thả tim/comment bên phải (`X: 886 – 1019`) với khoảng hở an toàn $> 60\text{px}$.

### 3.3. Phong cách hiển thị (Styling & Animation)
- **Font chữ:** `SVN-Gilroy SemiBold` (`C:/Users/PC/AppData/Local/Microsoft/Windows/Fonts/SVN-Gilroy SemiBold.otf`), cỡ chữ `9.5` – `10.0`.
- **Hiệu ứng chữ:** `ART EN CHALK M7 - Chalk With Background` (`effect_id = 7528350137333189941`) + Viền đen (`stroke: #000000`, `width: 0.08`).
- **Màu sắc Karaoke:**
  - Từ đang đọc (**Active**): Vàng Gold sáng `#FFE600` (`[1.0, 0.9, 0.0]`).
  - Các từ còn lại trong cụm (**Inactive**): Trắng `#FFFFFF` (`[1.0, 1.0, 1.0]`).
- **Hiệu ứng chuyển cụm:**
  - Animation vào: `Pop Up In` (`7646374911761452306`, thời lượng `250000` µs) chỉ áp dụng cho **từ đầu tiên** của mỗi cụm.
  - Các từ tiếp theo trong cụm: Animation rỗng để text giữ nguyên vị trí, chỉ đổi màu highlight theo từng từ mà không bị giật/nháy.

### 3.4. Xử lý Timecode & Gap Bridging
- Dùng `faster-whisper` (`model="small"` hoặc `"medium"`, `language="vi"`, `word_timestamps=True`) để lấy timestamp chính xác từng từ từ các file `.wav`.
- **Không chồng chéo:** `seg_duration = seg_end - seg_start` đảm bảo `0 µs` overlap giữa các từ.
- **Cầu nối khoảng nghỉ:** Nếu khoảng cách giữa 2 cụm liên tiếp $< 0.25\text{s}$, tự động kéo dài từ cuối của cụm trước chạm vào đầu cụm sau để phụ đề không bị chớp tắt.

---

## 4. Quy trình Xuất Video Nét Nhất Cho TikTok (2 Phiên Bản)

Khi người dùng yêu cầu **export video nét và chất lượng nhất để up TikTok**, thực hiện quy trình 2 bước sau và lưu vào thư mục `<ProjectFolder>\ex\`:

### Bước 1: Xuất Bản Master 4K 60fps Trực Tiếp Từ CapCut Native Engine
Tại sao phải xuất từ CapCut trước? Vì chỉ engine render nội bộ của CapCut mới vẽ đúng shader hiệu ứng chữ `.effect` (`ART EN CHALK M7`), animation `Pop Up In` và lớp chỉnh màu `lumi_hub_path`.

1. Cập nhật Registry đường dẫn xuất:
   - Key: `HKCU\Software\Bytedance\CapCut\Modules\Export`
   - `ExportPath` = `D:/Hoàng/Tháng 11/<Ten_Du_An>/ex`
2. Điều khiển cửa sổ CapCut trên Interactive Desktop (`WinSta0\Default`):
   - Lưu ý kỹ thuật: Shell sandboxed mặc định không nhìn thấy GUI. Phải gọi script Python qua `Invoke-CimMethod -ClassName Win32_Process -MethodName Create` với `pythonw.exe`.
   - Dùng `SetWindowPos(hwnd, HWND_TOPMOST, ...)` + `AttachThreadInput` + `SetForegroundWindow` để đưa cửa sổ CapCut (`Qt622QWindowIcon`) lên trên cùng.
   - Dùng `mouse_event(0x8001, norm_x, norm_y, 0, 0)` (`MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE`) trước khi click để Qt6 QML nhận diện đúng trạng thái hover.
   - Thông số hộp thoại Export:
     - **Resolution:** `4K` (`2160×3840`)
     - **Bit rate:** `Higher` (~`43.8 Mbps`)
     - **Codec:** `H.264`
     - **Format:** `mp4`
     - **Frame rate:** `60fps`
     - **Color space:** `Rec. 709 SDR`

### Bước 2: Tạo Bản Chuẩn TikTok 1080p 60fps Chống Nén (Lanczos + Unsharp)
Server TikTok sẽ tự động ép giảm độ phân giải mọi video $> 1080\times 1920$ bằng bộ lọc nhanh làm bệt chữ và chi tiết mắc cài. Do đó, từ file 4K Master vừa xuất, chạy FFmpeg để tạo thêm bản `1080p60` tối ưu hóa:

```powershell
ffmpeg -y -i "<ProjectFolder>\ex\<Ten_Du_An>.mp4" `
  -vf "scale=1080:1920:flags=lanczos,unsharp=3:3:0.35:3:3:0.0" `
  -c:v libx264 -profile:v high -level:v 4.2 -pix_fmt yuv420p `
  -preset fast -crf 15 -maxrate 20M -bufsize 40M `
  -color_primaries bt709 -color_trc bt709 -colorspace bt709 `
  -c:a aac -b:a 320k -ar 48000 -movflags +faststart `
  "<ProjectFolder>\ex\<Ten_Du_An>_TikTok_1080p60_Sharp.mp4"
```
