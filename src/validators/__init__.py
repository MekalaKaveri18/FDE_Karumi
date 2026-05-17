"""Automated Onboarding and Configuration Validator

Validates browser automation setup, detects UI elements, and tests login flows.
"""

from typing import Dict, List, Any
from dataclasses import dataclass
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
import structlog

logger = structlog.get_logger(__name__)


@dataclass
class ValidationResult:
    """Result of a validation check"""
    passed: bool
    check_name: str
    message: str
    details: Dict[str, Any] = None


@dataclass
class ValidationReport:
    """Complete validation report for an application"""
    url: str
    status: str  # "success", "warning", "failed"
    checks: List[ValidationResult]
    edge_cases: List[str]
    recommendations: List[str]
    timestamp: str


class ConfigurationValidator:
    """Validates SaaS application setup for agent compatibility"""
    
    def __init__(self, headless: bool = True, timeout: int = 30000):
        self.headless = headless
        self.timeout = timeout
        self.results: List[ValidationResult] = []
        self.edge_cases: List[str] = []
        self.recommendations: List[str] = []
    
    async def validate_app(self, url: str, username: str = None, password: str = None) -> ValidationReport:
        """
        Validate a SaaS application for agent compatibility
        
        Args:
            url: Target application URL
            username: Test account username (optional)
            password: Test account password (optional)
            
        Returns:
            ValidationReport with findings and recommendations
        """
        logger.info("Starting validation", url=url)
        self.results = []
        self.edge_cases = []
        self.recommendations = []
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            try:
                context = await browser.new_context()
                page = await context.new_page()
                
                # Run validation checks
                await self._check_page_load(page, url)
                await self._check_ui_elements(page)
                await self._check_accessibility(page)
                
                if username and password:
                    await self._check_login_flow(page, username, password)
                
                await self._check_dynamic_content(page)
                await self._detect_edge_cases(page)
                
                await context.close()
            finally:
                await browser.close()
        
        status = "success" if all(r.passed for r in self.results) else "warning" if any(r.passed for r in self.results) else "failed"
        
        from datetime import datetime
        report = ValidationReport(
            url=url,
            status=status,
            checks=self.results,
            edge_cases=self.edge_cases,
            recommendations=self.recommendations,
            timestamp=datetime.now().isoformat()
        )
        
        logger.info("Validation complete", status=status, checks_count=len(self.results))
        return report
    
    async def _check_page_load(self, page: Page, url: str) -> None:
        """Check if page loads successfully"""
        try:
            await page.goto(url, wait_until="networkidle", timeout=self.timeout)
            title = await page.title()
            self.results.append(ValidationResult(
                passed=True,
                check_name="Page Load",
                message=f"Page loaded successfully (title: {title})",
                details={"url": url, "title": title}
            ))
            logger.debug("Page load check passed", title=title)
        except Exception as e:
            self.results.append(ValidationResult(
                passed=False,
                check_name="Page Load",
                message=f"Failed to load page: {str(e)}",
                details={"error": str(e)}
            ))
            self.recommendations.append("Ensure the application URL is publicly accessible")
            logger.warning("Page load check failed", error=str(e))
    
    async def _check_ui_elements(self, page: Page) -> None:
        """Detect common UI elements"""
        selectors_to_check = [
            ("button", "Buttons"),
            ("input[type='text']", "Text inputs"),
            ("input[type='password']", "Password inputs"),
            ("[role='button']", "ARIA buttons"),
            ("[role='link']", "ARIA links"),
            ("a", "Links"),
        ]
        
        detected_elements = {}
        for selector, label in selectors_to_check:
            try:
                count = await page.locator(selector).count()
                detected_elements[label] = count
            except:
                detected_elements[label] = 0
        
        self.results.append(ValidationResult(
            passed=True,
            check_name="UI Elements Detection",
            message=f"Detected {len([v for v in detected_elements.values() if v > 0])} element types",
            details=detected_elements
        ))
        logger.info("UI elements detected", elements=detected_elements)
    
    async def _check_accessibility(self, page: Page) -> None:
        """Check accessibility features"""
        try:
            # Check for form labels
            labels = await page.locator("label").count()
            alt_text = await page.locator("img[alt]").count()
            
            accessibility_score = (labels + alt_text) / max(
                await page.locator("input").count() + 
                await page.locator("img").count(), 1
            )
            
            self.results.append(ValidationResult(
                passed=accessibility_score > 0.5,
                check_name="Accessibility",
                message=f"Accessibility score: {accessibility_score:.2%}",
                details={"labels": labels, "alt_text": alt_text}
            ))
            
            if accessibility_score < 0.7:
                self.recommendations.append("Improve accessibility with proper labels and alt text for images")
            
            logger.info("Accessibility check complete", score=accessibility_score)
        except Exception as e:
            logger.warning("Accessibility check failed", error=str(e))
    
    async def _check_login_flow(self, page: Page, username: str, password: str) -> None:
        """Test login flow"""
        try:
            # Try common login selectors
            login_selectors = [
                "input[type='email']", "input[name='email']", "input[name='username']",
                "input[type='password']", "input[name='password']",
                "button[type='submit']", "button:has-text('Login')", "button:has-text('Sign In')"
            ]
            
            found_elements = {
                "email_fields": 0,
                "password_fields": 0,
                "submit_buttons": 0
            }
            
            for selector in login_selectors[:3]:  # Check email fields
                try:
                    count = await page.locator(selector).count()
                    if count > 0:
                        found_elements["email_fields"] += count
                        break
                except:
                    pass
            
            for selector in login_selectors[3:5]:  # Check password fields
                try:
                    count = await page.locator(selector).count()
                    if count > 0:
                        found_elements["password_fields"] += count
                        break
                except:
                    pass
            
            self.results.append(ValidationResult(
                passed=found_elements["email_fields"] > 0 and found_elements["password_fields"] > 0,
                check_name="Login Flow",
                message="Found required login form elements",
                details=found_elements
            ))
            logger.info("Login flow check complete", elements=found_elements)
        except Exception as e:
            logger.warning("Login flow check failed", error=str(e))
    
    async def _check_dynamic_content(self, page: Page) -> None:
        """Detect dynamic content and modals"""
        try:
            # Check for common modal/dialog patterns
            modals = await page.locator("[role='dialog'], .modal, .popup").count()
            dynamic_elements = await page.locator("[data-react-fiber], [ng-app], [v-app]").count()
            
            if modals > 0:
                self.edge_cases.append(f"Dynamic modals detected ({modals})")
            
            self.results.append(ValidationResult(
                passed=True,
                check_name="Dynamic Content",
                message=f"Found {modals} modal patterns and {dynamic_elements} dynamic element indicators",
                details={"modals": modals, "dynamic_indicators": dynamic_elements}
            ))
            logger.info("Dynamic content check complete", modals=modals, dynamic=dynamic_elements)
        except Exception as e:
            logger.warning("Dynamic content check failed", error=str(e))
    
    async def _detect_edge_cases(self, page: Page) -> None:
        """Detect potential edge cases for automation"""
        try:
            # Check for authentication mechanisms
            if await page.locator("[data-testid='2fa'], .auth-code, .verification").count() > 0:
                self.edge_cases.append("Multi-factor authentication detected")
            
            # Check for timeouts
            meta_refresh = await page.locator("meta[http-equiv='refresh']").count()
            if meta_refresh > 0:
                self.edge_cases.append("Meta refresh detected - may cause timeout issues")
            
            # Check for lazy loading
            lazy_loading = await page.locator("[loading='lazy']").count()
            if lazy_loading > 0:
                self.edge_cases.append("Lazy loading detected - may affect element visibility")
            
            # Check for voice/accessibility features
            if await page.locator("[aria-label]").count() > 5:
                self.recommendations.append("Good ARIA labels present - voice automation may work well")
            
            logger.info("Edge case detection complete", edge_cases=self.edge_cases)
        except Exception as e:
            logger.warning("Edge case detection failed", error=str(e))


async def main():
    """Example usage"""
    validator = ConfigurationValidator()
    report = await validator.validate_app("https://example.com")
    return report


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
