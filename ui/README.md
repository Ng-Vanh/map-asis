# Map Assistant - React Frontend

## 🎨 Features

- 💬 **Chat Interface**: Giao diện chat thân thiện và trực quan
- 📝 **Markdown Support**: Hiển thị markdown đẹp mắt với react-markdown
- 🖼️ **Image Display**: Tự động hiển thị ảnh từ URL trong response
- 🎯 **Intent Badge**: Hiển thị loại intent được AI phân loại
- ⚡ **Real-time**: Giao tiếp real-time với backend API
- 🎨 **Beautiful UI**: Thiết kế hiện đại với Tailwind CSS

## 🚀 Quick Start

### 1. Cài đặt dependencies

```bash
cd /media/sda3/Workspace/map-assis/ui
npm install
```

### 2. Chạy development server

```bash
npm run dev
```

Ứng dụng sẽ chạy tại: http://localhost:3000

### 3. Build cho production

```bash
npm run build
npm run preview
```

## 📁 Project Structure

```
ui/
├── src/
│   ├── components/
│   │   ├── ChatInterface.jsx    # Main chat container
│   │   ├── Message.jsx           # Message bubble with markdown
│   │   └── MessageInput.jsx      # Input field with submit
│   ├── App.jsx                   # Root component
│   ├── main.jsx                  # Entry point
│   └── index.css                 # Global styles + Tailwind
├── package.json
├── vite.config.js
├── tailwind.config.js
└── index.html
```

## 🎯 API Integration

Frontend kết nối với backend API:
- **Endpoint**: `POST http://localhost:8864/api/v1/chat`
- **Request**: `{ "message": "user message" }`
- **Response**: `{ "response": "AI response", "intent": "intent_type" }`

## 🎨 Markdown Features

Message component hỗ trợ:
- ✅ **Headings** (H1-H6)
- ✅ **Lists** (ordered & unordered)
- ✅ **Tables** với styling đẹp
- ✅ **Code blocks** với syntax highlighting
- ✅ **Images** tự động resize
- ✅ **Links** mở tab mới
- ✅ **Blockquotes**
- ✅ **Bold, Italic, Strikethrough**
- ✅ **GitHub Flavored Markdown** (GFM)

## 🖼️ Image Display

Ảnh được tự động hiển thị khi có URL trong markdown:
```markdown
![Description](https://example.com/image.jpg)
```

Styling:
- Tự động resize phù hợp với container
- Border radius và shadow
- Lazy loading
- Max width responsive

## 📱 Responsive Design

- Desktop: Max width 4xl
- Tablet: Adaptive layout
- Mobile: Full width với spacing phù hợp

## 🎨 Customization

### Đổi màu chủ đạo

Edit [tailwind.config.js](tailwind.config.js):
```javascript
colors: {
  primary: {
    500: '#YOUR_COLOR',
    600: '#YOUR_COLOR',
  }
}
```

### Đổi API endpoint

Edit [ChatInterface.jsx](src/components/ChatInterface.jsx):
```javascript
const response = await axios.post('YOUR_API_URL', {
  message: userMessage
});
```

## 🔧 Technical Stack

- **React 18**: UI library
- **Vite**: Build tool & dev server
- **Tailwind CSS**: Utility-first CSS
- **react-markdown**: Markdown rendering
- **remark-gfm**: GitHub Flavored Markdown
- **axios**: HTTP client

## 📝 Example Messages

Thử các câu hỏi sau:
- "Tìm các địa điểm ở quận Hoàn Kiếm"
- "Gợi ý những nơi tôi nên đi ở Hà Nội"
- "So sánh Hồ Gươm và Hồ Tây"
- "Lên kế hoạch cho 3 ngày ở Hà Nội"
- "Tìm các quán cafe gần Văn Miếu"

## 🐛 Troubleshooting

### Lỗi kết nối API
Kiểm tra:
1. Backend đang chạy: `http://localhost:8864`
2. Neo4j service: port 7687
3. Qdrant service: port 6333
4. Embedding service: port 8080

### CORS issues
Vite proxy đã được cấu hình trong `vite.config.js`:
```javascript
proxy: {
  '/api': {
    target: 'http://localhost:8864',
    changeOrigin: true,
  }
}
```

## 📦 Dependencies

Main:
- react: ^18.2.0
- react-dom: ^18.2.0
- react-markdown: ^9.0.1
- remark-gfm: ^4.0.0
- axios: ^1.6.2

Dev:
- vite: ^5.0.8
- @vitejs/plugin-react: ^4.2.1
- tailwindcss: ^3.3.6
- autoprefixer: ^10.4.16
- postcss: ^8.4.32

## 🎯 Future Improvements

- [ ] Voice input
- [ ] Export conversation
- [ ] Dark mode
- [ ] Multi-language support
- [ ] Save conversation history
- [ ] Map integration
- [ ] Image upload support

## 📄 License

MIT
