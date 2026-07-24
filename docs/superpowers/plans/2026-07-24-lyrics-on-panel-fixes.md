# Lyrics on Panel 修复实施计划

> **供智能执行者使用：** 按任务逐项执行；实现阶段必须使用测试驱动方式，验证步骤按批次集中运行。

**目标：** 为 YesPlayMusic 歌词接口补充安全回归测试，修复 Plasma 暗色面板的主题自适应显示，并在备份后完成本机部署与布局验证。

**架构：** 后端继续由 `LyricsManager` 通过 YesPlayMusic 本地 HTTP 接口取回 LRC，仅增加隔离真实网络的测试保障。前端默认直接使用 Plasma 运行时主题文字色，单色控制图标由 `Kirigami.Icon` 着色；原有自定义歌词颜色和黑白图标选项保留在“使用自定义颜色”开关之后。

**技术栈：** Python 3 `unittest`、KDE Plasma 6 QML、Kirigami、KConfig XML、systemd 用户服务。

---

### 任务 1：安全的后端回归测试

**文件：**

- 修改：`backend/src/test/test_server.py`
- 新建：`backend/src/test/test_lyrics_manager.py`

- [ ] 把 `test_server.py` 的四个 `asyncio.run(...)` 放进 `main()` 和 `if __name__ == "__main__":`，确保测试发现阶段不会连接真实 WebSocket 或发送播放控制。
- [ ] 新建 `unittest.TestCase`：构造 `LyricsManager`，mock `_http_get`，第一次严格匹配 `http://localhost:27232/player` 并返回当前曲目，第二次严格匹配 `http://localhost:27232/api/lyric?id=12345` 并返回两行 LRC。
- [ ] 断言解析结果包含正确的微秒时间戳和歌词，并断言 `_http_get` 恰好按上述顺序调用两次。
- [ ] 在开发副本中临时把接口变异成 `/lyric?id=`，运行 `python -m unittest backend/src/test/test_lyrics_manager.py -v`，预期因 URL 不匹配失败；随后恢复 `/api/lyric?id=` 并重跑，预期通过。
- [ ] 运行安全测试发现、Python 编译检查和现有播放器模式相关单元测试；不得运行会连接真实服务的控制流程。
- [ ] 将安全测试与 YesPlayMusic 回归保障作为独立后端提交。

### 任务 2：主题自适应文字和控制图标

**文件：**

- 修改：`kde/v2/contents/config/main.xml`
- 修改：`kde/v2/contents/ui/configGeneral.qml`
- 修改：`kde/v2/contents/ui/main.qml`
- 新建：`backend/src/test/test_plasma_theme.py`

- [ ] 先写静态回归测试：KConfig 的 `Color` 默认值必须是合法十六进制颜色；新增 `useCustomColorsChecked` 默认为 `false`；歌词默认走 Plasma 主题色；控制图标必须由 `Kirigami.Icon` 按有效颜色着色。
- [ ] 运行 `python -m unittest backend/src/test/test_plasma_theme.py -v`，确认旧代码因 XML 默认值和 QML 主题绑定缺失而失败。
- [ ] 在 KConfig 中增加 `useCustomColorsChecked=false`，并把 `lyricTextColor` 默认值改成合法颜色字面量。
- [ ] 配置页增加“使用自定义文字和图标颜色”开关；仅在开关启用时允许编辑歌词颜色和白色图标选项。
- [ ] 主界面计算有效颜色：默认采用 `PlasmaCore.Theme.textColor`，自定义模式采用用户歌词色以及黑色或白色图标色。
- [ ] 用 `Kirigami.Icon` 替换控制区的单色 `Image`，设置 `isMask: true` 和主题颜色；“喜欢”状态保留原 SVG 的强调色。
- [ ] 重跑主题回归测试，并用 `qmllint`、XML 解析和 `kpackagetool6` 包校验检查 QML/KConfig。
- [ ] 将主题修复作为独立前端提交。

### 任务 3：受保护的本机部署与验收

**文件：**

- 本机安装：`~/.local/share/lyrics-on-panel`
- Plasma 小组件：`~/.local/share/plasma/plasmoids/lyrics-on-panel-plasma6-v2`
- Plasma 配置：`~/.config/plasma-org.kde.plasma.desktop-appletsrc`

- [ ] 再次记录两个安装位置的状态和 diff；创建带时间戳的独立备份，不清理、不重置安装目录 Git 工作区。
- [ ] 仅在源码测试通过后，从修复分支部署后端目标文件和 v2 小组件内容。
- [ ] 为 Plasma 配置创建时间戳备份，把 `AppletOrder` 精确改为 `3;4;5;6;27;7;21;22`；不把该文件加入 Git。
- [ ] 重启 `Universal-Mpris-LyricServer.service` 和 `plasma-plasmashell.service`，检查服务状态及日志。
- [ ] 连接 `/poll`，验证当前 YesPlayMusic 曲目的 `lyrics.current_lyric` 非空并随位置变化；检查小组件位于系统托盘左侧且暗色面板文字、图标清晰。
- [ ] 再次重启并复核布局和配置持久化；报告任何需要人工目视确认的项目。
- [ ] 不创建 PR；最终分别说明 fork 源码提交、本机配置、部署证据和未执行的外部动作。
