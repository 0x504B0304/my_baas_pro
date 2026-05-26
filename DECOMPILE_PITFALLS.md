# Python 3.11 字节码反编译常见错误（供 Agent 参考）

本文档记录了将 Python 3.11 `.pyc` 字节码反编译为 `.py` 源码时反复出现的系统性错误。反编译 Agent 在阅读 `dis.dis()` 输出时需特别注意以下模式。

---

## 1. CONTAINS_OP 1 = `not in`（漏掉 `not`）

**字节码**:
```
LOAD_CONST  '.'
LOAD_FAST   key
CONTAINS_OP 1          ← arg=1 表示 not in
POP_JUMP_FORWARD_IF_FALSE  → 跳转
```

**Python 3.11 opcode**:
- `CONTAINS_OP 0` → `a in b`
- `CONTAINS_OP 1` → `a not in b`

**错误还原**: `if '.' in key:`
**正确还原**: `if '.' not in key:`

**出险文件**: `config_panel.py`（两处）

---

## 2. KW_NAMES — 关键字参数值被当作位置参数

**字节码结构**:
```
LOAD_XXX  self          ← 位置1
LOAD_XXX  end           ← 位置2
LOAD_XXX  possibles     ← 位置3
LOAD_XXX  kw_val1       ← 【关键字值1】不是位置参数!
LOAD_XXX  kw_val2       ← 【关键字值2】不是位置参数!
KW_NAMES  ('cl', 'rate')  ← 关键字名(数量=kw_val数量)
PRECALL   N             ← N = 位置参数数 + 关键字参数数
CALL      N
```

**核心规则**: KW_NAMES 前的最后 K 个 LOAD（K = KW_NAMES 元组长度）是**关键字参数值**，不能作为位置参数。总参数 = PRECALL 的值。

**示例**:
```
LOAD_FAST  self
LOAD_CONST 'home_student'
LOAD_FAST  pos
LOAD_CONST (1233, 11)
LOAD_CONST 1
KW_NAMES   ('cl', 'rate')
PRECALL    5
CALL       5
```
3 个位置 + 2 个关键字 = 5。关键字值: `cl=(1233,11)`, `rate=1`。

**错误还原**: `detect(self, 'home_student', pos, (1233,11), cl=1, rate=1)`（cl 重复）
**正确还原**: `detect(self, 'home_student', pos, cl=(1233,11), rate=1)`

**常见误判**: 把关键字值替换为 `True`/`False`。如 `cl=1` → 错误还原为 `cl=True`。关键字值**必须严格取自对应的 LOAD_CONST**。

---

## 3. CALL_FUNCTION_EX — `func(*iterable)` 被误还原为 `func(iterable)`

**字节码**:
```
PUSH_NULL
LOAD_XXX  func
BUILD_LIST 0        ← 构建参数列表
LOAD_XXX  tuple_val
LIST_EXTEND 1       ← 展开 tuple_val 到列表
LOAD_CONST False
LIST_APPEND 1       ← 追加 False
LIST_TO_TUPLE       ← 转为元组
CALL_FUNCTION_EX 0  ← func(*args)
```

**错误还原**: `self.click(position[fn])`（单个元组参数）
**正确还原**: `self.click(*position[fn])` 或 `self.click(*position[fn], False)`（取决于列表构建的内容）

**出险文件**: `special_entrust.py`, `shop.py`, `main_story.py`, `work_task.py`, `cafe.py`

---

## 4. BUILD_CONST_KEY_MAP + DICT_UPDATE — 字典合并

**字节码**:
```
BUILD_MAP 0                    ← 构建空字典
LOAD_CONST 'key1'
LOAD_CONST val1
MAP_ADD 1                      ← 添加键值对
...
LOAD_CONST valA               ← 内层字典值1
LOAD_CONST valB               ← 内层字典值2
LOAD_CONST ('keyA','keyB')    ← 内层字典键元组
BUILD_CONST_KEY_MAP 2         ← 构建内层字典
DICT_UPDATE 1                  ← 合并到外层字典
STORE_NAME x                   ← x = 合并结果
```

**注意**: DICT_UPDATE 的 opcode 是 **165**，不是 STORE_SUBSCR (60)。`dis.dis()` 输出中会显示为 `DICT_UPDATE`。

