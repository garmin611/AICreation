# 项目开发需求描述

## 一、功能概述

本项目致力于打造一个融合大语言模型（LLM）与 ComfyUI 的智能创作平台，主要面向小说创作者、插画师以及 AI 生成内容开发者等群体。该平台能够助力用户快速生成创意文本，并结合 AI 技术实现图像生成。其中，LLM 的调用将通过类似 OpenAI 的 API 接口来完成，后端部分则采用 Python 的 FastAPI 框架搭建服务器，其职责是与 ComfyUI 服务器进行交互，并对外提供相应的 API 接口。平台生成的内容以文件夹形式存储，便于管理和扩展。

## 二、项目结构及功能规划

### 项目分层结构

项目采用分层架构设计，主要包括以下几个层次：

1. **API 接口层（controller）** ：负责处理前端请求，对外提供统一的 API 接口，进行参数校验和请求转发，返回处理结果给前端。
2. **业务逻辑层（service）** ：封装具体的业务逻辑，包括文本生成、图像生成、知识图谱管理等功能，调用数据访问层和工具类来完成业务处理。
3. **工具类（utils）** ：提供一些通用的工具方法，如提示词管理、上下文管理、音频生成等。

### 项目文件结构

```
ai-factory/                # 项目根目录
├── server/               # 服务器端代码
│   ├── config/           # 配置文件夹
│   │   ├── config.py     # 配置文件操作接口
│   │   └── config.yaml   # 系统配置文件
│   ├── controllers/      # API 接口层
│   │   ├── project_controller.py # 项目管理相关接口
│   │   ├── chapter_controller.py # 章节管理相关接口
│   │   ├── entity_controller.py # 实体管理相关接口
│   │   ├── media_controller.py   # 媒体生成相关接口
│   │   ├── video_controller.py   # 视频生成相关接口
│   │   └── admin_controller.py   # 系统管理接口（包括配置文件修改）
│   ├── services/         # 业务逻辑层
│   │   ├── llm_service.py    # LLM 相关业务逻辑
│   │   ├── image_service.py  # 图像生成相关业务逻辑
│   │   ├── kg_service.py     # 知识图谱管理相关业务逻辑
│   │   ├── singleton_service.py # 单例服务基类
│   │   ├── audio_service.py  # 音频生成相关业务逻辑
│   │   └── video_service.py  # 视频生成相关业务逻辑
│   ├── utils/            # 工具类
│   │   ├── prompt_manager.py # 提示词管理工具
│   │   ├── context_manager.py # 上下文管理工具
│   │   └── file_manager.py   # 文件管理工具
│   ├── prompts/          # 提示词模板文件夹
│   │   ├── novel_writing.txt     # 小说写作提示词模板
│   │   ├── character_generation.txt # 人物生成提示词模板
│   │   └── image_generation.txt  # 图像生成提示词模板
│   └── workflow/         # 工作流配置文件夹
│       └── default_workflow.json # 默认工作流配置文件
├── projects/             # 项目文件夹（与 server 同级）
│   ├── project1/         # 具体项目文件夹
│   │   ├── kg.json       # 知识图谱数据文件
│   │   ├── last_content.txt  # 最新生成的内容，用于维护写作上下文
│   │   ├── chapter1/     # 章节文件夹
│   │   │   ├── content.txt   # 章节内容文件（由 generate_chapter API 生成）
│   │   │   ├── 1/       # 子文件夹
│   │   │   │   ├── span.txt
│   │   │   │   ├── prompt.json
│   │   │   │   ├── image_2025-02-05_10-15-30_seed_12345.png
│   │   │   │   └── audio_2025-02-05_10-15-30.wav
│   │   │   ├── 2/       # 子文件夹
│   │   │   └── ...      # 其他子文件夹
│   │   └── ...          # 其他章节文件夹
│   └── ...              # 其他项目文件夹
└── README.md            # 项目说明文档
```

### 路径配置说明

项目中的路径配置遵循以下规则：

1. **项目文件夹（projects_path）**：

   - 配置值：`../projects/`
   - 说明：相对于 server 目录的上一级目录，与 server 目录同级
   - 用途：存储所有用户创建的项目及其相关文件

2. **提示词模板文件夹（prompts_path）**：

   - 配置值：`prompts/`
   - 说明：相对于 server 目录
   - 用途：存储各类提示词模板文件

