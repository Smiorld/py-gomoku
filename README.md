# py-gomoku
这个项目是用flask做的。一个在线五子棋项目。
目标是弄一个运算跑服务器端的web application，目前假想的是，有账号，有大厅，大厅里有房间，房间=棋局，能观战，能下棋能悔棋，还能房间内发消息聊天。


# plan

1.1 用户系统，能做多少做多少。后面的都得建立在这个之上了，不然坑太多。
1.2 。试图完善聊天框聊天功能
1.4 目前起码五子棋的部分能玩能跑

1.11 整个项目填坑填个80%-90%。
目前的todo：查看flask-socketio是否有事件接口。因为考虑到国情，一般出现断线重连大部分是IP已更换，需查看库session 算法是否包含含有ip参与计算。

# notes

12.28 今天把flask框架搭好了，数据库的表起了个头。初步接触、学习flask_socketOI 和 websocket。

12.29 把flask_socketIO和websocket打个样跑起来了。把数据库的room表填好了。把进出房间的socket及数据库的控制都写好了。
简单概括下现在有的功能：因为目前所有人都是不用账号的，加上为了测试，所以 一个窗口 = 一个用户 ，每个窗口都有自己链接到服务器的sessionid，作为唯一标识存在数据里。一个棋局最多容纳2+10个人，关闭窗口即可退出棋局。多的人会触发room reject的socket事件（暂时是一个警告弹窗+跳转到w3school）。

12.30 五子棋的纯棋局功能完整。右侧新增打印面板，用于开发阶段快速debug和监控数据。

12.31 右侧打印内容完善，新增棋局状态与回合信息，用h1输出。新增仅生效于客户端的假countdown timer。啥也不触发，只帮忙本地计时。

1.1 服务器端的timer做好了，历尽周折，简作记录。
第一步：首先eventlet使用的是协程，BackgroundScheduler实际是线程，两者是矛盾的。因此需要把线程绿化（变成协程？）。在使用BackgroundScheduler的文件中用猴子补丁实现本效果。
[解决方案参考一](https://blog.csdn.net/Ives_WangShen/article/details/103770838)[解决方案参考二](https://blog.csdn.net/u010376229/article/details/120819681?spm=1001.2101.3001.6661.1&utm_medium=distribute.pc_relevant_t0.none-task-blog-2%7Edefault%7ECTRLIST%7ERate-1-120819681-blog-103770838.pc_relevant_multi_platform_whitelistv4&depth_1-utm_source=distribute.pc_relevant_t0.none-task-blog-2%7Edefault%7ECTRLIST%7ERate-1-120819681-blog-103770838.pc_relevant_multi_platform_whitelistv4&utm_relevant_index=1)[解决方案参考三](https://stackoverflow.com/questions/71474916/is-it-possible-to-call-socketio-emit-from-a-job-scheduled-via-apscheduler-backg)

```python
import eventlet
eventlet.monkey_patch()
```

将上述代码放在任何一个跑了apscheduler的文件中最上方即可。

第二步：scheduler下的job执行时，db.model的query仍然会报错， 关于没有context。此处我折腾了一整天，翻了csdn和stackoverflow老久才找到相关的解决内容：[解决方案参考](https://stackoverflow.com/questions/40117324/querying-model-in-flask-apscheduler-job-raises-app-context-runtimeerror/47471227#47471227)

```python
def my_job():
    with app.app_context():
        ...
```

总算是大功告成。新年快乐。
