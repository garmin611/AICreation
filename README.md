# 项目开发需求描述

## 一、功能概述

本项目致力于打造一个融合大语言模型（LLM）与 ComfyUI 的智能创作平台，主要面向小说创作者、插画师以及 AI 生成内容开发者等群体。该平台能够助力用户快速生成创意文本，并结合 AI 技术实现图像生成。其中，LLM 的调用将通过类似 OpenAI 的 API 接口来完成，后端部分则采用 Python 的 Flask 框架搭建服务器，其职责是与 ComfyUI 服务器进行交互，并对外提供相应的 API 接口。平台生成的内容以文件夹形式存储，便于管理和扩展。

## 二、项目结构及功能规划

### 项目分层结构

项目采用分层架构设计，主要包括以下几个层次：

1. **API 接口层（controller）** ：负责处理前端请求，对外提供统一的 API 接口，进行参数校验和请求转发，返回处理结果给前端。
2. **业务逻辑层（service）** ：封装具体的业务逻辑，包括文本生成、图像生成、知识图谱管理等功能，调用数据访问层和工具类来完成业务处理。
3. **工具类（utils）** ：提供一些通用的工具方法，如提示词管理、上下文管理、音频生成等。

### 项目文件结构

**复制**

```
project/
├── config/                   # 配置文件夹
│   ├── config.py             # 配置文件操作接口
│   └── config.yaml           # 系统配置文件
├── controllers/              # API 接口层
│   ├── project_controller.py # 项目管理相关接口
│   ├── chapter_controller.py # 章节管理相关接口
│   ├── media_controller.py   # 媒体生成相关接口
│   └── admin_controller.py   # 系统管理接口（包括配置文件修改）
├── services/                 # 业务逻辑层
│   ├── llm_service.py        # LLM 相关业务逻辑
│   ├── image_service.py      # 图像生成相关业务逻辑
│   ├── kg_service.py         # 知识图谱管理相关业务逻辑
│   └── audio_service.py      # 音频生成相关业务逻辑
├── utils/                    # 工具类
│   ├── prompt_manager.py     # 提示词管理工具
│   ├── context_manager.py    # 上下文管理工具
│   └── file_manager.py       # 文件管理工具
├── projects/                 # 项目文件夹
│   ├── project1/             # 具体项目文件夹
│   │   ├── kg.json           # 知识图谱数据文件
│   │   ├── scenes.json           # 基底场景数据文件
│   │   ├── chapters/         # 章节文件夹
│   │   │   ├── chapter1/     # 章节文件夹
│   │   │   │   ├── 0/        # 子文件夹
│   │   │   │   │   ├── span.txt
│   │   │   │   │   ├── prompt.txt
│   │   │   │   │   ├── image_2025-02-05_10-15-30_seed_12345.png
│   │   │   │   │   └── audio_2025-02-05_10-15-30.wav
│   │   │   │   ├── 1/        # 子文件夹
│   │   │   │   └── ...       # 其他子文件夹
│   │   │   └── ...           # 其他章节文件夹
│   │   ├── prompts/          # 提示词模板文件夹
│   │   └── ...               # 其他项目相关文件
├── prompts/                  # 提示词模板文件夹
│   ├── novel_writing.txt     # 小说写作提示词模板
│   ├── character_generation.txt # 人物生成提示词模板
│   └── ...                   # 其他提示词模板
└── workflow/                 # ComfyUI 生图工作流文件夹
    └── ...                   # 各种工作流文件
```

## 三、各脚本功能及接口说明

### API 接口层（controller）

#### 1. `project_controller.py`

**功能描述** ：

- 提供与项目管理相关的 API 接口，包括创建项目、查询项目信息等功能。

**提供的接口** ：

- **创建项目** ：
  - `POST /api/project/create` ：创建一个新的项目。
  - 接收参数：`project_name`（字符串，项目名称）。
- **查询项目信息** ：
  - `GET /api/project/info` ：查询指定项目的详细信息。
  - 接收参数：`project_name`（字符串，项目 ID）。
- **查询知识图谱** ：
  - `GET /api/project/kg` ：查询指定项目的知识图谱数据。
  - 接收参数：`project_name`（字符串，项目 ID）。

#### 2. `chapter_controller.py`

**功能描述** ：

- 提供与章节管理相关的 API 接口，包括生成章节内容、查询章节信息等功能。

**提供的接口** ：

- **生成章节内容** ：
  - `POST /api/chapter/generate` ：根据给定的提示词生成章节内容。
  - 接收参数：`prompt`（字符串，提示词）、`project_name`（字符串，项目 ID）。