3. **工作流配置文件夹（workflow）**：

   - 配置值：`workflow/default_workflow.json`
   - 说明：相对于 server 目录
   - 用途：存储 ComfyUI 的工作流配置文件

所有路径配置均在 `server/config/config.yaml` 文件中定义。在使用相对路径时，server 端的代码会自动根据当前运行环境解析正确的绝对路径。

## 三、API 接口说明

### 1. 项目管理接口 (`project_controller.py`)

**功能描述**：

- 提供与项目管理相关的 API 接口，包括创建项目、获取项目列表、获取项目详情、更新项目名称和删除项目
- 创建项目时会自动创建项目目录和知识图谱文件（kg.json）
- 提供项目信息的增删改查功能

**主要接口**：

- `POST /project/create`：创建新项目，初始化项目目录和知识图谱文件
- `GET /project/info`：获取项目详细信息
- `GET /project/list`：获取所有项目列表
- `PUT /project/update`：更新项目信息
- `DELETE /project/delete`：删除指定项目

### 2. 实体管理接口 (`entity_controller.py`)

- 提供角色、场景管理相关的 API 接口，包括获取角色列表、更新角色信息、锁定/解锁角色、删除角色、获取场景列表、更新场景信息、删除场景等功能
- 所有接口都需要提供 project_name 参数来指定操作的项目
- 与知识图谱服务（kg_service）、场景服务(scene_service)交互来管理信息

### 3. 章节管理接口 (`chapter_controller.py`)

**功能描述**：

- 提供章节管理相关的 API 接口
- 支持章节的创建、获取、保存、生成和分割功能
- 通过 `llm_service` 获取章节内容，确保统一的内容访问方式
- **流式响应支持**：`/chapter/generate` 接口支持流式响应，允许前端实时接收生成的文本内容。

**主要接口**：

- `POST /chapter/create`：创建新章节
- `GET /chapter/content`：获取指定章节的内容
- `POST /chapter/save`：保存章节内容
- `POST /chapter/generate`：使用 AI 生成章节内容，支持流式响应。
  - 请求参数：
    - `project_name`（字符串，项目名称）
    - `chapter_name`（字符串，章节名称）
    - `prompt`（字符串，生成提示词）
    - `is_continuation`（布尔值，是否为续写模式）
    - `use_last_chapter`（布尔值，是否使用上一章内容作为上下文）
  - 返回：实时生成的章节内容，使用 SSE（Server-Sent Events）格式。
- `POST /chapter/split-text`：将章节内容分割成多个子章节，使用配置文件中的 window_size 参数控制分割大小
- `GET /chapter/list`：获取项目的所有章节列表
- `POST /api/chapter/save_scenes`：保存修改后的场景内容
  - 接收参数：
    - `project_name`（字符串，项目名称）
    - `chapter_name`（字符串，章节名称）
    - `scenes`（列表，场景列表）
      - 每个场景包含：`index`（序号）、`span`（分割片段）、`scene`（场景描述）、`prompt`（提示词）
  - 处理逻辑：
    - 根据场景序号找到对应的文件夹
    - 将分割片段保存到 `span.txt`
    - 将场景描述和提示词保存到 `prompt.json`

### 4. 媒体生成接口 (`media_controller.py`)

**功能描述**：

- 提供图像和音频生成的相关接口
- 支持单个和批量生成
- 提供任务进度查询和取消功能
- 处理 ComfyUI 的输出，包括保存的图片和预览图片
- 支持音频生成和管理

**主要接口**：

1. **图像生成**

   - `POST /media/generate_images`：生成一个或多个图片
   - 接收参数：
     - `project_name`（字符串，项目名称）
     - `chapter_name`（字符串，章节名称）
     - `prompts`（数组）：每个元素包含：
       - `id`（数字，场景 ID）
       - `prompt`（字符串，提示词）
     - `imageSettings`（对象，图片设置，包含宽度、高度等）
     - `workflow`（字符串，可选，工作流名称，默认为 "default_workflow.json"）
     - `params`（对象，可选，生成参数）
   - 返回：任务 ID 和总任务数

2. **音频生成**

   - `POST /media/generate-audio`：生成单个音频文件
   - 接收参数：
     - `project_name`（字符串，项目名称）
     - `chapter_name`（字符串，章节名称）
     - `audioSettings`（对象）：
       - `voice`（字符串，语音名称）
       - `rate`（字符串，语速，如 "+0%"）
     - `prompts`（数组）：每个元素包含：
       - `id`（数字，场景 ID）
       - `prompt`（字符串，文本内容）
   - 返回：任务 ID 和总任务数

