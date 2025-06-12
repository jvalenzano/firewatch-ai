# 🏗️ Architecture Diagrams Access Guide

**Issue:** GitHub Pages not available on private GitHub Enterprise instance

## 📱 **LOCAL ACCESS (Immediate Solution)**

Open these files directly in your browser:

### **Main Architecture Index**
```
file:///Users/jasonvalenzano/risen-one-science-research-agent/docs/architecture/index.html
```

### **Individual Interactive Diagrams**

1. **🔥 Live Fire Risk Demo**
   ```
   file:///Users/jasonvalenzano/risen-one-science-research-agent/docs/architecture/interactive/risen_one_fire_risk_demo.html
   ```

2. **🤖 Multi-Agent Architecture**
   ```
   file:///Users/jasonvalenzano/risen-one-science-research-agent/docs/architecture/interactive/risen_one_mas_architecture.html
   ```

3. **🌐 AWS-GCP Integration**
   ```
   file:///Users/jasonvalenzano/risen-one-science-research-agent/docs/architecture/interactive/risen_one_integration_architecture.html
   ```

4. **🧠 Session Coordination**
   ```
   file:///Users/jasonvalenzano/risen-one-science-research-agent/docs/architecture/interactive/risen_one_session_coordination_example.html
   ```

5. **⚙️ Technical Workflow**
   ```
   file:///Users/jasonvalenzano/risen-one-science-research-agent/docs/architecture/interactive/risen_one_technical_workflow.html
   ```

## 🌐 **ALTERNATIVE HOSTING OPTIONS**

### **Option 1: Simple HTTP Server**
```bash
cd docs/architecture
python -m http.server 8090
# Then visit: http://localhost:8090
```

### **Option 2: Deploy to Public GitHub**
- Fork to public GitHub repository
- Enable GitHub Pages in repository settings
- Access via: `https://yourusername.github.io/repo-name/docs/architecture/`

### **Option 3: Deploy to Netlify/Vercel**
- Connect repository to Netlify or Vercel
- Set build directory to `docs/architecture`
- Get public URL for sharing

## 📋 **CURRENT STATUS**

- ✅ **All interactive diagrams fully functional locally**
- ❌ **GitHub Pages not available (private enterprise instance)**
- ✅ **Content completely accessible via file:// URLs**
- ✅ **Alternative hosting options available**

## 🚀 **RECOMMENDATION**

For immediate access, use the local file URLs above. For sharing with stakeholders, set up a simple HTTP server or deploy to a public hosting service. 