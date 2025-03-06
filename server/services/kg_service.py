import os
import json
from server.config.config import load_config
from typing import Dict, List, Optional, Any, Tuple
from collections import deque
from .base_service import SingletonService

# 基础工具定义，用于角色提取
TOOLS_BASE = [
    {
        "type": "function",
        "function": {
            "name": "inquire_entities",
            "description": "用于查询单个或多个实体节点的详细信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_name": {
                        "type": "string",
                        "description": "项目ID"
                    },
                    "names": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "description": "实体的名称"
                        },
                        "description": "实体名称列表"
                    }
                },
                "required": ["project_name", "names"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "new_entity",
            "description": "用于添加新的实体节点",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_name": {
                        "type": "string",
                        "description": "项目ID"
                    },
                    "name": {
                        "type": "string",
                        "description": "实体的名称"
                    },
                    "attributes": {
                        "type": "object",
                        "description": "实体的属性",
                        "properties": {
                            "role": {
                                "type": "string",
                                "description": "角色职责"
                            },
                            "description": {
                                "type": "string",
                                "description": "英文视觉描述"
                            }
                        }
                    }
                },
                "required": ["project_name", "name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "modify_entity",
            "description": "用于修改已存在的实体节点的属性",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_name": {
                        "type": "string",
                        "description": "项目ID"
                    },
                    "name": {
                        "type": "string",
                        "description": "实体的名称"
                    },
                    "attributes": {
                        "type": "object",
                        "description": "实体的新属性",
                        "properties": {
                            "role": {
                                "type": "string",
                                "description": "角色职责"
                            },
                            "description": {
                                "type": "string",
                                "description": "英文视觉描述"
                            }
                        }
                    }
                },
                "required": ["project_name", "name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "inquire_relationship",
            "description": "用于查询两个实体之间的关系",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_name": {
                        "type": "string",
                        "description": "项目ID"
                    },
                    "entity_a": {
                        "type": "string",
                        "description": "第一个实体的名称"
                    },
                    "entity_b": {
                        "type": "string",
                        "description": "第二个实体的名称"
                    }
                },
                "required": ["project_name", "entity_a", "entity_b"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "new_relationship",
            "description": "用于添加新的关系边",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_name": {
                        "type": "string",
                        "description": "项目ID"
                    },
                    "type": {
                        "type": "string",
                        "description": "关系类型"
                    },
                    "source": {
                        "type": "string",
                        "description": "源实体名称"
                    },
                    "target": {
                        "type": "string",
                        "description": "目标实体名称"
                    },
                    "attributes": {
                        "type": "object",
                        "description": "关系的属性"
                    }
                },
                "required": ["project_name", "type", "source", "target"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "modify_relationship",
            "description": "用于修改已存在的关系边的属性",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_name": {
                        "type": "string",
                        "description": "项目ID"
                    },
                    "type": {
                        "type": "string",
                        "description": "关系类型"
                    },
                    "source": {
                        "type": "string",
                        "description": "源实体名称"
                    },
                    "target": {
                        "type": "string",
                        "description": "目标实体名称"
                    },
                    "attributes": {
                        "type": "object",
                        "description": "关系的新属性"
                    }
                },
                "required": ["project_name", "type", "source", "target"]
            }
        }
    }
]

