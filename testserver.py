import requests
import time
import threading
import random
import uuid
import json
import traceback

# 配置信息 - 替换为您的实际值
SERVER_URL = "https://scrawl.weber.edu.deal/api"  # 您的 Vercel 部署 URL
ADMIN_KEY = ""  # 清理端点的管理密钥

class CloudVariableClient:
    def __init__(self, server_url, project_id=None, api_key=None):
        self.server_url = server_url
        self.project_id = project_id
        self.api_key = api_key
        self.variables = {}
        
        # 如果没有提供项目ID，自动注册新项目
        if not project_id or not api_key:
            self.register_project()
    
    def register_project(self, project_name="TestProject"):
        """注册新项目"""
        url = f"{self.server_url}/register"
        payload = {"project_name": project_name}
        
        try:
            print(f"📤 注册项目: {project_name}")
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 201:
                data = response.json()
                self.project_id = data['project_id']
                self.api_key = data['api_key']
                print(f"✅ 项目注册成功! ID: {self.project_id}, API Key: {self.api_key}")
                return True
            else:
                print(f"❌ 项目注册失败: {response.status_code}")
                print(f"响应内容: {response.text}")
                print(f"请求URL: {url}")
                print(f"请求负载: {payload}")
                return False
        except Exception as e:
            print(f"❌ 注册请求异常: {str(e)}")
            traceback.print_exc()
            return False
    
    def set_variable(self, var_name, var_value):
        """设置变量值"""
        if not self.project_id or not self.api_key:
            print("❌ 未设置项目ID或API密钥")
            return False
        
        url = f"{self.server_url}/{self.project_id}/set"
        headers = {"X-API-Key": self.api_key}
        payload = {"var_name": var_name, "var_value": var_value}
        
        try:
            print(f"📤 设置变量: {var_name} = {var_value}")
            response = requests.post(url, json=payload, headers=headers, timeout=5)
            
            if response.status_code == 200:
                print(f"✅ 设置变量成功: {var_name} = {var_value}")
                self.variables[var_name] = var_value
                return True
            else:
                print(f"❌ 设置变量失败: {response.status_code}")
                print(f"响应内容: {response.text}")
                print(f"请求URL: {url}")
                print(f"请求头: {headers}")
                print(f"请求负载: {payload}")
                return False
        except Exception as e:
            print(f"❌ 设置变量异常: {str(e)}")
            traceback.print_exc()
            return False
    
    def get_variable(self, var_name):
        """获取变量值"""
        if not self.project_id or not self.api_key:
            print("❌ 未设置项目ID或API密钥")
            return None
        
        url = f"{self.server_url}/{self.project_id}/get"
        headers = {"X-API-Key": self.api_key}
        params = {"var_name": var_name}
        
        try:
            print(f"📥 获取变量: {var_name}")
            response = requests.get(url, params=params, headers=headers, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                value = data['var_value']
                print(f"✅ 获取变量成功: {var_name} = {value}")
                self.variables[var_name] = value
                return value
            else:
                print(f"❌ 获取变量失败: {response.status_code}")
                print(f"响应内容: {response.text}")
                print(f"请求URL: {url}")
                print(f"请求头: {headers}")
                print(f"请求参数: {params}")
                return None
        except Exception as e:
            print(f"❌ 获取变量异常: {str(e)}")
            traceback.print_exc()
            return None
    
    def get_all_variables(self):
        """获取所有变量"""
        if not self.project_id or not self.api_key:
            print("❌ 未设置项目ID或API密钥")
            return {}
        
        url = f"{self.server_url}/{self.project_id}/all"
        headers = {"X-API-Key": self.api_key}
        
        try:
            print("📥 获取所有变量")
            response = requests.get(url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                variables = response.json()
                print(f"✅ 获取所有变量成功: 共 {len(variables)} 个变量")
                self.variables = {k: v['value'] for k, v in variables.items()}
                return variables
            else:
                print(f"❌ 获取所有变量失败: {response.status_code}")
                print(f"响应内容: {response.text}")
                return {}
        except Exception as e:
            print(f"❌ 获取所有变量异常: {str(e)}")
            traceback.print_exc()
            return {}
    
    def health_check(self):
        """健康检查"""
        url = f"{self.server_url}/health"
        
        try:
            print("🩺 健康检查")
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 健康检查通过: {data}")
                return True
            else:
                print(f"❌ 健康检查失败: {response.status_code}")
                print(f"响应内容: {response.text}")
                return False
        except Exception as e:
            print(f"❌ 健康检查异常: {str(e)}")
            traceback.print_exc()
            return False

def basic_functionality_test():
    """基本功能测试"""
    print("\n" + "="*50)
    print("执行基本功能测试")
    print("="*50)
    
    # 创建客户端
    print("\n创建新客户端...")
    client = CloudVariableClient(SERVER_URL)
    
    # 健康检查
    print("\n执行健康检查...")
    client.health_check()
    
    # 测试变量操作
    print("\n测试变量操作...")
    client.set_variable("test_counter", "0")
    client.get_variable("test_counter")
    
    # 更新变量
    print("\n更新变量...")
    client.set_variable("test_counter", "42")
    client.get_variable("test_counter")
    
    # 测试另一个变量
    print("\n测试另一个变量...")
    client.set_variable("test_string", "Hello, Cloud!")
    client.get_variable("test_string")
    
    # 获取所有变量
    print("\n获取所有变量...")
    client.get_all_variables()
    
    print("\n✅ 基本功能测试完成")

def simple_concurrency_test():
    """简化的并发测试"""
    print("\n" + "="*50)
    print("执行简化的并发测试")
    print("="*50)
    
    # 创建主项目
    print("\n创建主客户端...")
    main_client = CloudVariableClient(SERVER_URL)
    project_id = main_client.project_id
    api_key = main_client.api_key
    
    # 创建计数器变量
    print("\n初始化计数器...")
    main_client.set_variable("concurrent_counter", "0")
    
    # 创建多个客户端
    clients = []
    for i in range(3):
        print(f"\n创建客户端 {i+1}...")
        client = CloudVariableClient(SERVER_URL, project_id, api_key)
        clients.append(client)
    
    # 每个客户端增加计数器
    for i, client in enumerate(clients):
        print(f"\n客户端 {i+1} 增加计数器...")
        current_value = client.get_variable("concurrent_counter")
        if current_value is None:
            print("❌ 无法获取计数器值，跳过")
            continue
            
        try:
            new_value = str(int(current_value) + 1)
            client.set_variable("concurrent_counter", new_value)
            print(f"✅ 客户端 {i+1} 增加计数器成功: {current_value} → {new_value}")
        except ValueError:
            print(f"❌ 无效的计数器值: {current_value}")
    
    # 检查最终值
    print("\n检查最终值...")
    final_value = main_client.get_variable("concurrent_counter")
    expected_value = "3"  # 3个客户端各增加1
    
    if final_value == expected_value:
        print(f"✅ 并发测试通过! 最终值: {final_value} (预期: {expected_value})")
    else:
        print(f"❌ 并发测试失败! 最终值: {final_value} (预期: {expected_value})")

def persistence_test():
    """持久性测试"""
    print("\n" + "="*50)
    print("执行持久性测试")
    print("="*50)
    
    # 创建客户端并设置变量
    print("\n创建客户端1并设置变量...")
    client1 = CloudVariableClient(SERVER_URL)
    client1.set_variable("persistence_test", "SurviveRestart")
    
    # 保存项目信息
    project_id = client1.project_id
    api_key = client1.api_key
    
    # 创建新客户端（使用相同的项目ID和API密钥）
    print("\n创建客户端2（相同凭证）...")
    client2 = CloudVariableClient(SERVER_URL, project_id, api_key)
    
    # 获取变量
    print("\n客户端2获取变量...")
    value = client2.get_variable("persistence_test")
    
    if value == "SurviveRestart":
        print("✅ 持久性测试通过 - 变量在客户端重启后仍然存在")
    else:
        print(f"❌ 持久性测试失败 - 获取的值: {value}")

def run_safe_tests():
    """运行安全测试（不涉及清理）"""
    print("="*50)
    print("开始云变量服务器测试")
    print("="*50)
    
    # 执行测试
    basic_functionality_test()
    simple_concurrency_test()
    persistence_test()
    
    print("\n" + "="*50)
    print("所有测试完成")
    print("="*50)

if __name__ == "__main__":
    run_safe_tests()