**错误**: 把内层字典的 LOAD_CONST 值当作外层 MAP_ADD 的键值对，产生元组作 key 的垃圾条目
**正确**: 内层值 + 键元组 → BUILD_CONST_KEY_MAP 构建内层字典 → DICT_UPDATE 合并

---

## 5. 条件逻辑合并错误（`not enable` 被漏掉）

**原字节码模式**:
```
LOAD  enable
POP_JUMP_FORWARD_IF_TRUE  → closed/continue   ← enable=False 时进入
LOAD  end_str
COMPARE_OP  !=                                ← enbale=True 时检查
POP_JUMP_FORWARD_IF_FALSE                     ← end为空 跳到waiting
LOAD  end_time < now
POP_JUMP_FORWARD_IF_FALSE
→ closed/continue                              ← 过期也进入
```

**正确逻辑**: 两个独立判断:
```python
if not enable:              # disable → skip/closed
    continue
if expired:                 # enabled + expired → skip/closed
    continue
```

**错误还原**: 合并为单一条件
```python
if enable and expired:      # ← 丢了 not enable 分支
    continue
```

**出险函数**: `get_task()`, `task_schedule()`, `compute_schedule()`

---

## 6. MAP_ADD opcode 识别

在 Python 3.11 中:
- **MAP_ADD** = **opcode 147**（不是某些旧文档中的 96）
- **BUILD_MAP** = opcode 105
- **BUILD_CONST_KEY_MAP** = opcode 156
- **DICT_UPDATE** = opcode 165（不是 STORE_SUBSCR = 60）

当手动解析原始字节码 hex 时，确保使用正确的 opcode 映射。

---

## 7. BUILD_CONST_KEY_MAP 纯字典（无 BUILD_MAP 前缀）

某些纯数据模块**直接**使用 BUILD_CONST_KEY_MAP:
```
LOAD_CONST val1
LOAD_CONST val2
...
LOAD_CONST ('key1', 'key2', ...)
BUILD_CONST_KEY_MAP N
STORE_NAME x
```

无 BUILD_MAP 前缀，无 MAP_ADD。N 个值 + 1 个键元组 = N+1 个 LOAD_CONST，构建一个字典。

**注意**: 识别这种模式需要在 LOAD_CONST 序列中区分"值"和"键元组"，键元组是最后一个 LOAD_CONST，序列长度 = N+1。

---

## 8. 超长常量字符串被截断

`dis.dis()` 输出的常量字段会截断超长字符串（>2000 字符）。当反编译包含长 CSS/JSON 字符串的文件时：

- **不要依赖 dis.dis() 输出中的常量显示**
- **直接从 .pyc 提取**: `marshal.load(f)` → `code.co_consts[i]` 获取完整字符串
- CSS 文件例: `styles.py` 的 `_BASE` (13607 chars)、`LIGHT_STYLE` (21038 chars)

---

## 9. 无效元组边界框检查

坐标数据模块中，边界框格式为 `(x1, y1, x2, y2)`。反编译后应检查:
- `x1 > x2` 或 `y1 > y2` → 无效边界框（除非原版就有此数据）

本次仅发现 1 处: `assets/position/cn/arena.py` 的 `'enemy-lv': (565, 293, 535, 315)` — 原版数据即如此。

---

## 10. 列表推导式 key 截取

schema 遍历时，key 为完整路径（如 `config.schedule`），但 `_ListEntryEditor` 需要短 key（如 `schedule`）:

**字节码 listcomp**:
```
k.split('.', 1)[1]   ← 只取点号后的部分
```

**错误还原**: `(k, v)` — 直接用完整 key
**正确还原**: `(k.split('.', 1)[1], v)` — 截取短 key

---

## 快速排查清单

反编译后逐文件检查:

1. **搜索 `CONTAINS_OP 1`** → 确保对应 `not in`
2. **搜索 `KW_NAMES`** → 逐行验证关键字参数值和数量匹配
3. **搜索 `CALL_FUNCTION_EX`** → 确保 `*` 解包语法正确
4. **搜索 `POP_JUMP_FORWARD_IF_TRUE`** → 检查条件是否被反转
5. **搜索 `enable` + `end_time`** → 确认是两步独立判断而非合并
6. **搜索超长字符串** → 从 .pyc 直接提取而非依赖 dis 输出
7. **搜索 `(k, v) for k, v in schema`** → 确认是否需 `k.split('.',1)[1]`
8. **搜索 opcode 165** → 确认为 DICT_UPDATE 而非 STORE_SUBSCR