- **查询最新章节** ：
  - `GET /api/chapter/latest` ：查询指定项目的最新章节序号。
  - 接收参数：`project_name`（字符串，项目 ID）。
- **切割文本并生成提示词** ：
  - `POST /api/chapter/split-text` ：将一章小说内容进行切割并生成提示词。
  - 接收参数：`text`（字符串，小说内容）、`project_name`（字符串，项目 ID）。
- **翻译提示词** ：
  - `POST /api/chapter/translate-prompt` ：将中文提示词翻译为英文提示词。
  - 接收参数：`prompt`（字符串，中文提示词）、`project_name`（字符串，项目 ID）。

#### 3. `media_controller.py`

**功能描述** ：

- 提供与媒体生成相关的 API 接口，包括生成图像、音频等功能，并确保生成的文件保存到指定的 `span` 文件夹中。

**提供的接口** ：

- **图像生成接口** ：
  - `POST /api/media/generate-image` ：根据传入的提示词、工作流以及项目、章节、span 信息生成单张图片并保存到指定的 span 文件夹中。系统自动生成种子数，并将其附加上图片文件名中。
  - 接收参数：
    - `prompt`（字符串，提示词）
    - `workflow`（字符串，工作流名称）
    - `project_name`（字符串，项目 ID）
    - `chapter_id`（字符串，章节 ID）
    - `span_id`（字符串，span ID）
- **批量图像生成接口** ：
  - `POST /api/media/generate-images-batch` ：根据传入的提示词列表、工作流以及项目、章节、span 信息生成多张图片并保存到指定的 span 文件夹中。系统为每张图片自动生成种子数，并附加上图片文件名中。批量生成时，需返回生成的进度给前端，并且可以中断生成。
  - 接收参数：
    - `prompts`（列表，提示词列表）
    - `workflow`（字符串，工作流名称）
    - `project_name`（字符串，项目 ID）
    - `chapter_id`（字符串，章节 ID）
    - `span_id`（字符串，span ID）
- **音频生成接口** ：
  - `POST /api/media/generate-audio` ：根据传入的 `span` 文本以及项目、章节、span 信息生成相应的音频文件并保存到指定的 span 文件夹中。
  - 接收参数：
    - `span_text`（字符串，文本内容）
    - `project_name`（字符串，项目 ID）
    - `chapter_id`（字符串，章节 ID）
    - `span_id`（字符串，span ID）
- **批量音频生成接口** ：
  - `POST /api/media/generate-audios-batch` ：根据传入的多段文本以及项目、章节、span 信息生成多段音频并保存到指定的 span 文件夹中。
  - 接收参数：
    - `span_texts`（列表，文本内容列表）
    - `project_name`（字符串，项目 ID）
    - `chapter_id`（字符串，章节 ID）
    - `span_id`（字符串，span ID）
- **获取生成进度** ：
  - `GET /api/media/generation-progress` ：获取当前生成任务的进度。
  - 接收参数：
    - `project_name`（字符串，项目 ID）
    - `chapter_id`（字符串，章节 ID）
    - `span_id`（字符串，span ID）
- **中断生成任务** ：
  - `POST /api/media/cancel-generation` ：中断当前生成任务。
  - 接收参数：
    - `project_name`（字符串，项目 ID）
    - `chapter_id`（字符串，章节 ID）
    - `span_id`（字符串，span ID）

#### 4. `admin_controller.py`

**功能描述** ：

- 提供系统管理相关的 API 接口，包括修改配置文件、获取配置文件内容等功能。

**提供的接口** ：

- **修改配置文件** ：
  - `POST /api/admin/config` ：修改配置文件中的一项或多项设置。
  - 接收参数：`config_key`（字符串，配置项的键）、`config_value`（字符串，配置项的新值）。
- **获取配置文件** ：
  - `GET /api/admin/config` ：获取当前的配置文件内容，以 JSON 格式返回。
  - 接收参数：无。

## 四、业务逻辑层（service）

#### 1. `llm_service.py`

**功能描述** ：

- 实现与 LLM 的交互，提供文本生成相关的业务逻辑。
- **AI 写作与续写** ：根据给定的初始内容或上下文，生成连贯且富有创意的文本内容。
- **人物提取与提示词生成** ：从小说文本中提取人物信息，并生成可用于 AI 生图的人物提示词，提示词需包含性别、年龄、外貌、性格特征等信息，且要符合 ComfyUI 的生图要求。
- **获取最新章节序号** ：检查当前项目文件夹中，最新生成的章节的序号。
- **文本切割与画面提示词生成** ：将输入的一章小说内容进行分割，生成多个 `[span]` ，每个 `[span]` 表示一段内容，并为每个 `[span]` 生成对应的画面提示词 `prompt` ，同时处理人物的提示词，以便后续图像生成。切割后的所有 `span` 和对应的提示词存入最新章节文件夹。
- **翻译功能** ：将用户设计的中文提示词翻译为适合 AI 生图的英文提示词。
- **上下文管理** ：通过知识图谱（KG）管理上下文信息，确保生成内容的连贯性。