3. **进度查询**

   - `GET /media/progress`：查询任务进度
   - 接收参数：
     - `task_id`（字符串，任务 ID）
   - 返回：
     - `status`：任务状态（running/completed/error/cancelled）
     - `current`：当前进度
     - `total`：总任务数
     - `task_type`：任务类型（audio/image）
     - `errors`：错误信息数组

4. **任务取消**

   - `POST /media/cancel`：取消正在进行的任务
   - 接收参数：
     - `task_id`（字符串，任务 ID）
   - 返回：取消操作是否成功

5. **媒体文件获取**

   - `GET /media/audio`：获取音频文件
   - `GET /media/image`：获取图片文件
   - 接收参数：
     - `project_name`（字符串，项目名称）
     - `chapter_name`（字符串，章节名称）
     - `span_id`（字符串，span ID）
     - `file_name`（字符串，文件名，仅音频需要）

**任务管理**：

- 使用任务 ID 跟踪每个生成任务
- 维护任务状态、进度和错误信息
- 支持任务取消和清理
- 自动生成随机种子（图片生成）
- 处理 ComfyUI 的 WebSocket 消息（图片生成）
- 获取和处理 ComfyUI 的历史记录（图片生成）

**错误处理**：

- 记录详细的错误信息
- 支持多种错误类型：
  - 工作流加载失败
  - 图片生成失败
  - 图片保存失败
  - WebSocket 连接失败
  - ComfyUI 服务器错误
  - 音频生成失败
  - 参数验证错误
- 错误信息包含在任务状态中返回给前端

**输出处理**：

- 图片输出：
  - 保存的图片文件
  - 预览图片
  - 节点输出信息
  - 图片文件命名包含时间戳和种子信息
- 音频输出：
  - WAV 格式音频文件
  - 文件名包含时间戳
  - 支持批量生成时的序号
- 自动创建输出目录

### 5. 系统管理接口 (`admin_controller.py`)

**功能描述**：

- 提供系统管理相关的 API 接口，包括修改配置文件、获取配置文件内容等功能。
- 在返回配置时会自动移除敏感信息（如 API keys）。
- 支持批量更新多个配置项。

**提供的接口**：

- **获取配置文件**：

  - `GET /api/admin/config`：获取当前的配置文件内容，以 JSON 格式返回。
  - 接收参数：无。
  - 返回值会自动移除敏感信息。

- **更新配置文件**：

  - `POST /api/admin/config`：更新配置文件中的一项或多项设置。
  - 接收参数：JSON 对象，包含要更新的配置项。
  - 支持嵌套的配置项更新。
  - 返回更新后的完整配置（同样会移除敏感信息）。

### 6. 视频生成服务 (`video_service.py`)

**功能描述**：

- 基于 `moviepy` 实现的视频生成服务，支持将图片和音频合成为视频。
- 提供异步生成机制和多线程处理。
- 支持自定义视频效果（缩放、平移）。
- 实现了单例模式，确保资源的有效利用。
- 需要安装ffmpeg并添加环境变量

**主要功能**：

- **视频生成**：

  - 支持整章节的视频生成。
  - 自动按顺序处理所有场景。
  - 并行处理多个视频片段。
  - 自动合并为完整视频。
  - 支持自定义视频参数（分辨率、帧率、编码器等）。

- **效果处理**：

  - 支持图片动态缩放效果。
  - 支持动态平移特效。
  - 支持自定义分辨率和帧率。

**内部机制**：

- **并行处理**：

  - 使用 `ThreadPoolExecutor` 实现并行处理。
  - 每个场景独立生成视频片段。
  - 最后统一合并所有片段。

- **临时文件管理**：

  - 使用临时文件暂存每个视频片段，确保在生成过程中不会因内存占用过高而影响性能。
  - 临时文件在视频生成完成后会自动清理，避免残留文件占用磁盘空间。
  - 这种方式的好处是能够有效管理内存和磁盘资源，尤其是在处理大量视频片段时，避免内存溢出问题。

- **效果处理**：

  - 动态缩放和平移效果通过逐帧计算实现，确保视频效果的平滑过渡。

