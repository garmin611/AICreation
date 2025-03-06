import os
import json
import time
import logging
import ssl
import asyncio
from typing import AsyncGenerator, List, Dict, Optional, Any, Tuple
from openai import OpenAI, AsyncOpenAI
import httpx
from httpx import Timeout
from server.services.kg_service import KGService
from .base_service import SingletonService
import re

# 配置日志输出
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # 输出到控制台
    ]
)

logger = logging.getLogger(__name__)

class LLMService(SingletonService):
    """LLM服务类"""
    
    # 类变量，用于缓存提示词模板
    _prompt_cache: Dict[str, str] = {}

    def _initialize(self):
     
        self.api_key = self.config['llm']['api_key']
        self.api_url = self.config['llm']['api_url']
        self.model_name = self.config['llm']['model_name']
        self.prompts_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'prompts')
        self.projects_path = self.config.get('projects_path', 'projects/')
        self.kg_service = KGService()
        
        # 配置HTTP客户端参数
        transport_params = {
            "retries": 3,  # 增加重试次数
        }

        # 根据配置决定是否验证SSL
        verify_ssl = self.config['llm'].get('verify_ssl', False)
        if isinstance(verify_ssl, bool) and not verify_ssl:
            transport_params["verify"] = False
        elif isinstance(verify_ssl, str):
            # 如果是证书路径，创建SSL上下文
            ssl_context = ssl.create_default_context()
            ssl_context.load_verify_locations(cafile=verify_ssl)
            transport_params["verify"] = ssl_context

        # 创建同步和异步的HTTP客户端
        timeout_config = Timeout(120.0, connect=30.0, read=90.0)  # 增加超时时间
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.api_url,
            http_client=httpx.Client(
                transport=httpx.HTTPTransport(**transport_params),
                proxies=self.config['llm'].get('proxies'),
                timeout=timeout_config
            )
        )
        
        # 创建异步客户端，yo
        self.async_client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.api_url,
            http_client=httpx.AsyncClient(
                transport=httpx.AsyncHTTPTransport(**transport_params),
                proxies=self.config['llm'].get('proxies'),
                timeout=timeout_config
            )
        )
    
    def _load_prompt(self, prompt_file: str) -> str:
        """加载提示词模板，优先从缓存中获取"""
        # 先从缓存中查找
        if prompt_file in self._prompt_cache:
            return self._prompt_cache[prompt_file]
            
        # 缓存中没有，从文件读取
        prompt_path = os.path.join(self.prompts_dir, prompt_file)
        if not os.path.exists(prompt_path):
            raise FileNotFoundError(f'提示词模板不存在：{prompt_file}')
        
        with open(prompt_path, 'r', encoding='utf-8') as f:
            prompt = f.read()
            
        # 存入缓存
        self._prompt_cache[prompt_file] = prompt
        return prompt
    
    def _make_api_request(self, messages: List[dict], tools: Optional[List[dict]] = None,force_json: bool = False) -> dict:
        """
        调用LLM API，包含更好的错误处理
        
        参数:
            messages (List[dict]): 对话消息列表
            tools (Optional[List[dict]]): 可用工具列表
            
        返回:
            dict: LLM响应
            
        异常:
            Exception: 各种类型的异常
        """
        max_retries = 3
        retry_count = 0
        last_error = None
        
        while retry_count < max_retries:
            try:
                kwargs = {
                    'model': self.model_name,
                    'messages': messages,
                    'temperature': 0.7,
                    'stream': False,
                    'timeout': 90  # 设置90秒超时
                }

                if force_json:
                    kwargs["response_format"] = {"type": "json_object"}
                
                if tools:
                    kwargs['tools'] = tools
                    kwargs['tool_choice'] = 'auto'

                logger.debug(f"发生请求到 {self.api_url} ，调用模型： {self.model_name}")
                response = self.client.chat.completions.create(**kwargs)

                if not response.choices:
                    raise Exception("API 响应中没有内容")

                message = response.choices[0].message
                if not message or (not message.content and not message.tool_calls):
                    raise Exception("API 响应中没有有效内容")

                return message

            except Exception as e:
                retry_count += 1
                last_error = str(e)
                error_msg = str(e)
                logger.warning(f"API请求失败 (尝试 {retry_count}/{max_retries}): {error_msg}")

                # 如果是速率限制错误，增加等待时间
                if "rate" in error_msg.lower():
                    wait_time = min(2 ** retry_count, 60)  # 指数退避，最大60秒
                    logger.info(f"速率限制触发，等待 {wait_time} 秒后重试")
                    time.sleep(wait_time)
                else:
                    time.sleep(retry_count * 2)  # 其他错误，逐步增加等待时间

        # 所有重试失败后抛出异常
        raise Exception(f"API请求失败，最大重试次数 ({max_retries}) 已用尽。最后一次错误: {last_error}")

    async def _make_async_api_request(self, messages: List[dict], tools: Optional[List[dict]] = None, force_json: bool = False) -> Any:
        """异步调用LLM API"""
        try:
            
            kwargs = {
                "model": self.model_name,
                "messages": messages,
                "temperature": 0.7,
                'stream': False,
                'timeout': 90  # 设置90秒超时
            }
            if force_json:
                kwargs["response_format"] = {"type": "json_object"}
            if tools:
                kwargs["tools"] = tools
            
            response = await self.async_client.chat.completions.create(**kwargs)
            
            return response
            
        except Exception as e:
            logging.error(f"调用LLM API时出错: {str(e)}")
            raise

    async def _make_async_api_request_stream(self, messages: List[dict], tools: Optional[List[dict]] = None, force_json: bool = False) -> AsyncGenerator[str, None]:
        """异步调用LLM API，返回流式响应"""
        try:
            
            kwargs = {
                "model": self.model_name,
                "messages": messages,
                "temperature": 0.7,
                'stream': True,
                'timeout': 90  # 设置90秒超时
            }
            if force_json:
                kwargs["response_format"] = {"type": "json_object"}
            if tools:
                kwargs["tools"] = tools
            
            response = await self.async_client.chat.completions.create(**kwargs)
            async for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
            
        except Exception as e:
            logging.error(f"调用LLM API时出错: {str(e)}")
            raise
    

    def _handle_function_call(self, response: dict, project_name: str) -> Tuple[str, List[dict]]:
        """
        处理函数调用响应
        
        参数:
            response (dict): LLM响应
            project_name (str): 项目ID
            
        返回:
            Tuple[str, List[dict]]: 返回处理后的结果和函数调用消息列表
        """
        messages = []
        result = None
        
        # 处理工具调用
        if hasattr(response, 'tool_calls') and response.tool_calls:
            for tool_call in response.tool_calls:
                try:
                    # 准备函数调用参数
                    function_name = tool_call.function.name
                    arguments = json.loads(tool_call.function.arguments)
                    arguments = self._prepare_function_arguments(arguments, project_name)
                    
                    logging.info(f"准备调用函数：{function_name}")
                    logging.info(f"函数参数：{arguments}")
                    
                    # 调用函数
                    function_result = getattr(self.kg_service, function_name)(**arguments)
                    logging.info(f"函数调用结果：{function_result}")
                    
                    # 记录函数调用
                    messages.append({
                        'role': 'assistant',
                        'content': None,
                        'tool_calls': [{
                            'id': tool_call.id,
                            'type': 'function',
                            'function': {
                                'name': function_name,
                                'arguments': json.dumps(arguments)
                            }
                        }]
                    })
                    
                    # 记录函数结果
                    messages.append({
                        'role': 'tool',
                        'tool_call_id': tool_call.id,
                        'content': str(function_result)
                    })
                    logging.info(f"已添加函数调用消息和结果到消息列表")
                    
                except Exception as e:
                    error_msg = f"处理工具调用时出错: {e}"
                    logging.error(error_msg)
                    logging.exception(e)  # 这会打印完整的堆栈跟踪
                    messages.append({
                        'role': 'tool',
                        'tool_call_id': tool_call.id,
                        'content': f"Error: {str(e)}"
                    })
        
        # 如果有直接的内容，使用它
        if hasattr(response, 'content') and response.content:
            logging.info(f"使用响应内容作为结果：{response.content}")
            result = response.content
            
        logging.info(f"_handle_function_call 完成，结果：{result}")
        logging.info(f"添加的消息数量：{len(messages)}")
        return result, messages
    
    def _process_llm_response(self, messages: List[dict], project_name: str, tools: List[dict]=None) -> Any:
        """
        处理 LLM 响应，包括工具调用
        
        参数:
            messages (List[dict]): 对话消息列表
            project_name (str): 项目ID
            tools (List[dict]): 可用的工具列表
            
        返回:
            Any: LLM响应结果
        """
        max_rounds = 10  # 最大工具调用轮数，防止无限循环
        current_round = 0
        result = None
        
        logging.info(f"开始处理LLM响应，项目：{project_name}")
        logging.info(f"初始消息数量：{len(messages)}")
        
        # 检查是否有工具可用
        has_tools = tools is not None and len(tools) > 0
        if has_tools:
            logging.info(f"可用工具数量：{len(tools)}")
            logging.info(f"可用工具列表：{[tool['function']['name'] for tool in tools if 'function' in tool]}")
        
        while current_round < max_rounds:
            logging.info(f"开始第 {current_round + 1} 轮处理")
            
            # 调用 LLM API
            response = self._make_api_request(messages, tools=tools)
            if not response:
                raise Exception("LLM API 请求失败")
            
            logging.info(f"LLM响应：{response}")
            if hasattr(response, 'content'):
                logging.info(f"响应内容：{response.content}")
                result = response.content
                
            # 只在有工具时才处理工具调用
            if has_tools and hasattr(response, 'tool_calls') and response.tool_calls:
                logging.info(f"工具调用数量：{len(response.tool_calls)}")
                
                # 处理工具调用
                new_result, function_messages = self._handle_function_call(response, project_name)
                
                # 如果有新的结果，更新结果
                if new_result:
                    logging.info(f"获得新结果：{new_result}")
                    result = new_result
                
                # 如果没有工具调用，结束循环
                if not function_messages:
                    logging.info("没有更多的工具调用，结束循环")
                    break
                    
                # 添加工具调用消息到对话历史
                messages.extend(function_messages)
                logging.info(f"添加了 {len(function_messages)} 条新消息，当前消息总数：{len(messages)}")
                current_round += 1
            else:
                # 没有工具调用，直接结束循环
                break
            
        return result

    def _prepare_function_arguments(self, arguments: dict, project_name: str) -> dict:
        """
        准备函数参数，始终使用传入的 project_name
        
        参数:
            arguments (dict): 原始函数参数
            project_name (str): 要使用的项目ID
            
        返回:
            dict: 更新后的参数
        """
        # 始终使用传入的 project_name 覆盖参数中的值
        arguments['project_name'] = project_name
        return arguments

    async def _process_text_chunk_async(self, text: str) -> list:
        """异步处理单个文本块"""
        try:
            chunk_preview = text[:50] + "..." if len(text) > 50 else text

            system_prompt = self._load_prompt('text_splitting.txt')
            messages = [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': text}
            ]
            
            response = await self._make_async_api_request(messages, force_json=True)
            result = response.choices[0].message.content
            
            # 解析结果
            if isinstance(result, str):
                try:
                    data = json.loads(result)
                    if isinstance(data, dict) and "spans" in data:
                        spans = []
                        for span in data["spans"]:
                            spans.append({
                                "content": span["content"],
                                "scene": span["scene"]
                            })
                        logging.info(f"文本块处理完成，生成了 {len(spans)} 个场景")
                        return spans
                except json.JSONDecodeError:
                    logging.error(f"JSON解析失败: {result}")
                    return [{"content": text, "scene": "", "error": "JSON解析失败"}]
            
            logging.error(f"LLM响应格式错误: {result}")
            return [{"content": text, "scene": "", "error": "LLM响应格式错误"}]
            
        except Exception as e:
            logging.error(f"处理文本块时出错: {str(e)}")
            return [{"content": text, "scene": "", "error": str(e)}]

    async def split_text_and_generate_prompts(self, project_name: str, text: str) -> List[dict]:
        """
        分割文本并生成描述词

        Args:
            project_name: 项目名称
            text: 要分割的文本

        Returns:
            List[dict]: 包含文本段落和对应描述词的列表
        """
        # 从配置文件读取 window_size
        window_size = self.config['llm'].get('window_size', -1)

        # 初始化 text_chunks 列表
        text_chunks = []

        # 如果 window_size <= 0，直接处理整个文本
        if window_size <= 0:
            # 不使用滑动窗口，整个文本一次性处理
            text_chunks = [text]
            logging.info("使用整体文本处理模式")
        else:
            # 使用滑动窗口来保持上下文连贯性
            paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
            OVERLAP_PARAGRAPHS = 1  # 与前后块重叠的段落数
            logging.info(f"使用滑动窗口处理模式，窗口大小: {window_size}，重叠段落数: {OVERLAP_PARAGRAPHS}")

            i = 0
            while i < len(paragraphs):
                # 获取当前窗口的段落
                window_end = min(i + window_size, len(paragraphs))
                current_paragraphs = paragraphs[i:window_end]

                # 如果不是第一个块，添加前文上下文
                if i > 0:
                    context_start = max(0, i - OVERLAP_PARAGRAPHS)
                    current_paragraphs = paragraphs[context_start:i] + current_paragraphs

                # 如果不是最后一个块，添加后文上下文
                if window_end < len(paragraphs):
                    context_end = min(len(paragraphs), window_end + OVERLAP_PARAGRAPHS)
                    current_paragraphs = current_paragraphs + paragraphs[window_end:context_end]

                # 合并段落
                chunk_text = "\n".join(current_paragraphs)
                text_chunks.append(chunk_text)

                # 移动窗口，但不包括重叠部分
                i += window_size - OVERLAP_PARAGRAPHS

        logging.info(f"文本已分割为 {len(text_chunks)} 个块")

        # 使用异步并行处理所有文本块
        async def process_all_chunks():
            tasks = [self._process_text_chunk_async(chunk) for chunk in text_chunks]
            results = await asyncio.gather(*tasks)

            # 如果使用了滑动窗口，需要去重
            if window_size > 0:
                seen_scenes = set()
                unique_results = []
                for sublist in results:
                    for item in sublist:
                        scene_content = item["content"]
                        if scene_content not in seen_scenes:
                            seen_scenes.add(scene_content)
                            unique_results.append(item)
                return unique_results
            else:
                # 不使用滑动窗口时，直接返回第一个（也是唯一的）结果
                return results[0]  # results[0] 已经是一个列表了，因为 _process_text_chunk_async 返回列表

        # 调用异步函数并等待结果
        try:
            results = await process_all_chunks()
            logging.info(f"文本处理完成，生成了 {len(results)} 个场景")
            return results
        except Exception as e:
            logging.error(f"分割文本时发生错误：{str(e)}")
            raise

    def get_chapter_content(self, project_name: str, chapter_name: str) -> str:
        """
        获取指定章节的content.txt文件内容
        
        参数:
            project_name (str): 项目名称
            chapter_name (str): 章节名称，例如 'chapter6'
            
        返回:
            str: 章节内容，如果文件不存在则返回空字符串
        """
        try:
            chapter_path = os.path.join(self.projects_path, project_name, chapter_name)
            content_path = os.path.join(chapter_path, 'content.txt')
            if os.path.exists(content_path):
                with open(content_path, 'r', encoding='utf-8') as f:
                    return f.read()
            return ''
        except Exception as e:
            logger.error(f"Error reading chapter content: {e}")
            return ''

    async def generate_text(self, prompt: str, project_name: str, last_content: str = '') -> AsyncGenerator[str, None]:
        """生成文本"""
        if not prompt:
            raise ValueError("提示词不能为空")
        
        try:
                
            # 加载并填充提示词模板
            system_prompt = self._load_prompt('novel_writing.txt')
            system_prompt = system_prompt.replace('{context}', last_content)
            system_prompt = system_prompt.replace('{requirements}', prompt)
            
            messages = [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': prompt}
            ]
            # 使用async for直接迭代异步生成器
            async for text in self._make_async_api_request_stream(messages):
                yield text
        except asyncio.CancelledError:
            logger.info("生成任务被取消")
            raise
        finally:
            # 执行必要的资源清理
            logger.info("生成器资源已释放")

    async def continue_story(self, original_story: str, project_name: str, last_content: str = '') -> AsyncGenerator[str, None]:
        """续写故事"""
        
        if not original_story:
            raise ValueError("故事内容不能为空")

        try:  
            system_prompt = self._load_prompt('story_continuation.txt')
            system_prompt = system_prompt.replace('{context}', last_content)
            
            messages = [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': original_story}
            ]
            async for text in self._make_async_api_request_stream(messages):
                yield text
        except asyncio.CancelledError:
            logger.info("续写任务被取消")
            raise
        finally:
            logger.info("续写生成器资源已释放")

    def extract_character(self, text: str, project_name: str) -> dict:
        """
        从文本中提取人物信息

        参数:
            text (str): 待提取的文本
            project_name (str): 项目名称

        返回:
            dict: 提取结果，包含添加到知识图谱的信息
        """
        if not text:
            raise ValueError("文本内容不能为空")
            
        # 加载并填充提示词模板
        system_prompt = self._load_prompt('character_extraction.txt')
        
        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': text}
        ]
        
        # 获取知识图谱工具
        tools = self.kg_service.get_tools()
        
        # 使用通用的处理方法处理响应
        result = self._process_llm_response(messages, project_name, tools=tools)
        
        # 查询所有实体
        entities = self.kg_service.inquire_entity_list(project_name=project_name)
        if isinstance(entities, str):
            entities = json.loads(entities)
        
        # 收集所有实体的关系
        relationships = {}
        for entity in entities:
            if isinstance(entity, dict) and 'name' in entity:
                entity_name = entity['name']
                entity_relationships = self.kg_service.inquire_entity_relationships(
                    project_name=project_name,
                    name=entity_name
                )
                if isinstance(entity_relationships, str):
                    entity_relationships = json.loads(entity_relationships)
                relationships[entity_name] = entity_relationships
        
        # 所有处理完成后，保存知识图谱
        self.kg_service.save_kg(project_name)
        
        return {
            'result': result,
            'entities': entities,
            'relationships': relationships
        }

    async def _translate_prompt_batch(self, project_name: str, prompts: List[str], system_prompt: str, entities: List[dict]) -> List[str]:
        """
        批量翻译提示词
        Args:
            project_name: 项目名称
            prompts: 提示词列表
            system_prompt: 系统提示词模板
            entities: 实体信息列表
        Returns:
            翻译后的提示词列表
        """
        try:
            # 收集所有提示词中的实体名称
            all_entity_names = set()
            for prompt in prompts:
                entity_names = re.findall(r'\{([^}]+)\}', prompt)
                all_entity_names.update(entity_names)
            
            # 找到对应的实体信息
            entity_infos = []
            for name in all_entity_names:
                for entity in entities:
                    if entity['name'] == name:
                        info_str = f"{entity['name']}：{entity.get('attributes', {}).get('description', '')}"
                        entity_infos.append(info_str)
                        break
            
            # 复制系统提示词并替换实体信息
            current_system_prompt = system_prompt
            if entity_infos:
                current_system_prompt = current_system_prompt.replace('{entities}', '\n'.join(entity_infos))
            
            # 将提示词分成更小的批次（每批5个）
            batch_size = 5
            translated_prompts = []
            total_batches = (len(prompts) + batch_size - 1) // batch_size
            
            for batch_index in range(total_batches):
                start_idx = batch_index * batch_size
                end_idx = min(start_idx + batch_size, len(prompts))
                batch_prompts = prompts[start_idx:end_idx]
                
                # 构建编号的提示词列表（使用实际序号）
                numbered_prompts = []
                for i, prompt in enumerate(batch_prompts, start_idx + 1):
                    numbered_prompts.append(f"{i}. {prompt}")
                prompts_str = '\n'.join(numbered_prompts)
                
                logging.info(f"处理第 {batch_index + 1}/{total_batches} 批提示词，包含 {len(batch_prompts)} 个提示词")
                logging.info(f"当前编号的提示词列表：\n{prompts_str}")
                
                # 构建消息列表
                messages = [
                    {'role': 'system', 'content': current_system_prompt},
                    {'role': 'user', 'content': prompts_str}
                ]
                
                # 调用 LLM API
                response = await self._make_async_api_request(messages)
                if not response or not response.choices or not response.choices[0].message.content:
                    raise Exception("LLM返回了空的响应")
                
                # 解析响应
                result = response.choices[0].message.content.strip()
                batch_results = []
                
                # 使用正则表达式匹配编号的提示词
                pattern = r'^\d+\.\s*(.+)$'
                for line in result.split('\n'):
                    line = line.strip()
                    if line:
                        match = re.match(pattern, line)
                        if match:
                            batch_results.append(match.group(1).strip())
                
                # 确保当前批次的翻译结果数量正确
                if len(batch_results) != len(batch_prompts):
                    raise Exception(f"批次 {batch_index + 1} 的翻译结果数量 ({len(batch_results)}) 与输入数量 ({len(batch_prompts)}) 不匹配")
                
                translated_prompts.extend(batch_results)
                
                # 在批次之间添加短暂延迟，避免触发速率限制
                if batch_index < total_batches - 1:
                    await asyncio.sleep(0.5)
            
            # 最终验证
            if len(translated_prompts) != len(prompts):
                raise Exception(f"总翻译结果数量 ({len(translated_prompts)}) 与输入数量 ({len(prompts)}) 不匹配")
            
            return translated_prompts
            
        except Exception as e:
            logging.error(f'批量翻译提示词失败: {str(e)}')
            raise

    async def translate_prompt(self, project_name: str, prompts: List[str]) -> List[str]:
        """
        翻译提示词列表
        Args:
            project_name: 项目名称
            prompts: 提示词列表
        Returns:
            翻译后的提示词列表
        """
        try:
            # 加载系统提示词
            system_prompt = self._load_prompt('prompt_translation.txt')

            # 从知识图谱中获取所有实体信息
            entities_json = self.kg_service.inquire_entity_list(project_name)
            entities = json.loads(entities_json)

            # 将提示词列表按每10个一组进行切分
            batch_size = 10
            batches = [prompts[i:i + batch_size] for i in range(0, len(prompts), batch_size)]

            # 并行处理每个批次
            tasks = []
            for batch in batches:
                tasks.append(self._translate_prompt_batch(project_name, batch, system_prompt, entities))

            # 执行所有任务
            results = await asyncio.gather(*tasks)

            # 将所有批次的结果合并
            translated_prompts = []
            for batch_result in results:
                translated_prompts.extend(batch_result)

            return translated_prompts

        except Exception as e:
            logging.error(f'翻译提示词失败: {str(e)}')
            raise

    def get_latest_chapter(self, project_path: str) -> int:
        """获取最新章节编号"""
        if not os.path.exists(project_path):
            raise Exception(f"项目路径不存在: {project_path}")
            
        chapters = [d for d in os.listdir(project_path) 
                   if os.path.isdir(os.path.join(project_path, d)) 
                   and d.startswith("chapter")]
        if not chapters:
            return 1
            
        latest = max(int(ch.replace("chapter", "")) for ch in chapters)
        return latest

    def generate_span_files(self, project_name: str, chapter_name: str, spans_and_prompts: List[dict]) -> None:
        """
        为每个文本片段生成对应的文件

        Args:
            project_name: 项目名称
            chapter_name: 章节名称
            spans_and_prompts: 包含文本片段和场景描述的列表
            
        Raises:
            Exception: 当章节目录不存在时抛出
        """
        try:
            # 构建章节目录路径
            chapter_dir = os.path.join('projects', project_name,  chapter_name)
            
            # 如果章节目录不存在，直接返回
            if not os.path.exists(chapter_dir):
                raise Exception(f"章节目录不存在: {chapter_dir}")
            
            # 清空现有的子文件夹
            for item in os.listdir(chapter_dir):
                item_path = os.path.join(chapter_dir, item)
                if os.path.isdir(item_path) and item.isdigit():  # 只删除数字命名的文件夹
                    import shutil
                    shutil.rmtree(item_path)
            
            # 为每个片段创建文件
            for i, span in enumerate(spans_and_prompts):
                span_dir = os.path.join(chapter_dir, str(i+1))
                os.makedirs(span_dir, exist_ok=True)
                
                # 写入span.txt
                with open(os.path.join(span_dir, 'span.txt'), 'w', encoding='utf-8') as f:
                    f.write(span['content'])
                
                # 写入prompt.json
                prompt_data = {
                    'scene': span['scene'],
                    'prompt': ''  # 默认为空
                }
                with open(os.path.join(span_dir, 'prompt.json'), 'w', encoding='utf-8') as f:
                    json.dump(prompt_data, f, ensure_ascii=False, indent=2)
                    
            logging.info(f"已为章节 {chapter_name} 生成 {len(spans_and_prompts)} 个场景文件")
            
        except Exception as e:
            logging.error(f"生成场景文件时出错: {str(e)}")
            raise e
