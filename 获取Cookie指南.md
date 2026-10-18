# 如何获取 LeetCode Session Cookie

要访问 LeetCode 的社区 solutions，您需要提供登录凭证（session cookie）。

## 步骤 1: 在浏览器中登录 LeetCode

1. 打开浏览器（Chrome、Firefox、Safari 等）
2. 访问 https://leetcode.com
3. 使用您的 VIP 账户登录

## 步骤 2: 获取 Session Cookie

### 方法 A: 使用 Chrome 浏览器

1. 登录后，按 `F12` 或 `Cmd+Option+I` (Mac) 打开开发者工具
2. 点击顶部的 **Application** 标签
3. 左侧展开 **Cookies** → 点击 `https://leetcode.com`
4. 找到名为 `LEETCODE_SESSION` 的 cookie
5. 双击右侧的 **Value** 列，复制整个值（很长的字符串）
6. （可选）同样方式复制 `csrftoken` 的值

### 方法 B: 使用 Firefox 浏览器

1. 登录后，按 `F12` 打开开发者工具
2. 点击 **Storage** (存储) 标签
3. 左侧展开 **Cookies** → 点击 `https://leetcode.com`
4. 找到 `LEETCODE_SESSION`
5. 复制其 **Value** (值)
6. （可选）同样方式复制 `csrftoken`

### 方法 C: 使用 Safari 浏览器

1. 首先启用开发菜单：Safari → 偏好设置 → 高级 → 勾选"在菜单栏中显示开发菜单"
2. 登录后，开发 → 显示Web检查器 (或 `Cmd+Option+I`)
3. 点击 **存储** 标签
4. 左侧点击 **Cookies** → `https://leetcode.com`
5. 找到 `LEETCODE_SESSION` 并复制其值

## 步骤 3: 配置环境变量

1. 在项目根目录创建 `.env` 文件：
   ```bash
   cp .env.example .env
   ```

2. 编辑 `.env` 文件，填入您的 cookie：
   ```bash
   nano .env
   # 或使用其他编辑器
   ```

3. 替换为您的实际值：
   ```env
   LEETCODE_SESSION=您复制的session值
   CSRF_TOKEN=您复制的csrftoken值
   ```

4. 保存文件 (nano: `Ctrl+X`, 然后 `Y`, 然后 `Enter`)

## 步骤 4: 运行爬虫

```bash
python scraper.py
```

现在爬虫将使用您的登录凭证来访问所有 solutions！

## 注意事项

⚠️ **安全提示：**
- **不要** 将 `.env` 文件提交到 Git（已在 .gitignore 中）
- **不要** 与他人分享您的 session cookie
- Session cookie 可能会过期，如果爬虫失败，请重新获取

⚠️ **Cookie 有效期：**
- LeetCode 的 session cookie 通常几天到几周后过期
- 如果爬虫突然无法访问内容，重新登录并获取新的 cookie

## 验证配置

运行此命令测试您的 session 是否有效：

```bash
python -c "
from config import LEETCODE_SESSION
if LEETCODE_SESSION and len(LEETCODE_SESSION) > 10:
    print('✓ LEETCODE_SESSION configured')
else:
    print('✗ LEETCODE_SESSION not found or invalid')
"
```

## 遇到问题？

如果仍然无法访问 solutions：
1. 确保在浏览器中能够正常访问 solutions 页面
2. 重新获取 cookie（可能已过期）
3. 检查 `.env` 文件中没有多余的空格或引号
4. 确保 cookie 值是完整的（通常很长）
