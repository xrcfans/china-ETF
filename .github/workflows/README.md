# 指数基金权重数据

自动获取五大指数（沪深300、中证500、中证A500、上证180、创业板指）成分股权重数据。

## 数据更新

- **自动更新**：每周一上午9点（UTC+8）
- **手动更新**：点击 Actions → Update Index Data → Run workflow

## 数据文件

| 文件 | 说明 | 大小 |
|------|------|------|
| `data.json` | 完整格式，按指数分离 | ~200KB |
| `data-compact.json` | 紧凑格式，无缩进 | ~150KB |
| `data-merged.json` | 合并去重，含重叠信息 | ~300KB |

## 使用方法

前端直接读取：
```javascript
const data = await fetch('https://raw.githubusercontent.com/xrcfans/index-data/main/data.json');
const indices = await data.json();