# 完整工具定义，包含所有功能
TOOLS = [
    # 查询类工具
    {
        "type": "function",
        "function": {
            "name": "inquire_entity_list",
            "description": "用于查询所有实体节点列表",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_name": {
                        "type": "string",
                        "description": "项目ID"
                    }
                },
                "required": ["project_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "inquire_entity_names",
            "description": "用于查询所有实体名称列表",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_name": {
                        "type": "string",
                        "description": "项目ID"
                    }
                },
                "required": ["project_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "inquire_entity_relationships",
            "description": "用于查询实体的所有关系",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_name": {
                        "type": "string",
                        "description": "项目ID"
                    },
                    "name": {
                        "type": "string",
                        "description": "实体名称"
                    }
                },
                "required": ["project_name", "name"]
            }
        }
    },
    # 修改类工具
    {
        "type": "function",
        "function": {
            "name": "delete_entity",
            "description": "用于删除实体节点",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_name": {
                        "type": "string",
                        "description": "项目ID"
                    },
                    "name": {
                        "type": "string",
                        "description": "实体的名称"
                    }
                },
                "required": ["project_name", "name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_relationship",
            "description": "用于删除关系边",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_name": {
                        "type": "string",
                        "description": "项目ID"
                    },
                    "type": {
                        "type": "string",
                        "description": "关系类型"
                    },
                    "source": {
                        "type": "string",
                        "description": "源实体名称"
                    },
                    "target": {
                        "type": "string",
                        "description": "目标实体名称"
                    }
                },
                "required": ["project_name", "type", "source", "target"]
            }
        }
    }
] + TOOLS_BASE


