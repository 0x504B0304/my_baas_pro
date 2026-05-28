# -*- coding: utf-8 -*-
"""BAAS Pro — 巴法云远程控制管理器

通过 TCP 长连接接入巴法云 (bemfa.com) IoT 平台，支持多配置独立启停。
每个配置可设置独立的 UID + Topic，收到 "on" 消息启动对应脚本，
收到 "off" 消息停止对应脚本。

架构：BemfaManager 在主进程（GUI 进程）运行，通过 process.m 控制
各 Baas 子进程的启停。这样即使子进程被终止，监听器仍可工作。
"""

import logging
import os
import socket
import threading
import time

from common import config

logger = logging.getLogger('baas.bemfa')

BEMFA_HOST = 'bemfa.com'
BEMFA_PORT = 8344
PING_INTERVAL = 30
RECONNECT_DELAY = 2


class BemfaManager:
    """巴法云远程控制管理器。

    负责：
    1. 读取所有配置文件中启用了 bemfa 的 (uid, topic) → [con, ...] 映射
    2. 为每个唯一的 (uid, topic) 建立 TCP 连接并订阅
    3. 后台监听 on/off 消息，调用 process.m.start_process / stop_process
    4. 定期心跳保活，断线自动重连
    """

    def __init__(self, process_module=None):
        """
        Args:
            process_module: common.process 模块引用（含 process.m 实例）。
                            传入 None 时延迟导入。
        """
        self._process_module = process_module
        # {(uid, topic): socket}
        self._sockets: dict[tuple[str, str], socket.socket] = {}
        # topic → [con1, con2, ...]  支持多个配置共享同一 topic
        self._topic_map: dict[str, list[str]] = {}
        self._lock = threading.Lock()
        self._running = False
        self._ping_timer: threading.Timer | None = None

    # ------------------------------------------------------------------
    # 公共接口
    # ------------------------------------------------------------------

    def start(self):
        """启动巴法云管理器：加载配置 → 建立连接 → 启动守护线程。"""
        if self._running:
            return
        self._running = True

        if self._process_module is None:
            from common import process as _proc
            self._process_module = _proc

        self._load_and_connect()
        if not self._sockets:
            logger.info('巴法云：无已启用的配置，跳过连接')
        else:
            logger.info(f'巴法云：已连接 {len(self._sockets)} 个设备')
        self._start_ping()

    def stop(self):
        """停止巴法云管理器：关闭所有连接、停止心跳。"""
        self._running = False
        if self._ping_timer:
            self._ping_timer.cancel()
            self._ping_timer = None

        with self._lock:
            for (uid, topic), sock in list(self._sockets.items()):
                try:
                    sock.close()
                except Exception:
                    pass
            self._sockets.clear()
            self._topic_map.clear()
        logger.info('巴法云：已停止')

    def reload(self):
        """热刷新：重新加载配置文件并更新连接映射。
        当用户修改配置后由 GUI 调用。
        """
        if not self._running:
            return
        old_topic_map = dict(self._topic_map)
        with self._lock:
            self._topic_map.clear()

        self._load_and_connect()

        # 关闭不再需要的旧连接
        old_keys = set(old_topic_map.keys())
        new_keys = set(self._topic_map.keys())
        removed_keys = old_keys - new_keys

        with self._lock:
            for uid, topic in list(self._sockets.keys()):
                if topic not in new_keys:
                    try:
                        self._sockets[(uid, topic)].close()
                    except Exception:
                        pass
                    del self._sockets[(uid, topic)]

        if removed_keys:
            logger.info(f'巴法云：已移除 {len(removed_keys)} 个不再使用的连接')

    # ------------------------------------------------------------------
    # 连接管理
    # ------------------------------------------------------------------

    def _load_and_connect(self):
        """扫描 configs/ 目录，为每个启用了 bemfa 的配置建立连接。"""
        mapping: dict[tuple[str, str], list[str]] = {}
        try:
            cfg_dir = config.config_dir()
            if not os.path.isdir(cfg_dir):
                return
            for fname in os.listdir(cfg_dir):
                if not fname.endswith('.json'):
                    continue
                con = fname[:-5]  # 去掉 .json
                mapping = self._collect_config(con, mapping)
        except Exception as e:
            logger.warning(f'巴法云：扫描配置目录失败 — {e}')
            return

        # 收集需要建立的新连接（在锁外执行 connect，避免死锁）
        to_connect: list[tuple[str, str]] = []
        with self._lock:
            self._topic_map.clear()
            for (uid, topic), cons in mapping.items():
                self._topic_map[topic] = cons
                key = (uid, topic)
                if key not in self._sockets:
                    to_connect.append(key)

        for uid, topic in to_connect:
            self._connect_one(uid, topic)

    def _collect_config(self, con: str, mapping: dict) -> dict:
        """读取单个配置，若启用了 bemfa 则加入映射。"""
        try:
            data = config.load_ba_config(con)
        except Exception:
            return mapping

        bemfa = data.get('baas', {}).get('bemfa', {})
        if not isinstance(bemfa, dict):
            return mapping
        if not bemfa.get('enable', False):
            return mapping

        uid = str(bemfa.get('uid', '')).strip()
        topic = str(bemfa.get('topic', '')).strip()
        if not uid or not topic:
            logger.warning(f'巴法云：[{con}] 已启用但 UID/Topic 为空，已跳过')
            return mapping

        key = (uid, topic)
        if key not in mapping:
            mapping[key] = []
        if con not in mapping[key]:
            mapping[key].append(con)
        return mapping

    def _connect_one(self, uid: str, topic: str):
        """为单个 (uid, topic) 建立 TCP 连接并启动监听线程。"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)  # 仅连接阶段超时
            sock.connect((BEMFA_HOST, BEMFA_PORT))
            subscribe_cmd = f'cmd=1&uid={uid}&topic={topic}\r\n'
            sock.send(subscribe_cmd.encode('utf-8'))
            sock.settimeout(None)  # 监听阶段阻塞等待，不做超时
            logger.info(f'巴法云：订阅成功 uid={uid} topic={topic}')
        except Exception as e:
            logger.warning(f'巴法云：连接失败 uid={uid} topic={topic} — {e}')
            return

        key = (uid, topic)
        with self._lock:
            self._sockets[key] = sock

        t = threading.Thread(
            target=self._listen, args=(uid, topic, sock),
            daemon=True, name=f'bemfa-{topic}'
        )
        t.start()

    def _reconnect(self, uid: str, topic: str):
        """断线后重连。"""
        if not self._running:
            return
        time.sleep(RECONNECT_DELAY)
        if not self._running:
            return
        logger.info(f'巴法云：尝试重连 uid={uid} topic={topic}')
        self._connect_one(uid, topic)

    # ------------------------------------------------------------------
    # 消息监听
    # ------------------------------------------------------------------

    def _listen(self, uid: str, topic: str, sock: socket.socket):
        """后台线程：循环接收 TCP 消息，解析 on/off 指令。"""
        buf = b''
        while self._running:
            try:
                data = sock.recv(1024)
                if not data:
                    logger.info(f'巴法云：连接断开 topic={topic}')
                    break
                buf += data
                # 按行解析（消息以 \n 分隔）
                while b'\n' in buf:
                    line, buf = buf.split(b'\n', 1)
                    self._parse_line(uid, topic, line)
            except (ConnectionError, OSError, TimeoutError) as e:
                # reload() 关闭旧连接时触发，属于正常行为，不警告
                logger.debug(f'巴法云：连接关闭 topic={topic} — {e}')
                break
            except Exception as e:
                logger.error(f'巴法云：未知异常 topic={topic} — {e}')
                break

        # 清理断开的连接
        key = (uid, topic)
        with self._lock:
            if key in self._sockets and self._sockets[key] is sock:
                del self._sockets[key]

        try:
            sock.close()
        except Exception:
            pass

        # 仅当没有同 key 的新连接时才重连（reload 可能已创建新连接）
        with self._lock:
            already_reconnected = key in self._sockets
        if self._running and not already_reconnected:
            self._reconnect(uid, topic)

    def _parse_line(self, uid: str, topic: str, line: bytes):
        """解析单行消息，触发 on/off 处理。"""
        try:
            msg = line.decode('utf-8', errors='replace').strip()
        except Exception:
            return
        if not msg:
            return

        logger.debug(f'巴法云：收到消息 topic={topic} — {msg}')

        if 'msg=on' in msg.lower():
            self._handle_on(topic)
        elif 'msg=off' in msg.lower():
            self._handle_off(topic)

    def _handle_on(self, topic: str):
        """收到 on 消息：启动该 topic 关联的所有配置。"""
        cons = self._topic_map.get(topic, [])
        for con in cons:
            try:
                state = self._process_module.m.state_process(con)
                if not state:
                    logger.info(f'巴法云：远程启动 [{con}]')
                    self._process_module.m.start_process(con)
                else:
                    logger.info(f'巴法云：[{con}] 已在运行，跳过启动')
            except Exception as e:
                logger.error(f'巴法云：启动 [{con}] 失败 — {e}')

    def _handle_off(self, topic: str):
        """收到 off 消息：停止该 topic 关联的所有配置。"""
        cons = self._topic_map.get(topic, [])
        for con in cons:
            try:
                state = self._process_module.m.state_process(con)
                if state:
                    logger.info(f'巴法云：远程停止 [{con}]')
                    self._process_module.m.stop_process(con)
                else:
                    logger.info(f'巴法云：[{con}] 未在运行，跳过停止')
            except Exception as e:
                logger.error(f'巴法云：停止 [{con}] 失败 — {e}')

    # ------------------------------------------------------------------
    # 心跳保活
    # ------------------------------------------------------------------

    def _start_ping(self):
        """启动定时心跳线程。"""
        self._ping_timer = threading.Timer(PING_INTERVAL, self._ping_loop)
        self._ping_timer.daemon = True
        self._ping_timer.start()

    def _ping_loop(self):
        """发送心跳 ping 到所有连接，并调度下一次。"""
        if not self._running:
            return

        with self._lock:
            dead_keys = []
            for key, sock in list(self._sockets.items()):
                try:
                    sock.send(b'ping\r\n')
                except Exception:
                    dead_keys.append(key)

        # 清理死连接并重连
        for uid, topic in dead_keys:
            logger.warning(f'巴法云：心跳失败 topic={topic}，将重连')
            with self._lock:
                if (uid, topic) in self._sockets:
                    try:
                        self._sockets[(uid, topic)].close()
                    except Exception:
                        pass
                    del self._sockets[(uid, topic)]
            self._reconnect(uid, topic)

        # 调度下一次心跳
        if self._running:
            self._ping_timer = threading.Timer(PING_INTERVAL, self._ping_loop)
            self._ping_timer.daemon = True
            self._ping_timer.start()


# 全局单例引用，由 MainWindow 管理生命周期
_bemfa_manager: BemfaManager | None = None


def get_manager() -> BemfaManager | None:
    """获取全局 BemfaManager 实例。"""
    return _bemfa_manager


def init_manager() -> BemfaManager:
    """初始化并启动全局 BemfaManager。"""
    global _bemfa_manager
    if _bemfa_manager is None:
        _bemfa_manager = BemfaManager()
    _bemfa_manager.start()
    return _bemfa_manager


def reload_manager():
    """热刷新全局 BemfaManager 配置。"""
    if _bemfa_manager is not None:
        _bemfa_manager.reload()


def shutdown_manager():
    """停止并销毁全局 BemfaManager。"""
    global _bemfa_manager
    if _bemfa_manager is not None:
        _bemfa_manager.stop()
        _bemfa_manager = None