**提供的接口** ：

- `generate_text(prompt, project_name)` ：根据给定的提示词生成文本。
- `continue_story(text, project_name)` ：根据已有的文本续写故事。
- `extract_character(text, project_name)` ：从小说文本中提取人物信息。
- `generate_character_prompt(character_info, project_name)` ：根据人物信息生成提示词。
- `get_latest_chapter(project_name)` ：获取指定项目中的最新章节序号。
- `split_text_and_generate_prompts(text, project_name)` ：将文本切割并生成提示词，保存到指定项目文件夹中。
- `translate_prompt(prompt, project_name)` ：将中文提示词翻译为英文提示词。
- `build_context(kg_data, project_name)` ：根据知识图谱数据构建上下文字符串。

#### 2. `image_service.py`

**功能描述** ：

- 负责与 ComfyUI 交互，提供图像生成相关的业务逻辑。
- **图片生成接口** ：根据传入的提示词、工作流和项目、章节、span 信息，生成单张图片并保存到指定的 span 文件夹中。系统自动生成种子数，并将其附加上图片文件名中。
- **批量图片生成接口** ：根据传入的提示词列表、工作流和项目、章节、span 信息，生成多张图片并保存到指定的 span 文件夹中。系统为每张图片自动生成种子数，并附加上图片文件名中。批量生成时，需返回生成的进度给前端，并且可以中断生成。

**提供的接口** ：

- `generate_image(prompt, workflow, project_name, chapter_id, span_id)` ：根据提示词、工作流生成单张图片，并保存到指定的 span 文件夹中。系统自动生成种子数，并将其附加上图片文件名中。
- `generate_images_batch(prompts, workflow, project_name, chapter_id, span_id)` ：根据提示词列表、工作流生成多张图片，并保存到指定的 span 文件夹中。系统为每张图片自动生成种子数，并附加上图片文件名中。批量生成时，需返回生成的进度给前端，并且可以中断生成。
- `get_generation_progress(project_name, chapter_id, span_id)` ：获取当前生成任务的进度。
- `cancel_generation(project_name, chapter_id, span_id)` ：中断当前生成任务。

#### 3. `kg_service.py`

**功能描述** ：

- 实现知识图谱（KG）功能，提供知识图谱的管理接口。
- **查询实体节点** ：可根据给定的条件或关键词，查询知识图谱中的实体节点信息。
- **查询关系边** ：查询实体之间存在的关系边的详细信息。
- **查询已存在实体连接的所有关系边** ：针对某个特定实体，查询其与其他所有实体之间的关系边。
- **查询所有实体节点名称** ：获取知识图谱中所有实体节点的名称列表。
- **修改实体节点** ：提供接口用于修改知识图谱中已存在的实体节点信息。
- **删除实体节点** ：实现删除指定实体节点的功能。
- **新建实体节点** ：允许在知识图谱中添加新的实体节点。知识图谱的内容以 JSON 格式保存在 `projects/` 文件夹对应项目的文件夹下，以便于不同项目之间知识图谱数据的独立存储和管理。

**提供的接口** ：

- `query_entity(condition, project_name)` ：根据条件查询实体节点。
- `query_relationship(entity1, entity2, project_name)` ：查询两个实体之间的关系边。
- `query_all_relationships(entity, project_name)` ：查询指定实体与其他所有实体的关系边。
- `get_all_entity_names(project_name)` ：获取所有实体节点的名称列表。
- `update_entity(entity, project_name)` ：修改指定实体节点的信息。
- `delete_entity(entity, project_name)` ：删除指定实体节点。
- `create_entity(entity, project_name)` ：新建实体节点。

#### 4. `audio_service.py`

**功能描述** ：

- 负责音频生成相关的业务逻辑。
- **音频生成接口** ：根据传入的 `span` 文本和项目、章节、span 信息生成相应的音频文件，并保存到指定的 span 文件夹中。
- **批量音频生成接口** ：根据传入的多段文本和项目、章节、span 信息生成多段音频，并保存到指定的 span 文件夹中。批量生成时，需返回生成的进度给前端，并且可以中断生成。

