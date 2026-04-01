# KẾ HOẠCH MEDISIGN AI - MODEL UPDATE

## Thay đổi Model: Qwen 70B → Qwen2.5-VL-72B

### Lý do thay đổi

| Feature | Qwen 70B | Qwen2.5-VL-72B |
|---------|-----------|-----------------|
| Text processing | ✅ | ✅ |
| **Đọc ảnh thuốc** | ❌ | ✅ |
| **OCR tích hợp** | ❌ | ✅ |
| Vietnamese | ✅ | ✅ tốt hơn |
| Self-hosted | ✅ | ✅ |

### Luồng xử lý mới

```
1. User gửi ẢNH THUỐC
         │
         ▼
2. Qwen2.5-VL-72B đọc ảnh
   - Extract tên thuốc từ nhãn
   - Trích xuất: hàm lượng, nhà sản xuất
         │
         ▼
3. Đối chiếu JSON Database
   - Tìm thuốc trong drug_database.json
   - Lấy thông tin: công dụng, liều, tương tác
         │
         ▼
4. Đưa ra kết luận
   - Thông tin thuốc
   - Cảnh báo y tế
   - Gợi ý gặp bác sĩ
```

### Dữ liệu Training hiện tại

| Dataset | Records |
|---------|---------|
| Train | 15,603 |
| Eval | 1,733 |
| **Total** | **17,336** |

### Target: 30,000+ records

Đang crawl thêm từ:
- Wikipedia (thuốc + bệnh)
- Drug interactions
- Vietnamese medical sources

### File cần thiết cho VL

```json
// drug_database.json
{
  "name": "Paracetamol 500mg",
  "brands": ["Hapacol", "Efferalgan", "Tylenol"],
  "uses": "Hạ sốt, giảm đau",
  "dose": "500-1000mg/lần",
  "side_effects": "Tổn thương gan nếu quá liều",
  "interactions": ["Warfarin", "Rượu"],
  "contraindications": ["Suy gan", "Dị ứng"]
}
```

### Status

- [x] Update Design.md: Qwen2.5-VL-72B
- [x] Update Required.md
- [x] Tạo tài liệu Qwen2.5-VL-Architecture.md
- [ ] Crawl dữ liệu hoàn chỉnh (đang chạy)
- [ ] Chuẩn hóa dữ liệu
- [ ] Fine-tune model

---
**Updated:** 2026-03-15
