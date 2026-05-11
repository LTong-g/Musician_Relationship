# force-graph 可控项清单

## 数据输入

- 图数据：`graphData([data])`
- 节点 ID 字段：`nodeId([str])`
- 边源字段：`linkSource([str])`
- 边目标字段：`linkTarget([str])`

## 容器布局

- 画布宽度：`width([px])`
- 画布高度：`height([px])`
- 背景颜色：`backgroundColor([str])`

## 节点样式

- 节点相对大小：`nodeRelSize([num])`
- 节点数值映射：`nodeVal([num, str or fn])`
- 节点标签：`nodeLabel([str or fn])`
- 节点显示开关：`nodeVisibility([boolean, str or fn])`
- 节点颜色：`nodeColor([str or fn])`
- 节点自动分色：`nodeAutoColorBy([str or fn])`
- 自定义节点绘制：`nodeCanvasObject([fn])`
- 节点自定义绘制模式：`nodeCanvasObjectMode([str or fn])`
- 节点命中区域绘制：`nodePointerAreaPaint([fn])`

## 边样式

- 边标签：`linkLabel([str or fn])`
- 边显示开关：`linkVisibility([boolean, str or fn])`
- 边颜色：`linkColor([str or fn])`
- 边自动分色：`linkAutoColorBy([str or fn])`
- 边虚线：`linkLineDash([num[], str or fn])`
- 边宽度：`linkWidth([num, str or fn])`
- 边曲率：`linkCurvature([num, str or fn])`
- 自定义边绘制：`linkCanvasObject([fn])`
- 边自定义绘制模式：`linkCanvasObjectMode([str or fn])`
- 箭头长度：`linkDirectionalArrowLength([num, str or fn])`
- 箭头颜色：`linkDirectionalArrowColor([str or fn])`
- 箭头位置：`linkDirectionalArrowRelPos([num, str or fn])`
- 粒子数量：`linkDirectionalParticles([num, str or fn])`
- 粒子速度：`linkDirectionalParticleSpeed([num, str or fn])`
- 粒子偏移：`linkDirectionalParticleOffset([num, str or fn])`
- 粒子宽度：`linkDirectionalParticleWidth([num, str or fn])`
- 粒子颜色：`linkDirectionalParticleColor([str or fn])`
- 粒子自定义绘制：`linkDirectionalParticleCanvasObject([fn])`
- 主动发射粒子：`emitParticle(link)`
- 边命中区域绘制：`linkPointerAreaPaint([fn])`
- 边悬停精度：`linkHoverPrecision([int])`

## 力导向与布局

- DAG 模式：`dagMode([str])`
- DAG 层间距：`dagLevelDistance([num])`
- DAG 节点过滤：`dagNodeFilter([fn])`
- DAG 错误处理：`onDagError([fn])`
- 最小 alpha：`d3AlphaMin([num])`
- alpha 衰减：`d3AlphaDecay([num])`
- 速度衰减：`d3VelocityDecay([num])`
- 力函数配置：`d3Force(str, [fn])`
- 重新点燃模拟：`d3ReheatSimulation()`
- 预热步数：`warmupTicks([int])`
- 冷却步数：`cooldownTicks([int])`
- 冷却时间：`cooldownTime([num])`

## 交互

- 节点点击：`onNodeClick(fn)`
- 节点右键：`onNodeRightClick(fn)`
- 节点悬停：`onNodeHover(fn)`
- 节点拖动：`onNodeDrag(fn)`
- 节点拖动结束：`onNodeDragEnd(fn)`
- 边点击：`onLinkClick(fn)`
- 边右键：`onLinkRightClick(fn)`
- 边悬停：`onLinkHover(fn)`
- 背景点击：`onBackgroundClick(fn)`
- 背景右键：`onBackgroundRightClick(fn)`
- 指针光标：`showPointerCursor([objAccessor])`
- 缩放回调：`onZoom(fn)`
- 缩放结束回调：`onZoomEnd(fn)`
- 节点拖拽开关：`enableNodeDrag([boolean])`
- 缩放交互开关：`enableZoomInteraction([boolean or fn])`
- 平移交互开关：`enablePanInteraction([boolean or fn])`
- 指针命中开关：`enablePointerInteraction([boolean])`

## 视图控制

- 暂停自动重绘：`autoPauseRedraw([boolean])`
- 暂停动画：`pauseAnimation()`
- 恢复动画：`resumeAnimation()`
- 视口中心：`centerAt([x], [y], [durationMs])`
- 视口缩放：`zoom([scale], [durationMs])`
- 适配到画布：`zoomToFit([durationMs], [padding], [nodeFilter])`
- 最小缩放：`minZoom([scale])`
- 最大缩放：`maxZoom([scale])`
- 渲染前回调：`onRenderFramePre(callback)`
- 渲染后回调：`onRenderFramePost(callback)`

## 工具方法

- 图边界框：`getGraphBbox([nodeFilter])`
- 屏幕转图坐标：`screen2GraphCoords(x, y)`
- 图转屏幕坐标：`graph2ScreenCoords(x, y)`
