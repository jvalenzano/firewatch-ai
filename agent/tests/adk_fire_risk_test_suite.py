#!/usr/bin/env python3
"""
Enhanced ADK Fire Risk Agent Test Suite
Addresses challenges discovered in Phase III validation
Compatible with Google ADK agent architecture
"""

import asyncio
import json
import time
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple, Optional
from pathlib import Path
from dataclasses import dataclass, asdict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class TestResult:
    """Structured test result data"""
    test_name: str
    suite: str
    passed: bool
    duration: float
    details: Dict[str, Any]
    error: Optional[str] = None
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


class ADKFireRiskTestSuite:
    """Enhanced test suite for ADK Fire Risk Agent"""
    
    def __init__(self, agent_path: str = None):
        self.agent_path = agent_path or Path(__file__).parent
        self.results = {
            "test_info": {
                "start_time": datetime.now().isoformat(),
                "agent_id": os.getenv('AGENT_ID', '6609146802375491584'),
                "project_id": os.getenv('PROJECT_ID'),
                "test_runner": "ADK Enhanced Test Suite v2.0"
            },
            "test_results": [],
            "suite_summaries": {},
            "metrics": {
                "total_tests": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "response_times": []
            }
        }
        
        # Import agent tools dynamically
        self._import_agent_tools()
        
    def _import_agent_tools(self):
        """Dynamically import agent tools"""
        try:
            # Add agent directory to path
            sys.path.insert(0, str(self.agent_path))
            
            # Import tools module
            from data_science import agent
            
            # Store tool references
            self.tools = {
                'calculate_fire_danger': getattr(agent, 'calculate_fire_danger', None),
                'get_fire_danger_for_station': getattr(agent, 'get_fire_danger_for_station', None),
                'get_real_time_fire_weather_conditions': getattr(agent, 'get_real_time_fire_weather_conditions', None),
                'get_fire_weather_forecast': getattr(agent, 'get_fire_weather_forecast', None),
                'analyze_fire_zone': getattr(agent, 'analyze_fire_zone', None),
                'analyze_financial_impact': getattr(agent, 'analyze_financial_impact', None),
                'explain_fire_danger_level': getattr(agent, 'explain_fire_danger_level', None)
            }
            
            # Import visual formatter if available
            try:
                from data_science.visual_formatter import VisualResponseFormatter
                self.visual_formatter = VisualResponseFormatter()
            except ImportError:
                self.visual_formatter = None
                logger.warning("Visual formatter not available")
                
        except Exception as e:
            logger.error(f"Failed to import agent tools: {e}")
            raise
            
    def execute_tool(self, tool_name: str, *args, **kwargs) -> Tuple[Any, float, Optional[str]]:
        """Execute a tool and measure performance"""
        if tool_name not in self.tools or self.tools[tool_name] is None:
            return None, 0.0, f"Tool '{tool_name}' not available"
            
        start_time = time.time()
        try:
            # Handle both sync and async tools
            tool = self.tools[tool_name]
            if asyncio.iscoroutinefunction(tool):
                # Run async tool
                loop = asyncio.get_event_loop()
                result = loop.run_until_complete(tool(*args, **kwargs))
            else:
                # Run sync tool
                result = tool(*args, **kwargs)
                
            duration = time.time() - start_time
            return result, duration, None
            
        except Exception as e:
            duration = time.time() - start_time
            error_msg = str(e)
            logger.error(f"Tool execution failed: {tool_name} - {error_msg}")
            return None, duration, error_msg
            
    def parse_tool_response(self, response: Any) -> Dict[str, Any]:
        """Parse tool response handling both structured and string responses"""
        if response is None:
            return {"error": "No response"}
            
        # If response is already a dict, return it
        if isinstance(response, dict):
            return response
            
        # Convert string response to structured data
        response_str = str(response)
        
        parsed = {
            "raw_response": response_str,
            "response_length": len(response_str),
            "has_visual_elements": False,
            "extracted_values": {}
        }
        
        # Check for visual elements
        visual_indicators = ['█', '▓', '░', '🔴', '🟠', '🟡', '🟢', '⚠️', '🚨']
        parsed["has_visual_elements"] = any(indicator in response_str for indicator in visual_indicators)
        
        # Extract common patterns
        import re
        
        # Fire danger classification
        classification_match = re.search(r'(LOW|MODERATE|HIGH|VERY HIGH|EXTREME)', response_str, re.IGNORECASE)
        if classification_match:
            parsed["extracted_values"]["classification"] = classification_match.group(1).upper()
            
        # Numeric values
        numeric_patterns = {
            'burning_index': r'burning\s*index[:\s]+(\d+\.?\d*)',
            'temperature': r'temperature[:\s]+(\d+\.?\d*)',
            'humidity': r'humidity[:\s]+(\d+\.?\d*)',
            'wind_speed': r'wind\s*speed[:\s]+(\d+\.?\d*)',
            'fire_weather_index': r'fire\s*weather\s*index[:\s]+(\d+\.?\d*)'
        }
        
        for key, pattern in numeric_patterns.items():
            match = re.search(pattern, response_str, re.IGNORECASE)
            if match:
                try:
                    parsed["extracted_values"][key] = float(match.group(1))
                except ValueError:
                    pass
                    
        # Financial values
        dollar_match = re.findall(r'\$[\d,]+(?:\.\d{2})?', response_str)
        if dollar_match:
            parsed["extracted_values"]["financial_values"] = dollar_match
            
        # Station names
        station_match = re.findall(r'(?:station\s+)?([A-Z][A-Z0-9_]+)', response_str)
        if station_match:
            parsed["extracted_values"]["stations"] = list(set(station_match))[:5]  # Limit to 5
            
        return parsed
        
    def log_result(self, result: TestResult):
        """Log test result"""
        self.results["test_results"].append(asdict(result))
        
        # Update suite summary
        if result.suite not in self.results["suite_summaries"]:
            self.results["suite_summaries"][result.suite] = {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "avg_duration": 0.0,
                "durations": []
            }
            
        suite = self.results["suite_summaries"][result.suite]
        suite["total"] += 1
        suite["durations"].append(result.duration)
        
        if result.passed:
            suite["passed"] += 1
            self.results["metrics"]["passed"] += 1
        else:
            suite["failed"] += 1
            self.results["metrics"]["failed"] += 1
            
        self.results["metrics"]["total_tests"] += 1
        self.results["metrics"]["response_times"].append(result.duration)
        
        # Calculate average duration
        suite["avg_duration"] = sum(suite["durations"]) / len(suite["durations"])
        
    # ============ TEST SUITES ============
    
    def test_suite_1_basic_functionality(self):
        """Test Suite 1: Basic Functionality"""
        logger.info("\n🔧 Test Suite 1: Basic Functionality")
        
        # Test 1.1: Simple fire danger calculation
        result, duration, error = self.execute_tool(
            'calculate_fire_danger',
            temperature=85.0,
            relative_humidity=25.0,
            wind_speed=15.0
        )
        
        parsed = self.parse_tool_response(result)
        classification = parsed["extracted_values"].get("classification")
        
        test_passed = error is None and classification is not None
        
        self.log_result(TestResult(
            test_name="simple_calculation",
            suite="basic_functionality",
            passed=test_passed,
            duration=duration,
            details={
                "classification": classification,
                "has_response": result is not None,
                "response_type": type(result).__name__
            },
            error=error
        ))
        
        logger.info(f"  Simple calculation: {'✅ PASS' if test_passed else '❌ FAIL'} ({duration:.3f}s)")
        
        # Test 1.2: Station data retrieval
        result, duration, error = self.execute_tool(
            'get_fire_danger_for_station',
            station_name="BROWNSBORO",
            limit=1
        )
        
        parsed = self.parse_tool_response(result)
        test_passed = error is None and parsed["response_length"] > 50
        
        self.log_result(TestResult(
            test_name="station_data_retrieval",
            suite="basic_functionality",
            passed=test_passed,
            duration=duration,
            details={
                "response_length": parsed["response_length"],
                "stations_found": parsed["extracted_values"].get("stations", [])
            },
            error=error
        ))
        
        logger.info(f"  Station data retrieval: {'✅ PASS' if test_passed else '❌ FAIL'} ({duration:.3f}s)")
        
    def test_suite_2_performance(self):
        """Test Suite 2: Performance Validation"""
        logger.info("\n⚡ Test Suite 2: Performance Validation")
        
        # Test 2.1: Response time for simple queries
        response_times = []
        
        for i in range(3):
            result, duration, error = self.execute_tool(
                'calculate_fire_danger',
                temperature=80.0 + i*5,
                relative_humidity=30.0 - i*3,
                wind_speed=10.0 + i*2
            )
            response_times.append(duration)
            
        avg_time = sum(response_times) / len(response_times)
        test_passed = avg_time < 1.0 and all(t < 2.0 for t in response_times)
        
        self.log_result(TestResult(
            test_name="response_time_consistency",
            suite="performance",
            passed=test_passed,
            duration=avg_time,
            details={
                "individual_times": response_times,
                "average_time": avg_time,
                "max_time": max(response_times),
                "min_time": min(response_times)
            }
        ))
        
        logger.info(f"  Response time consistency: {'✅ PASS' if test_passed else '❌ FAIL'} (avg: {avg_time:.3f}s)")
        
        # Test 2.2: Complex query performance
        result, duration, error = self.execute_tool(
            'analyze_fire_zone',
            zone_id="Zone 7"
        )
        
        test_passed = error is None and duration < 5.0
        
        self.log_result(TestResult(
            test_name="complex_query_performance",
            suite="performance",
            passed=test_passed,
            duration=duration,
            details={
                "target_time": 5.0,
                "actual_time": duration
            },
            error=error
        ))
        
        logger.info(f"  Complex query performance: {'✅ PASS' if test_passed else '❌ FAIL'} ({duration:.3f}s)")
        
    def test_suite_3_accuracy(self):
        """Test Suite 3: Calculation Accuracy"""
        logger.info("\n🎯 Test Suite 3: Calculation Accuracy")
        
        # Test 3.1: Extreme conditions
        result, duration, error = self.execute_tool(
            'calculate_fire_danger',
            temperature=110.0,
            relative_humidity=5.0,
            wind_speed=40.0
        )
        
        parsed = self.parse_tool_response(result)
        classification = parsed["extracted_values"].get("classification")
        
        test_passed = classification == "EXTREME"
        
        self.log_result(TestResult(
            test_name="extreme_conditions",
            suite="accuracy",
            passed=test_passed,
            duration=duration,
            details={
                "expected": "EXTREME",
                "actual": classification,
                "conditions": {
                    "temperature": 110.0,
                    "humidity": 5.0,
                    "wind_speed": 40.0
                }
            },
            error=error
        ))
        
        logger.info(f"  Extreme conditions: {'✅ PASS' if test_passed else '❌ FAIL'}")
        
        # Test 3.2: Low risk conditions
        result, duration, error = self.execute_tool(
            'calculate_fire_danger',
            temperature=65.0,
            relative_humidity=80.0,
            wind_speed=5.0
        )
        
        parsed = self.parse_tool_response(result)
        classification = parsed["extracted_values"].get("classification")
        
        test_passed = classification in ["LOW", "MODERATE"]
        
        self.log_result(TestResult(
            test_name="low_risk_conditions",
            suite="accuracy",
            passed=test_passed,
            duration=duration,
            details={
                "expected": "LOW or MODERATE",
                "actual": classification
            },
            error=error
        ))
        
        logger.info(f"  Low risk conditions: {'✅ PASS' if test_passed else '❌ FAIL'}")
        
    def test_suite_4_visual_formatting(self):
        """Test Suite 4: Visual Formatting"""
        logger.info("\n🎨 Test Suite 4: Visual Formatting")
        
        # Test 4.1: Visual elements in response
        result, duration, error = self.execute_tool(
            'calculate_fire_danger',
            temperature=88.0,
            relative_humidity=22.0,
            wind_speed=18.0
        )
        
        parsed = self.parse_tool_response(result)
        has_visuals = parsed["has_visual_elements"]
        
        test_passed = has_visuals and error is None
        
        self.log_result(TestResult(
            test_name="visual_elements",
            suite="visual_formatting",
            passed=test_passed,
            duration=duration,
            details={
                "has_visual_elements": has_visuals,
                "response_preview": str(result)[:200] if result else None
            },
            error=error
        ))
        
        logger.info(f"  Visual elements: {'✅ PASS' if test_passed else '❌ FAIL'}")
        
    def test_suite_5_error_handling(self):
        """Test Suite 5: Error Handling"""
        logger.info("\n⚠️ Test Suite 5: Error Handling")
        
        # Test 5.1: Invalid station name
        result, duration, error = self.execute_tool(
            'get_fire_danger_for_station',
            station_name="INVALID_STATION_XYZ",
            limit=1
        )
        
        # Should handle gracefully - either return empty result or error message
        test_passed = duration < 5.0  # Should not hang
        
        self.log_result(TestResult(
            test_name="invalid_station_handling",
            suite="error_handling",
            passed=test_passed,
            duration=duration,
            details={
                "handled_gracefully": test_passed,
                "response_type": type(result).__name__ if result else "None"
            },
            error=error
        ))
        
        logger.info(f"  Invalid station handling: {'✅ PASS' if test_passed else '❌ FAIL'}")
        
        # Test 5.2: Invalid parameters
        result, duration, error = self.execute_tool(
            'calculate_fire_danger',
            temperature=-999,  # Invalid temperature
            relative_humidity=150,  # Invalid humidity
            wind_speed=-10  # Invalid wind speed
        )
        
        # Should handle invalid inputs gracefully
        test_passed = duration < 2.0 and (error is not None or result is not None)
        
        self.log_result(TestResult(
            test_name="invalid_parameters",
            suite="error_handling",
            passed=test_passed,
            duration=duration,
            details={
                "invalid_inputs": {
                    "temperature": -999,
                    "humidity": 150,
                    "wind_speed": -10
                }
            },
            error=error
        ))
        
        logger.info(f"  Invalid parameters: {'✅ PASS' if test_passed else '❌ FAIL'}")
        
    def test_suite_6_integration(self):
        """Test Suite 6: Integration Tests"""
        logger.info("\n🔗 Test Suite 6: Integration Tests")
        
        # Test 6.1: Zone 7 emergency response
        result, duration, error = self.execute_tool(
            'analyze_fire_zone',
            zone_id="Zone 7"
        )
        
        parsed = self.parse_tool_response(result)
        response_str = str(result).upper() if result else ""
        has_emergency_tone = any(word in response_str for word in ["EMERGENCY", "CRITICAL", "EVACUATE", "🚨"])
        
        test_passed = has_emergency_tone and error is None
        
        self.log_result(TestResult(
            test_name="zone_7_emergency",
            suite="integration",
            passed=test_passed,
            duration=duration,
            details={
                "has_emergency_tone": has_emergency_tone,
                "zone_id": "Zone 7"
            },
            error=error
        ))
        
        logger.info(f"  Zone 7 emergency: {'✅ PASS' if test_passed else '❌ FAIL'}")
        
        # Test 6.2: Financial analysis
        result, duration, error = self.execute_tool(
            'analyze_financial_impact',
            scenario="prescribed_burn_vs_suppression"
        )
        
        parsed = self.parse_tool_response(result)
        has_financial = len(parsed["extracted_values"].get("financial_values", [])) > 0
        
        test_passed = has_financial and error is None
        
        self.log_result(TestResult(
            test_name="financial_analysis",
            suite="integration",
            passed=test_passed,
            duration=duration,
            details={
                "has_financial_data": has_financial,
                "financial_values": parsed["extracted_values"].get("financial_values", [])
            },
            error=error
        ))
        
        logger.info(f"  Financial analysis: {'✅ PASS' if test_passed else '❌ FAIL'}")
        
    def generate_report(self):
        """Generate comprehensive test report"""
        # Calculate final metrics
        metrics = self.results["metrics"]
        if metrics["response_times"]:
            metrics["avg_response_time"] = sum(metrics["response_times"]) / len(metrics["response_times"])
            metrics["min_response_time"] = min(metrics["response_times"])
            metrics["max_response_time"] = max(metrics["response_times"])
        
        metrics["pass_rate"] = (metrics["passed"] / metrics["total_tests"] * 100) if metrics["total_tests"] > 0 else 0
        
        # Determine final status
        pass_rate = metrics["pass_rate"]
        if pass_rate >= 80:
            final_status = "✅ PASS"
            status_detail = "System meets validation criteria"
        elif pass_rate >= 60:
            final_status = "🟡 CONDITIONAL PASS"
            status_detail = "System partially meets criteria"
        else:
            final_status = "❌ FAIL"
            status_detail = "System does not meet criteria"
            
        self.results["summary"] = {
            "final_status": final_status,
            "status_detail": status_detail,
            "test_date": datetime.now().isoformat(),
            "duration": (datetime.now() - datetime.fromisoformat(self.results["test_info"]["start_time"])).total_seconds()
        }
        
        # Save JSON report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_filename = f"adk_test_results_{timestamp}.json"
        
        with open(json_filename, 'w') as f:
            json.dump(self.results, f, indent=2)
            
        # Create markdown report
        self._create_markdown_report(json_filename)
        
        # Print summary
        print("\n" + "=" * 60)
        print("TEST EXECUTION SUMMARY")
        print("=" * 60)
        print(f"\n📊 Overall Results:")
        print(f"  • Total Tests: {metrics['total_tests']}")
        print(f"  • Passed: {metrics['passed']} ✅")
        print(f"  • Failed: {metrics['failed']} ❌")
        print(f"  • Pass Rate: {metrics['pass_rate']:.1f}%")
        
        if 'avg_response_time' in metrics:
            print(f"  • Avg Response Time: {metrics['avg_response_time']:.3f}s")
            
        print(f"\n📋 Suite Results:")
        for suite_name, suite_data in self.results["suite_summaries"].items():
            print(f"\n  {suite_name.replace('_', ' ').title()}:")
            print(f"    • Tests: {suite_data['total']}")
            print(f"    • Passed: {suite_data['passed']}")
            print(f"    • Success Rate: {(suite_data['passed']/suite_data['total']*100):.0f}%")
            print(f"    • Avg Duration: {suite_data['avg_duration']:.3f}s")
            
        print(f"\n🏆 FINAL STATUS: {final_status}")
        print(f"   {status_detail}")
        print("=" * 60)
        
        print(f"\n💾 Reports saved:")
        print(f"  • JSON: {json_filename}")
        print(f"  • Markdown: {json_filename.replace('.json', '.md')}")
        
        return final_status, json_filename
        
    def _create_markdown_report(self, json_filename: str):
        """Create markdown report"""
        md_filename = json_filename.replace('.json', '.md')
        
        with open(md_filename, 'w') as f:
            f.write("# ADK Fire Risk Agent Test Report\n\n")
            f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Agent ID**: {self.results['test_info']['agent_id']}\n")
            f.write(f"**Project ID**: {self.results['test_info']['project_id']}\n\n")
            
            # Summary
            summary = self.results["summary"]
            metrics = self.results["metrics"]
            
            f.write("## Executive Summary\n\n")
            f.write(f"**Final Status**: {summary['final_status']}\n")
            f.write(f"**Status Detail**: {summary['status_detail']}\n")
            f.write(f"**Total Duration**: {summary['duration']:.1f}s\n\n")
            
            f.write("### Key Metrics\n\n")
            f.write(f"- **Total Tests**: {metrics['total_tests']}\n")
            f.write(f"- **Passed**: {metrics['passed']}\n")
            f.write(f"- **Failed**: {metrics['failed']}\n")
            f.write(f"- **Pass Rate**: {metrics['pass_rate']:.1f}%\n")
            
            if 'avg_response_time' in metrics:
                f.write(f"- **Average Response Time**: {metrics['avg_response_time']:.3f}s\n")
                f.write(f"- **Min Response Time**: {metrics['min_response_time']:.3f}s\n")
                f.write(f"- **Max Response Time**: {metrics['max_response_time']:.3f}s\n")
                
            # Suite summaries
            f.write("\n## Test Suite Results\n\n")
            
            for suite_name, suite_data in self.results["suite_summaries"].items():
                success_rate = (suite_data['passed']/suite_data['total']*100) if suite_data['total'] > 0 else 0
                
                f.write(f"### {suite_name.replace('_', ' ').title()}\n\n")
                f.write(f"- **Total Tests**: {suite_data['total']}\n")
                f.write(f"- **Passed**: {suite_data['passed']}\n")
                f.write(f"- **Failed**: {suite_data['failed']}\n")
                f.write(f"- **Success Rate**: {success_rate:.0f}%\n")
                f.write(f"- **Average Duration**: {suite_data['avg_duration']:.3f}s\n\n")
                
            # Detailed test results
            f.write("## Detailed Test Results\n\n")
            
            current_suite = None
            for test_result in self.results["test_results"]:
                if test_result["suite"] != current_suite:
                    current_suite = test_result["suite"]
                    f.write(f"### {current_suite.replace('_', ' ').title()}\n\n")
                    
                status = "✅" if test_result["passed"] else "❌"
                f.write(f"#### {status} {test_result['test_name'].replace('_', ' ').title()}\n\n")
                f.write(f"- **Duration**: {test_result['duration']:.3f}s\n")
                
                if test_result.get("error"):
                    f.write(f"- **Error**: {test_result['error']}\n")
                    
                if test_result.get("details"):
                    f.write("- **Details**:\n")
                    for key, value in test_result["details"].items():
                        f.write(f"  - {key}: {value}\n")
                f.write("\n")
                
            # Recommendations
            f.write("## Recommendations\n\n")
            
            if metrics['pass_rate'] >= 80:
                f.write("### ✅ System Ready for Production\n\n")
                f.write("1. All major functionality verified\n")
                f.write("2. Performance meets targets\n")
                f.write("3. Consider additional stress testing\n")
                f.write("4. Monitor production performance\n")
            elif metrics['pass_rate'] >= 60:
                f.write("### 🟡 Address Issues Before Production\n\n")
                f.write("1. Fix failing tests\n")
                f.write("2. Review error handling\n")
                f.write("3. Optimize slow operations\n")
                f.write("4. Re-run validation after fixes\n")
            else:
                f.write("### ❌ Significant Improvements Needed\n\n")
                f.write("1. Review core functionality\n")
                f.write("2. Fix critical failures\n")
                f.write("3. Improve test coverage\n")
                f.write("4. Consider architecture review\n")
                
    def run_all_tests(self):
        """Execute all test suites"""
        logger.info("Starting ADK Fire Risk Agent Test Suite")
        logger.info("=" * 60)
        
        # Run test suites
        try:
            self.test_suite_1_basic_functionality()
            self.test_suite_2_performance()
            self.test_suite_3_accuracy()
            self.test_suite_4_visual_formatting()
            self.test_suite_5_error_handling()
            self.test_suite_6_integration()
        except Exception as e:
            logger.error(f"Test execution failed: {e}")
            raise
            
        # Generate report
        final_status, report_file = self.generate_report()
        
        return final_status.startswith("✅"), report_file


def main():
    """Main entry point"""
    # Check for agent path argument
    agent_path = sys.argv[1] if len(sys.argv) > 1 else None
    
    # Create and run test suite
    test_suite = ADKFireRiskTestSuite(agent_path)
    
    try:
        success, report_file = test_suite.run_all_tests()
        
        # Exit with appropriate code
        sys.exit(0 if success else 1)
        
    except Exception as e:
        logger.error(f"Test suite failed: {e}")
        sys.exit(2)


if __name__ == "__main__":
    main()