class KGService(SingletonService):
    def _initialize(self):
        self.kg_cache = {}  # 用于缓存已加载的知识图谱
        self.kg_dirty = {}  # 标记缓存是否被修改
        self.config = load_config()

    def _get_kg_path(self, project_name: str) -> str:

        return os.path.join(self.config['projects_path'], project_name, 'kg.json')

    def _load_kg(self, project_name: str) -> dict:
        """
        加载项目的知识图谱

        参数:
            project_name (str): 项目ID

        返回:
            dict: 知识图谱数据

        异常:
            ValueError: 如果知识图谱文件格式错误
            Exception: 其他加载错误
        """
        if project_name in self.kg_cache:
            return self.kg_cache[project_name]

        kg_path = self._get_kg_path(project_name)
        default_kg = {'entities': [], 'relationships': []}

        if not os.path.exists(kg_path):
            self.kg_cache[project_name] = default_kg
            return self.kg_cache[project_name]

        try:
            with open(kg_path, 'r', encoding='utf-8') as f:
                kg_data = json.load(f)

                # 确保数据有正确的结构
                if not isinstance(kg_data, dict):
                    raise ValueError('知识图谱数据必须是字典类型')

                # 确保必要的键存在
                kg_data.setdefault('entities', [])
                kg_data.setdefault('relationships', [])
                kg_data.setdefault('locked_entities', [])

                # 确保值的类型正确
                if not isinstance(kg_data['entities'], list):
                    raise ValueError('entities 必须是列表类型')
                if not isinstance(kg_data['relationships'], list):
                    raise ValueError('relationships 必须是列表类型')
                if not isinstance(kg_data['locked_entities'], list):
                    raise ValueError('locked_entities 必须是列表类型')

                self.kg_cache[project_name] = kg_data
                return kg_data
        except json.JSONDecodeError as e:
            raise ValueError(f'知识图谱文件格式错误: {str(e)}')
        except Exception as e:
            raise Exception(f'加载知识图谱时发生错误: {str(e)}')

    def save_kg(self, project_name: str) -> None:
        """
        保存知识图谱到文件

        参数:
            project_name (str): 项目ID
        """
        if project_name not in self.kg_cache:
            raise Exception(f"项目 {project_name} 的知识图谱未加载")

        kg_path = self._get_kg_path(project_name)
        os.makedirs(os.path.dirname(kg_path), exist_ok=True)
        kg_data = self._load_kg(project_name)
        try:
            with open(kg_path, 'w', encoding='utf-8') as f:
                json.dump(kg_data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            raise Exception(f'保存知识图谱时发生错误: {str(e)}')

    def get_tools(self, include_all: bool = False) -> List[dict]:
        """
        获取知识图谱工具列表

        参数:
            include_all (bool): 是否包含所有工具，默认只返回基础工具

        返回:
            List[dict]: 工具列表
        """
        return TOOLS if include_all else TOOLS_BASE

    '''
    下列工具函数返回的结果是str而不是其他的如bool类型等简单的结果，是为了方便LLM感知function_call结果
    '''

    def inquire_entities(self, project_name: str, names: List[str]) -> str:
        """
        查询实体信息，支持查询单个或多个实体

        参数:
            project_name (str): 项目ID
            names (List[str]): 实体名称列表

        返回:
            str: 实体信息列表的JSON字符串。
                如果查询单个实体且未找到，返回包含错误信息的字符串。
                如果查询多个实体，返回找到的实体列表，未找到的实体将被忽略。
        """
        try:
            kg_data = self._load_kg(project_name)
            entities = []
            for entity in kg_data.get('entities', []):
                if entity['name'] in names:
                    entities.append(entity)
            
            # 如果是查询单个实体且未找到，返回错误信息
            if len(names) == 1 and not entities:
                return f"实体 {names[0]} 不存在"
                
            return json.dumps(entities, ensure_ascii=False)
        except Exception as e:
            raise Exception(f"查询实体失败: {str(e)}")

    def new_entity(self, project_name: str, name: str, attributes: Optional[dict] = None, save_kg: bool = False) -> str:
        """
        新增实体

        参数:
            project_name (str): 项目ID
            name (str): 实体名称
            attributes (Optional[dict]): 实体属性
            save_kg (bool): 是否保存知识图谱，默认为False

        返回:
            str: 操作结果
        """
        # 先加载知识图谱到缓存
        kg_data = self._load_kg(project_name)

        # 检查是否已存在
        if any(e['name'] == name for e in kg_data['entities']):
            return f"实体 {name} 已存在"

        # 添加实体
        entity = {'name': name, 'attributes': attributes or {}}
        kg_data['entities'].append(entity)

        # 更新缓存
        self.kg_cache[project_name] = kg_data

        if save_kg:
            self.save_kg(project_name)

        return "添加成功"

    def modify_entity(self, project_name: str, name: str, attributes: Optional[dict] = None, save_kg: bool = False) -> str:
        """
        修改实体

        参数:
            project_name (str): 项目ID
            name (str): 实体名称
            attributes (Optional[dict]): 实体新属性
            save_kg (bool): 是否保存知识图谱，默认为False

        返回:
            str: 操作结果
        """
        kg_data = self._load_kg(project_name)

        for entity in kg_data['entities']:
            if entity['name'] == name:
                entity['attributes'] = attributes or {}
                self.kg_cache[project_name] = kg_data
                if save_kg:
                    self.save_kg(project_name)
                return "修改成功"

        return f"实体 {name} 不存在"

    def delete_entity(self, project_name: str, name: str, save_kg: bool = False) -> str:
        """
        删除实体

        参数:
            project_name (str): 项目ID
            name (str): 实体名称
            save_kg (bool): 是否保存知识图谱，默认为False

        返回:
            str: 操作结果
        """
        try:
            kg_data = self._load_kg(project_name)

            # 检查实体是否被锁定
            locked_entities = self.get_locked_entities(project_name)
            if name in locked_entities:
                return f"实体 {name} 已被锁定，无法删除"

            # 删除实体
            kg_data['entities'] = [e for e in kg_data['entities'] if e['name'] != name]

            # 删除相关的关系
            kg_data['relationships'] = [
                r for r in kg_data['relationships']
                if r['source'] != name and r['target'] != name
            ]

            # 保存更改
            self.kg_cache[project_name] = kg_data

            if save_kg:
                self.save_kg(project_name)

            return "删除成功"
        except Exception as e:
            raise Exception(f"删除实体失败: {str(e)}")

    def inquire_relationship(self, project_name: str, entity_a: str, entity_b: str) -> str:
        """
        查询两个实体间的关系

        参数:
            project_name (str): 项目ID
            entity_a (str): 第一个实体名称
            entity_b (str): 第二个实体名称

        返回:
            str: 关系信息
        """
        kg_data = self._load_kg(project_name)

        # 直接关系
        direct = [r for r in kg_data['relationships']
                 if (r['source'] == entity_a and r['target'] == entity_b) or
                    (r['source'] == entity_b and r['target'] == entity_a)]

        if direct:
            return json.dumps(direct, ensure_ascii=False)

        # 构建图并查找间接关系
        graph = self._build_graph(kg_data)
        path = self._find_shortest_path(graph, entity_a, entity_b)

        if path:
            return f"找到间接关系路径：{json.dumps(path, ensure_ascii=False)}"

        return "关系不存在"

    def new_relationship(self, project_name: str, type: str, source: str, target: str,
                        attributes: Optional[dict] = None, save_kg: bool = False) -> str:
        """
        新增关系

        参数:
            project_name (str): 项目ID
            type (str): 关系类型
            source (str): 源实体名称
            target (str): 目标实体名称
            attributes (Optional[dict]): 关系属性
            save_kg (bool): 是否保存知识图谱，默认为False

        返回:
            str: 操作结果
        """
        try:
            if not type or not type.strip():
                return "关系类型不能为空"

            kg_data = self._load_kg(project_name)

            # 检查实体是否存在
            if not any(e['name'] == source for e in kg_data['entities']):
                return f"源实体 {source} 不存在"
            if not any(e['name'] == target for e in kg_data['entities']):
                return f"目标实体 {target} 不存在"

            # 检查关系是否已存在
            if any(r['type'] == type and r['source'] == source and r['target'] == target
                   for r in kg_data['relationships']):
                return "该关系已存在"

            # 添加关系
            relationship = {
                'type': type,
                'source': source,
                'target': target,
                'attributes': attributes or {}
            }
            kg_data['relationships'].append(relationship)
            self.kg_cache[project_name] = kg_data

            if save_kg:
                self.save_kg(project_name)

            return "添加成功"
        except Exception as e:
            return f"新增关系时发生错误: {str(e)}"

    def modify_relationship(self, project_name: str, type: str, source: str, target: str,
                           attributes: Optional[dict] = None, save_kg: bool = False) -> str:
        """
        修改关系

        参数:
            project_name (str): 项目ID
            type (str): 关系类型
            source (str): 源实体名称
            target (str): 目标实体名称
            attributes (Optional[dict]): 关系新属性
            save_kg (bool): 是否保存知识图谱，默认为False

        返回:
            str: 操作结果
        """
        kg_data = self._load_kg(project_name)

        for rel in kg_data['relationships']:
            if (rel['source'] == source and rel['target'] == target):
                # 更新关系类型和属性
                rel['type'] = type
                rel['attributes'] = attributes or {}
                self.kg_cache[project_name] = kg_data
                if save_kg:
                    self.save_kg(project_name)
                return "修改成功"

        return "该关系不存在"

    def delete_relationship(self, project_name: str, type: str, source: str, target: str, save_kg: bool = False) -> str:
        """
        删除关系

        参数:
            project_name (str): 项目ID
            type (str): 关系类型
            source (str): 源实体名称
            target (str): 目标实体名称
            save_kg (bool): 是否保存知识图谱，默认为False

        返回:
            str: 操作结果
        """
        kg_data = self._load_kg(project_name)

        initial_length = len(kg_data['relationships'])
        kg_data['relationships'] = [
            r for r in kg_data['relationships']
            if not (r['type'] == type and
                   r['source'] == source and
                   r['target'] == target)
        ]

        if len(kg_data['relationships']) < initial_length:
            self.kg_cache[project_name] = kg_data
            if save_kg:
                self.save_kg(project_name)
            return "删除成功"

        return "该关系不存在"

    def inquire_entity_relationships(self, project_name: str, name: str) -> str:
        """
        查询实体的所有关系

        参数:
            project_name (str): 项目ID
            name (str): 实体名称

        返回:
            str: 关系信息
        """
        try:
            kg_data = self._load_kg(project_name)

            if not any(e['name'] == name for e in kg_data['entities']):
                return f"实体 {name} 不存在"

            relationships = [
                r for r in kg_data['relationships']
                if r['source'] == name or r['target'] == name
            ]

            return json.dumps(relationships, ensure_ascii=False)
        except Exception as e:
            return f"查询实体关系时发生错误: {str(e)}"

    def inquire_entity_names(self, project_name: str) -> List[str]:
        """
        获取所有实体名称列表

        参数:
            project_name (str): 项目ID

        返回:
            List[str]: 实体名称列表
        """
        kg_data = self._load_kg(project_name)
        return [entity['name'] for entity in kg_data.get('entities', [])]

    def inquire_entity_list(self, project_name: str) -> str:
        """
        获取所有实体列表（包含完整信息）

        参数:
            project_name (str): 项目ID

        返回:
            str: 实体列表（包含完整信息）
        """
        try:
            kg_data = self._load_kg(project_name)
            entities = kg_data.get('entities', [])
            return json.dumps(entities, ensure_ascii=False)
        except Exception as e:
            raise Exception(f"获取实体列表失败: {str(e)}")

    def _build_graph(self, kg_data: dict) -> dict:
        """
        构建图结构

        参数:
            kg_data (dict): 知识图谱数据

        返回:
            dict: 图结构
        """
        graph = {}
        for rel in kg_data['relationships']:
            source, target = rel['source'], rel['target']
            if source not in graph:
                graph[source] = []
            if target not in graph:
                graph[target] = []
            graph[source].append((target, rel))
            graph[target].append((source, rel))
        return graph

    def _find_shortest_path(self, graph: dict, start: str, end: str) -> List[dict]:
        """
        查找最短路径

        参数:
            graph (dict): 图结构
            start (str): 起始实体名称
            end (str): 目标实体名称

        返回:
            List[dict]: 最短路径
        """
        if start not in graph or end not in graph:
            return []

        visited = {start}
        queue = deque([(start, [])])

        while queue:
            current, path = queue.popleft()
            if current == end:
                return path

            for neighbor, rel in graph[current]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [rel]))

    def get_locked_entities(self, project_name: str) -> List[str]:
        """
        获取项目中被锁定的实体列表

        参数:
            project_name (str): 项目名称

        返回:
            List[str]: 被锁定的实体名称列表
        """
        kg_data = self._load_kg(project_name)
        return kg_data.get('locked_entities', [])

    def toggle_entity_lock(self, project_name: str, entity_name: str, save_kg: bool = False) -> bool:
        """
        切换实体的锁定状态

        参数:
            project_name (str): 项目名称
            entity_name (str): 实体名称
            save_kg (bool): 是否保存知识图谱，默认为False

        返回:
            bool: True表示现在是锁定状态，False表示现在是解锁状态
        """
        try:
            # 验证实体是否存在
            entities = self.inquire_entity_list(project_name)
            entities = json.loads(entities) if isinstance(entities, str) else entities
            if not any(entity['name'] == entity_name for entity in entities):
                raise Exception(f"实体 {entity_name} 不存在")

            # 加载知识图谱数据
            kg_data = self._load_kg(project_name)
            locked_entities = kg_data.get('locked_entities', [])

            # 切换锁定状态
            is_locked = False
            if entity_name in locked_entities:
                locked_entities.remove(entity_name)
            else:
                locked_entities.append(entity_name)
                is_locked = True

            # 更新知识图谱数据
            kg_data['locked_entities'] = locked_entities
            # 确保数据在缓存中
            self.kg_cache[project_name] = kg_data
            if save_kg:
                self.save_kg(project_name)

            return is_locked

        except Exception as e:
            raise Exception(f"切换实体锁定状态失败: {str(e)}")
