from abc import ABC
from config.config import load_config
import logging

# 配置日志输出
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SingletonService(ABC):
    """
    单例服务基类，所有需要单例模式的服务都应该继承这个类
    """
    _instances = {}
    _config = None
    
    @classmethod
    def get_config(cls):
        """获取全局配置"""
        if cls._config is None:
            cls._config = load_config()
            logger.info("Configuration loaded successfully")
        return cls._config
    
    def __new__(cls, *args, **kwargs):
        if cls not in cls._instances:
            logger.info(f"Creating new instance of {cls.__name__}")
            cls._instances[cls] = super(SingletonService, cls).__new__(cls)
            # 添加初始化标志
            cls._instances[cls]._initialized = False
        else:
            logger.info(f"Returning existing instance of {cls.__name__}")
        return cls._instances[cls]
        
    def __init__(self, *args, **kwargs):
        # 确保初始化代码只运行一次
        if not self._initialized:
            # 在初始化时加载配置
            logger.info(f"{self.__class__.__name__}: Starting initialization")
            self.config = self.get_config()
            self._initialize(*args, **kwargs)
            self._initialized = True
            logger.info(f"{self.__class__.__name__}: Initialization completed")
        else:
            logger.info(f"{self.__class__.__name__}: Already initialized, skipping")
            
    def _initialize(self, *args, **kwargs):
        """
        初始化方法，子类应该重写这个方法来实现自己的初始化逻辑
        """
        pass