**主要方法**：

- `generate_video`：生成视频主方法

  - 参数：`chapter_path`（章节路径）、`video_settings`（视频设置）。
  - 返回：生成的视频文件路径。
  - 支持多线程处理。
  - 自动排序和处理子文件夹。
  - 合并所有视频片段。
  - 输出最终视频文件。

- `_process_segment`：处理单个视频片段

  - 加载资源文件。
  - 应用视频效果。
  - 生成帧数据并写入临时视频文件。

- `_apply_effects`：应用视频效果

  - 实现动态缩放效果。
  - 实现动态平移效果。
  - 支持自定义参数。

- `_merge_videos`：合并视频片段

  - 使用 `ffmpeg` 合并所有临时视频片段。
  - 支持硬件加速（如可用）。

> **硬编码加速说明**：
>
> 本服务支持使用 NVIDIA GPU 进行视频编码加速（NVENC），需要进行以下配置：
>
> 1. 下载 FFmpeg Builds ，并解压
> 2. 设置环境变量：
>
>    - 将 FFmpeg 的 bin 目录添加到系统的 PATH 环境变量
>    - 确保 NVIDIA 显卡驱动已正确安装
>
> 3. 验证配置：
>
>    - 打开命令行，运行 `ffmpeg -encoders | findstr nvenc`
>    - 如果显示包含 h264_nvenc，则说明配置成功
>
> 如果配置失败或没有 NVIDIA 显卡，系统会自动切换到 CPU 编码模式。

## 五、工具类（utils）

### 1. 提示词管理工具 (`prompt_manager.py`)

**功能描述**：

- 提供提示词管理功能。
- **加载提示词模板**：从 `prompts/` 文件夹中加载提示词模板。
- **替换提示词中的变量**：实现提示词的动态更新，以适应不同的创作需求。

**提供的接口**：

- `load_prompt(template_name)`：加载指定的提示词模板。
- `replace_variables(prompt, variables)`：替换提示词中的变量。

### 2. 上下文管理工具 (`context_manager.py`)

**功能描述**：

- 负责上下文管理，通过知识图谱（KG）管理上下文信息。
- **构建上下文字符串**：确保生成内容的连贯性。
- **更新上下文**：在执行知识图谱数据的增删改操作时，自动更新上下文。

**提供的接口**：

- `build_context(kg_data, project_name)`：根据知识图谱数据构建上下文字符串。
- `update_context(kg_data, project_name)`：更新上下文信息。

### 3. 文件管理工具 (`file_manager.py`)

**功能描述**：

- 提供文件管理工具方法。
- **创建文件夹**：创建指定的文件夹。
- **读取文件内容**：读取指定文件的内容。
- **保存文件内容**：将内容保存到指定文件。
- **删除文件**：删除指定文件。

**提供的接口**：

- `create_folder(folder_path)`：创建文件夹。
- `read_file(file_path)`：读取文件内容。
- `write_file(file_path, content)`：保存文件内容。
- `delete_file(file_path)`：删除文件。

## 六、项目依赖管理

项目依赖的第三方库包括 OpenAI 库、FastAPI 框架、edge tts 库等，通过 `requirements.txt` 文件进行管理，方便项目的安装和部署。

## 七、项目部署说明

项目部署在服务器上，配置好 FastAPI 框架和相关依赖库，设置好 LLM 和 ComfyUI 的 API 接口地址和认证信息，启动 FastAPI 服务器，即可对外提供服务。前端通过调用 API 接口与后端进行交互，实现智能创作平台的各项功能。

## 八、保存文件规则

### 图片文件名规则

- **单张图片生成**：生成的图片文件名包含种子数、日期和时间戳，格式为：`image_YYYY-MM-DD_HH-mm-SS_seed_<seed_number>.png`。例如：`image_2025-02-05_10-15-30_seed_12345.png`。
- **批量图片生成**：每张图片的文件名同样包含种子数、日期和时间戳，格式为：`image_<batch_index>_YYYY-MM-DD_HH-mm-SS_seed_<seed_number>.png`。例如：`image_0_2025-02-05_10-15-30_seed_12345.png`、`image_1_2025-02-05_10-15-30_seed_67890.png`。

### 音频文件名规则

