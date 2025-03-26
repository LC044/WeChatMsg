import os
import sqlite3
import threading
import queue
import time
from typing import Dict, Optional, List, Tuple

class DatabaseConnectionPool:
    """
    SQLite数据库连接池，用于管理多个数据库连接，减少连接创建和销毁的开销
    """
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(DatabaseConnectionPool, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance
    
    def __init__(self, max_connections=5, timeout=5):
        # 保证只初始化一次
        if self._initialized:
            return
            
        self._initialized = True
        self.max_connections = max_connections
        self.timeout = timeout
        self.pools: Dict[str, queue.Queue] = {}
        self.in_use: Dict[str, Dict[sqlite3.Connection, threading.Thread]] = {}
        self.connection_locks: Dict[str, threading.Lock] = {}
    
    def _create_connection(self, db_path: str) -> sqlite3.Connection:
        """创建一个新的数据库连接"""
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"数据库文件不存在: {db_path}")
        
        conn = sqlite3.connect(db_path, check_same_thread=False)
        # 开启外键约束
        conn.execute('PRAGMA foreign_keys = ON')
        # 启用写入确认，提高安全性
        conn.execute('PRAGMA synchronous = NORMAL')
        # 提高写入性能
        conn.execute('PRAGMA journal_mode = WAL')
        # 设置页缓存
        conn.execute('PRAGMA cache_size = 10000')
        return conn
    
    def _get_pool(self, db_path: str) -> queue.Queue:
        """获取或创建指定数据库的连接池"""
        if db_path not in self.pools:
            with self._lock:
                if db_path not in self.pools:
                    self.pools[db_path] = queue.Queue(maxsize=self.max_connections)
                    self.in_use[db_path] = {}
                    self.connection_locks[db_path] = threading.Lock()
                    
                    # 预创建连接
                    for _ in range(min(2, self.max_connections)):
                        try:
                            conn = self._create_connection(db_path)
                            self.pools[db_path].put(conn)
                        except Exception as e:
                            print(f"预创建连接失败: {e}")
        
        return self.pools[db_path]
    
    def get_connection(self, db_path: str) -> sqlite3.Connection:
        """
        从连接池获取一个数据库连接
        
        Args:
            db_path: 数据库文件路径
            
        Returns:
            sqlite3.Connection: 数据库连接对象
            
        Raises:
            TimeoutError: 超时未获取到连接
        """
        pool = self._get_pool(db_path)
        
        # 尝试从池中获取连接
        try:
            conn = pool.get(block=True, timeout=self.timeout)
        except queue.Empty:
            # 如果池已满但仍在使用的连接数小于最大连接数，则创建新连接
            with self.connection_locks[db_path]:
                if len(self.in_use[db_path]) < self.max_connections:
                    conn = self._create_connection(db_path)
                else:
                    raise TimeoutError(f"无法获取数据库连接，连接池已满: {db_path}")
        
        # 记录连接使用情况
        with self.connection_locks[db_path]:
            self.in_use[db_path][conn] = threading.current_thread()
        
        return conn
    
    def release_connection(self, db_path: str, conn: sqlite3.Connection):
        """
        释放数据库连接回连接池
        
        Args:
            db_path: 数据库文件路径
            conn: 要释放的连接
        """
        if db_path not in self.pools:
            conn.close()
            return
            
        with self.connection_locks[db_path]:
            if conn in self.in_use[db_path]:
                del self.in_use[db_path][conn]
                try:
                    # 将连接放回池中
                    self.pools[db_path].put(conn, block=False)
                except queue.Full:
                    # 如果池已满，关闭多余的连接
                    conn.close()
    
    def execute_batch(self, db_path: str, sql: str, params_list: List[tuple], commit=True) -> List[Optional[Tuple]]:
        """
        执行批量SQL操作，适用于多次执行相同SQL语句的情况
        
        Args:
            db_path: 数据库文件路径
            sql: SQL语句
            params_list: 参数列表，每个元素是一个参数元组
            commit: 是否自动提交事务
            
        Returns:
            list: 执行结果列表
        """
        conn = None
        results = []
        
        try:
            conn = self.get_connection(db_path)
            cursor = conn.cursor()
            
            # 启动事务
            if commit:
                conn.execute("BEGIN TRANSACTION")
                
            # 批量执行
            for params in params_list:
                cursor.execute(sql, params)
                if cursor.description:  # 如果有返回数据
                    results.append(cursor.fetchall())
                else:
                    results.append(None)
            
            # 提交事务
            if commit:
                conn.commit()
                
            return results
        except Exception as e:
            if conn and commit:
                conn.rollback()
            raise e
        finally:
            if conn:
                self.release_connection(db_path, conn)
    
    def execute_query(self, db_path: str, sql: str, params=None) -> List[Tuple]:
        """
        执行查询SQL语句
        
        Args:
            db_path: 数据库文件路径
            sql: SQL查询语句
            params: 查询参数
            
        Returns:
            list: 查询结果列表
        """
        conn = None
        try:
            conn = self.get_connection(db_path)
            cursor = conn.cursor()
            
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
                
            return cursor.fetchall()
        finally:
            if conn:
                self.release_connection(db_path, conn)
    
    def execute_update(self, db_path: str, sql: str, params=None) -> int:
        """
        执行更新SQL语句
        
        Args:
            db_path: 数据库文件路径
            sql: SQL更新语句
            params: 更新参数
            
        Returns:
            int: 受影响的行数
        """
        conn = None
        try:
            conn = self.get_connection(db_path)
            cursor = conn.cursor()
            
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
                
            conn.commit()
            return cursor.rowcount
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                self.release_connection(db_path, conn)
    
    def close_all(self):
        """关闭所有连接池中的连接"""
        with self._lock:
            for db_path, pool in self.pools.items():
                # 关闭所有未使用的连接
                while not pool.empty():
                    try:
                        conn = pool.get(block=False)
                        conn.close()
                    except queue.Empty:
                        break
                
                # 关闭所有正在使用的连接
                with self.connection_locks[db_path]:
                    for conn in list(self.in_use[db_path].keys()):
                        try:
                            conn.close()
                        except:
                            pass
                    self.in_use[db_path].clear()
            
            # 清空池
            self.pools.clear()

# 全局连接池实例
db_pool = DatabaseConnectionPool()

def close_db_pool():
    """关闭数据库连接池中的所有连接"""
    db_pool.close_all() 