"""
Simple AI Agent for SSL Certificate Checking
Uses Google Gemini directly with function calling
"""
import os
import json
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
import google.genai as genai

from app.services.ssl_checker import SSLCheckerService

# Load environment variables
load_dotenv()

# Configure Google Gemini
client = genai.Client(api_key=os.getenv('GOOGLE_API_KEY'))


class SSLAgent:
    """Simple AI agent for SSL certificate checking using Google Gemini"""
    
    def __init__(self):
        self.model_name = os.getenv('LLM_MODEL', 'gemini-2.0-flash-exp')
        self.ssl_checker = SSLCheckerService()
        
        # System prompt for conversational behavior
        self.system_prompt = """Your name is SSL Guardian and your job is to check SSL/TLS certificates for security vulnerabilities, validity issues, and best practices.

You are a friendly, conversational AI assistant that helps developers and teams ensure their websites and APIs have secure, valid SSL certificates.

When a user greets you or starts a conversation:
- Introduce yourself warmly as SSL Guardian
- Ask them which domain(s) they'd like you to check
- If they mention domains without specifying what to check, assume they want a full SSL certificate analysis
- Be encouraging about the importance of SSL security

When analyzing SSL certificates:
- Check certificate validity and expiration dates
- Review certificate issuer and chain of trust
- Analyze security details (key size, algorithms, SANs)
- Identify security vulnerabilities or weak configurations
- Flag certificates expiring within 30 days as warnings
- Provide specific, actionable recommendations
- Assign a security grade: A+, A, B, C, D, or F
- Give a clear assessment: SECURE, MONITOR, URGENT_ATTENTION, or CRITICAL_ISSUE

Keep your responses:
- Conversational and friendly (not robotic or overly formal)
- Concise but informative with key details
- Focused on helping users maintain secure certificates
- Balanced (point out both good security practices AND issues to fix)
- Actionable (tell them exactly what to check and when to renew)

Use clear indicators:
- ✅ Valid/secure certificates
- ⚠️ Certificates expiring soon or minor issues
- ❌ Invalid/expired certificates or security problems
- 📊 Include countdown days for expiration
- 🔒 Highlight security strengths
- 🚨 Flag critical security issues

If the user asks about specific aspects (like "check expiration only" or "focus on security"), prioritize that area in your analysis.

Special handling:
- Multiple domains: Provide summary table with status overview
- Single domain: Give detailed certificate breakdown
- Invalid domains: Suggest checking domain spelling or DNS
- Connection issues: Explain possible causes (firewall, DNS, etc.)

Remember: You're here to help users maintain secure, trustworthy websites and APIs. Be encouraging about SSL best practices while being thorough about security issues!"""
        
        # Define function declarations for Gemini
        self.tools = [
            {
                "function_declarations": [
                    {
                        "name": "check_ssl_certificate",
                        "description": "Check SSL/TLS certificate for a single domain. Returns certificate details including expiry date, issuer, and validity status.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "domain": {
                                    "type": "string",
                                    "description": "The domain name to check (e.g., 'github.com', 'google.com')"
                                }
                            },
                            "required": ["domain"]
                        }
                    },
                    {
                        "name": "check_multiple_domains",
                        "description": "Check SSL/TLS certificates for multiple domains at once. Returns a summary of all certificates.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "domains": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "List of domain names to check"
                                }
                            },
                            "required": ["domains"]
                        }
                    }
                ]
            }
        ]
    
    def _execute_function(self, function_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the requested function and return results"""
        
        if function_name == "check_ssl_certificate":
            domain = arguments.get("domain")
            result = self.ssl_checker.check_certificate(domain)
            
            if result.success:
                return {
                    "success": True,
                    "domain": domain,
                    "certificate": {
                        "issuer": result.certificate.issuer,
                        "subject": result.certificate.subject,
                        "valid_from": result.certificate.notBefore.isoformat(),
                        "valid_until": result.certificate.notAfter.isoformat(),
                        "days_until_expiry": result.certificate.daysUntilExpiry,
                        "is_valid": result.certificate.isValid,
                        "is_expiring_soon": result.certificate.isExpiringSoon
                    },
                    "message": f"✅ SSL certificate for {domain} is valid until {result.certificate.notAfter.strftime('%Y-%m-%d')} ({result.certificate.daysUntilExpiry} days remaining)"
                }
            else:
                return {
                    "success": False,
                    "domain": domain,
                    "error": result.error,
                    "message": f"❌ Failed to check SSL for {domain}: {result.error}"
                }
        
        elif function_name == "check_multiple_domains":
            domains = arguments.get("domains", [])
            results = []
            
            for domain in domains:
                result = self.ssl_checker.check_certificate(domain)
                if result.success:
                    results.append({
                        "domain": domain,
                        "status": "✅ Valid" if result.certificate.isValid else "❌ Invalid",
                        "days_remaining": result.certificate.daysUntilExpiry,
                        "expires": result.certificate.notAfter.strftime('%Y-%m-%d')
                    })
                else:
                    results.append({
                        "domain": domain,
                        "status": "❌ Error",
                        "error": result.error
                    })
            
            return {
                "success": True,
                "total_domains": len(domains),
                "results": results,
                "message": f"Checked {len(domains)} domain(s)"
            }
        
        return {"success": False, "error": f"Unknown function: {function_name}"}
    
    async def process_message(self, user_message: str, conversation_history: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        Process a user message and return AI response
        
        Args:
            user_message: The user's input message
            conversation_history: Optional previous messages for context
            
        Returns:
            Dictionary with response text and any artifacts (structured data)
        """
        try:
            # Build contents from conversation history
            contents = []
            
            # Add system prompt first
            contents.append({"role": "user", "parts": [{"text": f"System: {self.system_prompt}"}]})
            
            # Add conversation history
            if conversation_history:
                for msg in conversation_history:
                    role = msg.get("role", "user")
                    content = msg.get("content", "")
                    contents.append({"role": role, "parts": [{"text": content}]})
            
            # Add current user message
            contents.append({"role": "user", "parts": [{"text": user_message}]})
            
            # Generate response with tools
            response = client.models.generate_content(
                model=self.model_name,
                contents=contents,
                config={
                    "tools": self.tools,
                    "automatic_function_calling": {"disable": True}  # We'll handle function calls manually
                }
            )
            
            # Process function calls if any
            function_responses = []
            artifacts = []
            
            # Check if the response has function calls
            if response.candidates and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'function_call') and part.function_call:
                        function_call = part.function_call
                        function_name = function_call.name
                        function_args = dict(function_call.args)
                        
                        # Execute the function
                        function_result = self._execute_function(function_name, function_args)
                        
                        # Store as artifact
                        artifacts.append({
                            "name": function_name,
                            "data": function_result
                        })
                        
                        # For function calling, we need to send another request with the function response
                        function_response_content = {
                            "role": "user",
                            "parts": [{
                                "function_response": {
                                    "name": function_name,
                                    "response": {"result": function_result}
                                }
                            }]
                        }
                        
                        # Get final response after function call
                        final_response = client.models.generate_content(
                            model=self.model_name,
                            contents=contents + [function_response_content]
                        )
                        
                        final_text = final_response.text if hasattr(final_response, 'text') and final_response.text else "SSL check completed."
                    else:
                        # Regular text response
                        final_text = response.text if hasattr(response, 'text') and response.text else "I've processed your SSL certificate request."
            else:
                final_text = response.text if hasattr(response, 'text') and response.text else "I've processed your SSL certificate request."
            
            return {
                "success": True,
                "response": final_text,
                "artifacts": artifacts,
                "usage": getattr(response, 'usage_metadata', {})
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response": f"I encountered an error while processing your request: {str(e)}"
            }


# Create singleton instance
ssl_agent = SSLAgent()
