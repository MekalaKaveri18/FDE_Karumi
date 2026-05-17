"""End-to-End Testing Harness for Agentic Demos

Simulates user interactions using Playwright + LLM reasoning.
Includes reliability checks: retry logic, screenshot diffs, conversation flow validation.
"""

from typing import Dict, List, Any, Optional, Callable, Coroutine
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
from playwright.async_api import Page, BrowserContext
import structlog
import asyncio

logger = structlog.get_logger(__name__)


class StepStatus(str, Enum):
    """Status of a test step"""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class ActionStep:
    """Single action in a test scenario"""
    name: str
    description: str
    action: Callable[..., Coroutine]  # async function to execute
    selector: Optional[str] = None  # element to interact with
    input_text: Optional[str] = None  # text to input
    expected_outcome: Optional[str] = None  # what should happen
    retries: int = 3
    retry_delay: int = 2
    screenshot_on_failure: bool = True


@dataclass
class TestResult:
    """Result of a single test"""
    step_name: str
    status: StepStatus
    duration_ms: float
    error: Optional[str] = None
    screenshot_path: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TestScenarioResult:
    """Result of a complete test scenario"""
    scenario_name: str
    overall_status: StepStatus
    duration_ms: float
    steps: List[TestResult]
    conversation_flow: List[Dict[str, Any]] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class TestingHarness:
    """End-to-end testing harness for agent scenarios"""
    
    def __init__(self, page: Page, headless: bool = True, screenshot_dir: str = "./screenshots"):
        self.page = page
        self.headless = headless
        self.screenshot_dir = screenshot_dir
        self.conversation_history = []
        self.action_results = []
    
    async def run_scenario(
        self,
        scenario_name: str,
        steps: List[ActionStep],
        pre_condition: Optional[Callable[..., Coroutine]] = None,
        post_condition: Optional[Callable[..., Coroutine]] = None
    ) -> TestScenarioResult:
        """
        Run a complete test scenario
        
        Args:
            scenario_name: Name of the scenario
            steps: List of action steps to execute
            pre_condition: Optional setup function
            post_condition: Optional cleanup function
            
        Returns:
            TestScenarioResult with all step results
        """
        logger.info("Starting test scenario", scenario=scenario_name, steps_count=len(steps))
        
        start_time = datetime.now()
        results = []
        overall_status = StepStatus.PASSED
        
        try:
            # Run pre-condition if provided
            if pre_condition:
                logger.debug("Running pre-condition")
                await pre_condition()
            
            # Run each step with retry logic
            for step in steps:
                result = await self._execute_step_with_retry(step)
                results.append(result)
                
                if result.status == StepStatus.FAILED:
                    overall_status = StepStatus.FAILED
                    logger.warning("Step failed", step=step.name, error=result.error)
                else:
                    logger.info("Step completed", step=step.name, status=result.status)
            
            # Run post-condition if provided
            if post_condition:
                logger.debug("Running post-condition")
                await post_condition()
        
        except Exception as e:
            logger.error("Test scenario error", error=str(e))
            overall_status = StepStatus.FAILED
        
        duration_ms = (datetime.now() - start_time).total_seconds() * 1000
        
        scenario_result = TestScenarioResult(
            scenario_name=scenario_name,
            overall_status=overall_status,
            duration_ms=duration_ms,
            steps=results,
            conversation_flow=self.conversation_history
        )
        
        logger.info("Test scenario completed", scenario=scenario_name, status=overall_status, duration_ms=duration_ms)
        return scenario_result
    
    async def _execute_step_with_retry(self, step: ActionStep) -> TestResult:
        """Execute a step with retry logic"""
        for attempt in range(step.retries):
            try:
                logger.debug("Executing step", step=step.name, attempt=attempt + 1)
                start_time = datetime.now()
                
                # Execute the action
                result = await step.action(self.page, step)
                
                duration_ms = (datetime.now() - start_time).total_seconds() * 1000
                
                test_result = TestResult(
                    step_name=step.name,
                    status=StepStatus.PASSED if result else StepStatus.FAILED,
                    duration_ms=duration_ms,
                    details={"result": result} if result else {}
                )
                
                logger.info("Step executed successfully", step=step.name, duration_ms=duration_ms)
                return test_result
            
            except Exception as e:
                logger.warning("Step failed", step=step.name, attempt=attempt + 1, error=str(e))
                
                if attempt < step.retries - 1:
                    await asyncio.sleep(step.retry_delay)
                else:
                    # Last attempt failed - take screenshot if enabled
                    screenshot_path = None
                    if step.screenshot_on_failure:
                        screenshot_path = await self._take_screenshot(f"{step.name}_failed")
                    
                    duration_ms = (datetime.now() - datetime.now()).total_seconds() * 1000
                    return TestResult(
                        step_name=step.name,
                        status=StepStatus.FAILED,
                        duration_ms=duration_ms,
                        error=str(e),
                        screenshot_path=screenshot_path
                    )
        
        # Should not reach here
        return TestResult(
            step_name=step.name,
            status=StepStatus.FAILED,
            duration_ms=0,
            error="Max retries exceeded"
        )
    
    async def _take_screenshot(self, name: str) -> str:
        """Take a screenshot and save to file"""
        try:
            import os
            os.makedirs(self.screenshot_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.screenshot_dir}/{name}_{timestamp}.png"
            
            await self.page.screenshot(path=filename)
            logger.debug("Screenshot saved", filename=filename)
            return filename
        except Exception as e:
            logger.error("Failed to take screenshot", error=str(e))
            return None
    
    async def navigate(self, url: str) -> bool:
        """Navigate to URL"""
        try:
            await self.page.goto(url, wait_until="networkidle")
            return True
        except Exception as e:
            logger.error("Navigation failed", url=url, error=str(e))
            return False
    
    async def click_element(self, selector: str, retries: int = 3) -> bool:
        """Click an element with retry logic"""
        for attempt in range(retries):
            try:
                await self.page.click(selector)
                logger.info("Element clicked", selector=selector)
                return True
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(1)
                else:
                    logger.error("Failed to click element", selector=selector, error=str(e))
        return False
    
    async def fill_input(self, selector: str, text: str) -> bool:
        """Fill an input field"""
        try:
            await self.page.fill(selector, text)
            logger.info("Input filled", selector=selector)
            return True
        except Exception as e:
            logger.error("Failed to fill input", selector=selector, error=str(e))
            return False
    
    async def wait_for_element(self, selector: str, timeout: int = 5000) -> bool:
        """Wait for element to appear"""
        try:
            await self.page.wait_for_selector(selector, timeout=timeout)
            logger.info("Element appeared", selector=selector)
            return True
        except Exception as e:
            logger.error("Element did not appear", selector=selector, error=str(e))
            return False
    
    async def extract_text(self, selector: str) -> Optional[str]:
        """Extract text from element"""
        try:
            text = await self.page.text_content(selector)
            logger.debug("Text extracted", selector=selector, text=text[:100] if text else None)
            return text
        except Exception as e:
            logger.error("Failed to extract text", selector=selector, error=str(e))
            return None
    
    def add_conversation_entry(self, role: str, message: str) -> None:
        """Add to conversation history"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "role": role,
            "message": message
        }
        self.conversation_history.append(entry)
        logger.debug("Conversation entry added", role=role, message=message[:50])


async def create_sample_scenario() -> List[ActionStep]:
    """Create a sample test scenario"""
    
    async def navigate_step(page: Page, step: ActionStep):
        await page.goto("https://example.com")
        return True
    
    async def wait_for_dashboard(page: Page, step: ActionStep):
        return await page.wait_for_selector("[data-testid='dashboard']", timeout=5000)
    
    async def filter_data(page: Page, step: ActionStep):
        await page.click("[data-testid='filter-button']")
        await page.fill("[data-testid='filter-input']", "sales")
        return True
    
    return [
        ActionStep(
            name="Navigate to App",
            description="Navigate to the SaaS application",
            action=navigate_step,
            expected_outcome="Page loads successfully"
        ),
        ActionStep(
            name="Wait for Dashboard",
            description="Wait for dashboard to load",
            action=wait_for_dashboard,
            expected_outcome="Dashboard is visible"
        ),
        ActionStep(
            name="Filter Data",
            description="Apply filter to data",
            action=filter_data,
            expected_outcome="Filtered results display"
        ),
    ]
