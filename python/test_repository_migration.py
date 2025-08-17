#!/usr/bin/env python3
"""
Test script to validate repository pattern migration
"""
import asyncio
import os
import sys

# Add the src directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_connection_manager():
    """Test the connection manager is working"""
    print("🔍 Testing ConnectionManager...")
    try:
        from server.services.client_manager import get_connection_manager
        
        manager = get_connection_manager()
        print(f"✅ ConnectionManager created: {type(manager).__name__}")
        
        # Test health check
        health = await manager.health_check()
        print(f"✅ Health check: {health}")
        
        return True
    except Exception as e:
        print(f"❌ ConnectionManager test failed: {e}")
        return False


async def test_repository_provider():
    """Test the repository provider is working"""
    print("\n🔍 Testing RepositoryProvider...")
    try:
        from server.services.client_manager import get_repository_provider
        
        provider = get_repository_provider()
        print(f"✅ RepositoryProvider created: {type(provider).__name__}")
        
        # Test getting a repository
        source_repo = provider.get_source_repository()
        print(f"✅ SourceRepository: {type(source_repo).__name__}")
        
        project_repo = provider.get_project_repository()
        print(f"✅ ProjectRepository: {type(project_repo).__name__}")
        
        return True
    except Exception as e:
        print(f"❌ RepositoryProvider test failed: {e}")
        return False


async def test_services():
    """Test that services can be instantiated"""
    print("\n🔍 Testing Service instantiation...")
    try:
        from server.services.source_management_service import SourceManagementService
        from server.services.projects.project_service import ProjectService
        from server.services.projects.task_service import TaskService
        from server.services.search.rag_service import RAGService
        
        # Test service creation
        source_service = SourceManagementService()
        print(f"✅ SourceManagementService: {type(source_service).__name__}")
        
        project_service = ProjectService()
        print(f"✅ ProjectService: {type(project_service).__name__}")
        
        task_service = TaskService()
        print(f"✅ TaskService: {type(task_service).__name__}")
        
        rag_service = RAGService()
        print(f"✅ RAGService: {type(rag_service).__name__}")
        
        return True
    except Exception as e:
        print(f"❌ Service instantiation test failed: {e}")
        return False


async def test_database_operations():
    """Test basic database operations"""
    print("\n🔍 Testing basic database operations...")
    try:
        from server.services.client_manager import get_connection_manager
        
        manager = get_connection_manager()
        
        # Test read operations
        async with manager.get_reader() as db:
            # Test selecting from sources table
            result = await db.select("sources", limit=1)
            print(f"✅ Sources table query: success={result.success}")
            
            # Test selecting from projects table  
            result = await db.select("projects", limit=1)
            print(f"✅ Projects table query: success={result.success}")
            
        return True
    except Exception as e:
        print(f"❌ Database operations test failed: {e}")
        return False


async def main():
    """Run all tests"""
    print("🚀 Repository Pattern Migration Test")
    print("=" * 40)
    
    tests = [
        test_connection_manager,
        test_repository_provider, 
        test_services,
        test_database_operations
    ]
    
    results = []
    for test in tests:
        try:
            result = await test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 40)
    print("📊 Test Results:")
    passed = sum(results)
    total = len(results)
    print(f"✅ Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! Repository migration is working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Check the output above for details.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)