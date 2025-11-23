# Kyaru

公主连结渠道服/台服会战查询网页端，代号「Kyaru」

解决了机器人不能搜索的问题，显示更加方便。从此渠道服与台服可以在线快速查询公会战信息。

参考项目 https://github.com/Kengxxiao/Kyouka

由于搞不到公会ID，所以收藏功能不能做了。

demo page : https://kyaru.infedg.xyz/tw

渠道服数据获取方式已开源，在项目 https://github.com/infinityedge01/qqbot2/tree/main/hoshino/modules/Luna 内，是 nonebot 插件的形式。

Traditional Chinese Translated By [@TragicLifeHu](https://github.com/TragicLifeHu).

## 手动备份数据

如果错过了自动备份时间（会战开始前一天），可以使用以下命令手动触发数据迁移：

```bash
python manual_backup.py
```

## 手动运行数据抓取

如果需要手动触发一次数据抓取（非最终结算），可以使用以下命令：

```bash
python manual_stage_data.py
```
