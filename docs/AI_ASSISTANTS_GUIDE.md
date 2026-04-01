# Hướng dẫn AI Assistants cho MediSign AI

## Tổng quan

Dự án MediSign AI hỗ trợ nhiều AI coding assistants khác nhau. Mỗi AI có cấu trúc thư mục riêng để lưu trữ skills và workflows.

## Bảng so sánh AI Assistants

| AI Assistant | Thư mục | Skills | Workflows/Commands | Format | Ghi chú |
|-------------|---------|--------|-------------------|--------|---------|
| **Kiro** | `.kiro/` | ✅ 10 skills | ✅ 10 workflows (.md) | Markdown | Đang sử dụng |
| **Windsurf** | `.windsurf/` | ✅ 10 skills | ✅ 10 workflows (.md) | Markdown | - |
| **VibeCode** | `.vibecode/` | ✅ 10 skills | ✅ 10 workflows (.md) | Markdown | - |
| **Kilocode** | `.kilocode/` | ✅ 10 skills | ✅ 10 workflows (.md) | Markdown | Tên cũ của Kiro |
| **Agent (Generic)** | `.agent/` | ✅ 10 skills | ✅ 10 workflows (.md) | Markdown | Cho các AI chung |
| **Cursor** | `.cursor/` | ✅ 10 skills | ✅ 10 commands (.md) | Markdown | Dùng "commands" thay vì "workflows" |
| **Codex** | `.codex/` | ✅ 10 skills | ❌ | Markdown | Chỉ có skills |
| **Gemini** | `.gemini/` | ✅ 10 skills | ✅ 10 commands (.toml) | TOML | Format khác biệt |

## Cấu trúc thư mục chuẩn

```
.<ai-name>/
├── skills/                    # Thư mục chứa skills
│   ├── openspec-new-change/
│   │   └── SKILL.md          # Định nghĩa skill
│   ├── openspec-continue-change/
│   │   └── SKILL.md
│   └── ...
└── workflows/                 # Thư mục chứa workflows (hoặc commands)
    ├── opsx-new.md
    ├── opsx-continue.md
    └── ...
```

## 10 OpenSpec Skills có sẵn

| # | Skill Name | Mô tả | Khi nào dùng |
|---|-----------|-------|--------------|
| 1 | **openspec-new-change** | Tạo change mới | Bắt đầu feature/fix mới |
| 2 | **openspec-continue-change** | Tiếp tục change đang làm | Làm tiếp artifact tiếp theo |
| 3 | **openspec-apply-change** | Apply change vào codebase | Implement code từ change |
| 4 | **openspec-verify-change** | Verify change đã hoàn thành | Kiểm tra trước khi archive |
| 5 | **openspec-archive-change** | Archive change đã xong | Dọn dẹp sau khi hoàn thành |
| 6 | **openspec-bulk-archive-change** | Archive nhiều changes cùng lúc | Dọn dẹp hàng loạt |
| 7 | **openspec-ff-change** | Fast-forward change | Bỏ qua artifacts không cần |
| 8 | **openspec-explore** | Khám phá changes hiện có | Xem danh sách changes |
| 9 | **openspec-sync-specs** | Đồng bộ specs | Cập nhật specs từ delta |
| 10 | **openspec-onboard** | Onboard vào OpenSpec | Setup ban đầu |

## Workflow chuẩn cho Kiro

### Khi bắt đầu session mới

1. **Đọc context dự án**
   ```
   - README.md (hiểu tổng quan dự án)
   - docs/AI_ASSISTANTS_GUIDE.md (tài liệu này)
   ```

2. **Kiểm tra active changes**
   ```bash
   openspec list --json
   ```

3. **Nếu có change đang làm dở**
   - Đọc `.kiro/skills/openspec-continue-change/SKILL.md`
   - Đọc `.kiro/workflows/opsx-continue.md`
   - Tiếp tục theo workflow

4. **Nếu bắt đầu change mới**
   - Đọc `.kiro/skills/openspec-new-change/SKILL.md`
   - Đọc `.kiro/workflows/opsx-new.md`
   - Tạo change theo workflow

### Quy trình làm việc với OpenSpec

```
1. NEW → Tạo change mới
   ↓
2. CONTINUE → Làm từng artifact
   ↓
3. APPLY → Implement code
   ↓
4. VERIFY → Kiểm tra
   ↓
5. ARCHIVE → Hoàn thành
```

## Sự khác biệt giữa các AI

### Format Skills
- **Giống nhau**: Tất cả đều dùng `SKILL.md` với YAML frontmatter
- **Nội dung**: Hoàn toàn giống nhau

### Format Workflows/Commands

#### Markdown-based (.md)
- Kiro, Windsurf, VibeCode, Kilocode, Agent, Cursor
- File `.md` với instructions trực tiếp

#### TOML-based (.toml)
- Gemini
- File `.toml` với field `prompt` chứa instructions
- Cấu trúc:
  ```toml
  description = "..."
  prompt = """
  ... instructions ...
  """
  ```

## Lưu ý quan trọng cho Kiro

### ✅ PHẢI LÀM
1. Đọc skill file trước khi thực hiện task
2. Đọc workflow file để hiểu quy trình
3. Follow đúng steps trong skill
4. Dừng lại khi skill yêu cầu "STOP and wait"
5. Không tự ý skip steps

### ❌ KHÔNG LÀM
1. Đoán hoặc tự sáng tạo workflow
2. Skip việc đọc skill/workflow files
3. Làm nhiều bước cùng lúc khi skill yêu cầu từng bước
4. Tự động tạo artifacts mà không hỏi user

## Ví dụ: Workflow tạo change mới

```markdown
User: "Tạo feature authentication mới"

Kiro workflow:
1. Đọc .kiro/skills/openspec-new-change/SKILL.md
2. Đọc .kiro/workflows/opsx-new.md
3. Derive name: "add-authentication"
4. Run: openspec new change "add-authentication"
5. Run: openspec status --change "add-authentication"
6. Run: openspec instructions <first-artifact> --change "add-authentication"
7. STOP - Show template và hỏi user
```

## Cập nhật tài liệu này

Khi thêm AI assistant mới hoặc thay đổi cấu trúc, cập nhật file này để đảm bảo tất cả AI đều có hướng dẫn đúng.

---

**Tạo bởi**: Kiro AI Assistant  
**Ngày**: 2026-02-15  
**Version**: 1.0