- **单段音频生成**：生成的音频文件名包含日期和时间戳，格式为：`audio_YYYY-MM-DD_HH-mm-SS.wav`。例如：`audio_2025-02-05_10-15-30.wav`。
- **多段音频生成**：每段音频的文件名包含日期、时间戳和索引，格式为：`audio_<index>_YYYY-MM-DD_HH-mm-SS.wav`。例如：`audio_0_2025-02-05_10-15-30.wav`、`audio_1_2025-02-05_10-15-30.wav`。

## 九、总结

- 在接口设计中，种子数不再作为参数传入，而是由系统在生成图片时自动生成。这样既简化了接口调用，又确保了生成的图片文件名中包含种子数，符合项目需求。
- 接口层通过传递 `project_name`、`chapter_id` 和 `span_id`，确保生成的图片或音频文件能够正确地保存到对应的 `span` 文件夹中，便于管理和使用。
- 批量生成接口能够返回生成的进度给前端，并且可以中断生成，提高了用户体验和系统的灵活性。
- 图片和音频文件名的规则清晰明了，便于用户识别和管理生成的文件。
- 翻译功能在 `llm_service.py` 中实现，并在 `chapter_controller.py` 中提供了相应的接口，确保功能完整性和可用性。
- LLM 上下文管理通过知识图谱（KG）实现，确保生成内容的连贯性和一致性。

### 提示词系统

#### 1. 模板设计

提示词模板采用占位符设计，支持动态内容注入：

- `{tools}`：知识图谱工具的描述和参数说明
- `{scene_text}`, `{text_content}` 等：用户输入内容
- `{gender}`, `{age}`, `{role}` 等：角色属性

#### 2. 主要模板

- **novel_writing.txt**：小说创作模板，指导 LLM 进行创作并维护知识图谱
- **story_continuation.txt**：故事续写模板，确保情节连贯性
- **character_extraction.txt**：角色信息提取模板，规范化角色属性
- **character_generation.txt**：角色描述生成模板，生成适合 AI 绘图的提示词
- **scene_description.txt**：场景描述生成模板，将文本场景转换为绘图提示词

#### 3. 工具集成

- 模板中的 `{tools}` 占位符会被自动替换为最新的工具描述
- 工具描述包含：名称、功能说明、参数列表、必填参数标记
- LLM 可以根据需要自主选择合适的工具来完成任务

### KGService

知识图谱服务，提供对知识图谱的基本操作。每个项目的知识图谱都存储在独立的 JSON 文件中。

#### 主要功能

1. 实体管理

   - `inquire_entities`: 查询实体信息，支持查询单个或多个实体
   - `new_entity`: 新增单个实体
   - `modify_entity`: 修改单个实体
   - `delete_entity`: 删除单个实体
   - `inquire_entity_list`: 获取项目中的所有实体列表
   - `inquire_entity_names`: 获取项目中的所有实体名称
   - `inquire_entity_relationships`: 查询指定实体的所有关系

2. 关系管理

   - `new_relationship`: 新增单个关系
   - `modify_relationship`: 修改单个关系
   - `delete_relationship`: 删除单个关系

3. 实体锁定

   - `toggle_entity_lock`: 切换实体的锁定状态
   - `get_locked_entities`: 获取所有被锁定的实体
   - `is_entity_locked`: 检查实体是否被锁定

4. 路径查找

   - `find_paths`: 查找两个实体之间的所有可能路径

#### 数据结构

知识图谱使用 JSON 格式存储，包含以下主要字段：

```json
{
  "entities": [
    {
      "name": "实体名称",
      "attributes": {
        "key": "value"
      }
    }
  ],
  "relationships": [
    {
      "source": "源实体名称",
      "target": "目标实体名称",
      "type": "关系类型",
      "attributes": {
        "key": "value"
      }
    }
  ],
  "locked_entities": ["被锁定的实体名称"]
}
```

#### 缓存机制

为了提高性能，KGService 实现了内存缓存机制：

1. 首次访问时加载知识图谱到内存
2. 所有修改操作先更新内存中的数据
3. 调用 `save_kg` 方法时才会将更改写入文件
4. 可以通过 `save_kg` 参数控制是否在操作后立即保存到文件

### 4. 流式响应实现

在 `llm_service.py` 中，`continue_story` 和 `generate_text` 方法已被修改为支持流式输出。通过使用异步生成器，文本内容将逐步返回，前端可以实时更新显示.

```
启动 FastAPI 服务器，即可对外提供服务

```

```

```