**提供的接口** ：

- `generate_audio(span_text, project_name, chapter_id, span_id)` ：根据指定的文本生成音频文件并保存到指定的 span 文件夹中。
- `generate_audios_batch(span_texts, project_name, chapter_id, span_id)` ：根据多段文本生成多段音频并保存到指定的 span 文件夹中。
- `get_generation_progress(project_name, chapter_id, span_id)` ：获取当前生成任务的进度。
- `cancel_generation(project_name, chapter_id, span_id)` ：中断当前生成任务。

## 五、工具类（utils）

#### 1. `prompt_manager.py`

**功能描述** ：

- 提供提示词管理功能。
- **加载提示词模板** ：从 `prompts/` 文件夹中加载提示词模板。
- **替换提示词中的变量** ：实现提示词的动态更新，以适应不同的创作需求。

**提供的接口** ：

- `load_prompt(template_name)` ：加载指定的提示词模板。
- `replace_variables(prompt, variables)` ：替换提示词中的变量。

#### 2. `context_manager.py`

**功能描述** ：

- 负责上下文管理，通过知识图谱（KG）管理上下文信息。
- **构建上下文字符串** ：确保生成内容的连贯性。
- **更新上下文** ：在执行知识图谱数据的增删改操作时，自动更新上下文。

**提供的接口** ：

- `build_context(kg_data, project_name)` ：根据知识图谱数据构建上下文字符串。
- `update_context(kg_data, project_name)` ：更新上下文信息。

#### 3. `file_manager.py`

**功能描述** ：

- 提供文件管理工具方法。
- **创建文件夹** ：创建指定的文件夹。
- **读取文件内容** ：读取指定文件的内容。
- **保存文件内容** ：将内容保存到指定文件。
- **删除文件** ：删除指定文件。

**提供的接口** ：

- `create_folder(folder_path)` ：创建文件夹。
- `read_file(file_path)` ：读取文件内容。
- `write_file(file_path, content)` ：保存文件内容。
- `delete_file(file_path)` ：删除文件。

## 六、项目依赖管理

项目依赖的第三方库包括 OpenAI 库、Flask 框架、edge tts 库等，通过 `requirements.txt` 文件进行管理，方便项目的安装和部署。

## 七、项目部署说明

项目部署在服务器上，配置好 Flask 框架和相关依赖库，设置好 LLM 和 ComfyUI 的 API 接口地址和认证信息，启动 Flask 服务器，即可对外提供服务。前端通过调用 API 接口与后端进行交互，实现智能创作平台的各项功能。

## 八、保存文件规则

### 图片文件名规则

- **单张图片生成** ：生成的图片文件名包含种子数、日期和时间戳，格式为：`image_YYYY-MM-DD_HH-mm-SS_seed_<seed_number>.png`。例如：`image_2025-02-05_10-15-30_seed_12345.png`。
- **批量图片生成** ：每张图片的文件名同样包含种子数、日期和时间戳，格式为：`image_<batch_index>_YYYY-MM-DD_HH-mm-SS_seed_<seed_number>.png`。例如：`image_0_2025-02-05_10-15-30_seed_12345.png`、`image_1_2025-02-05_10-15-30_seed_67890.png`。

### 音频文件名规则

- **单段音频生成** ：生成的音频文件名包含日期和时间戳，格式为：`audio_YYYY-MM-DD_HH-mm-SS.wav`。例如：`audio_2025-02-05_10-15-30.wav`。
- **多段音频生成** ：每段音频的文件名包含日期、时间戳和索引，格式为：`audio_<index>_YYYY-MM-DD_HH-mm-SS.wav`。例如：`audio_0_2025-02-05_10-15-30.wav`、`audio_1_2025-02-05_10-15-30.wav`。

## 九、总结

- 在接口设计中，种子数不再作为参数传入，而是由系统在生成图片时自动生成。这样既简化了接口调用，又确保了生成的图片文件名中包含种子数，符合项目需求。
- 接口层通过传递 `project_name`、`chapter_id` 和 `span_id`，确保生成的图片或音频文件能够正确地保存到对应的 `span` 文件夹中，便于管理和使用。
- 批量生成接口能够返回生成的进度给前端，并且可以中断生成，提高了用户体验和系统的灵活性。
- 图片和音频文件名的规则清晰明了，便于用户识别和管理生成的文件。
- 翻译功能在 `llm_service.py` 中实现，并在 `chapter_controller.py` 中提供了相应的接口，确保功能完整性和可用性。
- LLM 上下文管理通过知识图谱（KG）实现，确保生成内容的连贯性和一致性。
