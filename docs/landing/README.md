# RapidWhisper Landing Page

Modern, responsive landing page for RapidWhisper - a cross-platform speech-to-text transcription application.

## 🎨 Features

- **Modern Design**: Clean, minimalist design inspired by SuperWhisper
- **Fully Responsive**: Works perfectly on desktop, tablet, and mobile
- **Smooth Animations**: Scroll animations and transitions
- **Cross-Platform Focus**: Highlights Windows, macOS, and Linux support
- **Complete Documentation**: Comprehensive docs page with sidebar navigation
- **SEO Optimized**: Proper meta tags and semantic HTML

## 📁 Structure

```
docs/landing/
├── index.html          # Main landing page
├── docs.html           # Documentation page
├── styles.css          # Main styles
├── docs-styles.css     # Documentation-specific styles
├── script.js           # Main page interactions
├── docs-script.js      # Documentation page interactions
└── README.md           # This file
```

## 🚀 Quick Start

### Local Development

Simply open `index.html` in your browser:

```bash
cd docs/landing
# Open in default browser
start index.html  # Windows
open index.html   # macOS
xdg-open index.html  # Linux
```

### Using a Local Server

For better development experience with live reload:

```bash
# Using Python
python -m http.server 8000

# Using Node.js (http-server)
npx http-server -p 8000

# Using PHP
php -S localhost:8000
```

Then visit: `http://localhost:8000`

## 📄 Pages

### Main Landing Page (`index.html`)

- **Hero Section**: Eye-catching introduction with CTA buttons
- **Demo Section**: Visual representation of the app
- **Features Grid**: 9 key features with icons
- **How It Works**: 4-step process explanation
- **Platforms Section**: Detailed platform support (Windows, macOS, Linux)
- **Download Section**: Download options for all platforms
- **Footer**: Links and social media

### Documentation Page (`docs.html`)

- **Sidebar Navigation**: Easy access to all sections
- **Getting Started**: Installation and quick start guides
- **Features**: Detailed feature explanations
- **Configuration**: Settings and customization
- **Platform Guides**: Platform-specific instructions
- **Troubleshooting**: Common issues and solutions
- **FAQ**: Frequently asked questions

## 🎨 Customization

### Colors

Edit CSS variables in `styles.css`:

```css
:root {
    --primary: #6366f1;        /* Primary brand color */
    --primary-dark: #4f46e5;   /* Darker shade */
    --secondary: #8b5cf6;      /* Secondary color */
    --text-primary: #1f2937;   /* Main text */
    --text-secondary: #6b7280; /* Secondary text */
}
```

### Content

1. **Update Links**: Replace `yourusername` in GitHub links
2. **Add Download Links**: Update download URLs in the download section
3. **Customize Features**: Edit feature cards in the features section
4. **Update Documentation**: Modify docs.html content as needed

### Images

To add images:

1. Create an `images/` folder
2. Add your images
3. Update image paths in HTML:

```html
<img src="images/screenshot.png" alt="RapidWhisper Screenshot">
```

## 🌐 Deployment

### GitHub Pages

1. Push to GitHub repository
2. Go to Settings → Pages
3. Select branch and `/docs/landing` folder
4. Save and wait for deployment

### Netlify

1. Drag and drop the `landing/` folder to Netlify
2. Or connect your GitHub repository
3. Set build directory to `docs/landing`

### Vercel

```bash
cd docs/landing
vercel
```

### Custom Server

Upload all files to your web server:

```bash
# Using SCP
scp -r docs/landing/* user@server:/var/www/html/

# Using FTP
# Use your preferred FTP client
```

## 📱 Responsive Breakpoints

- **Desktop**: 1024px and above
- **Tablet**: 768px - 1023px
- **Mobile**: Below 768px

## ✨ Features Highlighted

1. ⚡ **Lightning Fast** - 1-2 second transcription
2. 🎯 **Smart Formatting** - Context-aware text formatting
3. 🌍 **Multi-Language** - 15 interface languages
4. 🎨 **Beautiful UI** - Modern floating window
5. 🤫 **Smart Detection** - Automatic silence detection
6. ⌨️ **Global Hotkey** - Activate from anywhere
7. 🔔 **System Tray** - Background operation
8. ⚙️ **Easy Configuration** - Graphical settings
9. 🌐 **Web Apps Support** - 20+ web applications

## 🔧 Browser Support

- Chrome/Edge: ✅ Full support
- Firefox: ✅ Full support
- Safari: ✅ Full support
- Opera: ✅ Full support
- IE11: ❌ Not supported

## 📝 SEO Checklist

- [x] Meta description
- [x] Semantic HTML5 tags
- [x] Alt text for images
- [x] Proper heading hierarchy
- [x] Mobile-friendly
- [x] Fast loading
- [x] HTTPS ready

## 🎯 Performance

- **Minimal Dependencies**: No heavy frameworks
- **Optimized CSS**: Clean, efficient styles
- **Lazy Loading**: Images load on demand
- **Fast Animations**: GPU-accelerated transforms

## 📄 License

Same as RapidWhisper - Proprietary Software, Free for Personal & Business Use

## 🤝 Contributing

To improve the landing page:

1. Fork the repository
2. Make your changes in `docs/landing/`
3. Test responsiveness
4. Submit a pull request

## 📞 Support

For issues or questions:
- GitHub Issues: [Create an issue](https://github.com/yourusername/rapidwhisper/issues)
- Documentation: [View docs](docs.html)

---

**Built with ❤️ for RapidWhisper**
