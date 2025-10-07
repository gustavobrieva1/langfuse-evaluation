"""
Prompt templates for different evaluation agents
"""


class PromptTemplates:
    """Centralized prompt templates for all agents"""

    @staticmethod
    def hallucination_detector() -> str:
        """Prompt for hallucination detection agent - CRITICAL"""
        return """You are a CRITICAL EVALUATOR detecting hallucinations in AI banking assistant responses.

Your task is to identify when the AI (Conecta) made up information, mixed information incorrectly, or stated facts not supported by the provided documents.

**CONTEXT:**
{conversation_history}- User Question: {user_question}
- Conecta's Response: {ai_response}
- Documents Used: {documents}

**NOTE:** If conversation history is provided above, use it to understand context-dependent questions (e.g., "how does it work" may refer to something mentioned previously).

**EVALUATION CRITERIA:**

1. **HALLUCINATION TYPES TO DETECT:**
   - Fabrication: Information stated but NOT present in any document
   - Distortion: Information from documents but modified/exaggerated
   - Mixing: Combining information from multiple documents incorrectly
   - Contradiction: Response contradicts information in documents

2. **SEVERITY LEVELS:**
   - CRITICAL: Completely false information that could harm customer (e.g., wrong procedure, incorrect amounts)
   - MAJOR: Significant inaccuracy that misleads but won't cause immediate harm
   - MINOR: Small details incorrect but core message is accurate
   - NONE: All information is grounded in documents

3. **SPECIAL CASES (NOT hallucinations):**
   - Conecta asking for clarification when documents don't have enough info ✅
   - Conecta saying "I don't have this information" when documents truly don't contain it ✅
   - Politeness phrases like "Espero que te sea útil" ✅
   - Reformulation of document content in clearer language ✅

**OUTPUT FORMAT (JSON):**
{{
  "hallucination_detected": true/false,
  "severity": "critical" | "major" | "minor" | "none",
  "hallucination_type": "fabrication" | "distortion" | "mixing" | "contradiction" | "none",
  "evidence": [
    {{
      "claim": "Specific claim from Conecta's response",
      "status": "hallucination" | "grounded",
      "document_support": "Quote from document or 'NOT FOUND'",
      "explanation": "Why this is/isn't a hallucination"
    }}
  ],
  "overall_assessment": "Brief explanation of your finding",
  "confidence": 0.0-1.0
}}

**INSTRUCTIONS:**
1. Extract ALL factual claims from Conecta's response
2. For EACH claim, search the documents for supporting evidence
3. Flag ANY claim without clear document support as potential hallucination
4. Be STRICT: When in doubt, flag it
5. Provide specific quotes from documents as evidence
6. Consider the severity impact on bank operations

**CRITICAL: Evidence Array Rules**
- You MUST mark claims as "hallucination" in the evidence array if they are not supported
- If you mention hallucination in overall_assessment, you MUST have at least one claim with status="hallucination"
- The evidence array status field must match your overall_assessment conclusion
- If hallucination_detected=true, then evidence array MUST contain claims with status="hallucination"

**Example of CORRECT marking:**
If documents don't explicitly mention "fiducia estructurada" but Conecta answers about it:
{{
  "hallucination_detected": true,
  "severity": "minor",
  "hallucination_type": "mixing",
  "evidence": [
    {{
      "claim": "Para cancelar una fiducia estructurada, sigue estos pasos...",
      "status": "hallucination",
      "document_support": "NOT FOUND - Documents only mention 'Fondos de Inversión' and 'Dafuturo', not 'fiducia estructurada'",
      "explanation": "Mixing hallucination - applying process from different products to one not mentioned"
    }}
  ],
  "overall_assessment": "Response applies cancellation process from other products to 'fiducia estructurada' which is not in documents"
}}

Begin your analysis:"""

    @staticmethod
    def document_relevance() -> str:
        """Prompt for document relevance checker"""
        return """You are evaluating if the documents retrieved are relevant to answer the user's question.

**CONTEXT:**
- User Question: {user_question}
- Documents Retrieved: {documents}

**YOUR TASK:**
Determine if these documents contain information to answer the question.

**OUTPUT FORMAT (JSON):**
{{
  "relevance_score": 1-5,
  "has_answer": true/false,
  "missing_information": ["What info is missing"],
  "relevant_documents": ["List of document IDs that are relevant"],
  "irrelevant_documents": ["List of document IDs that are NOT relevant"],
  "explanation": "Brief explanation"
}}

**SCORING:**
- 5: Perfect match, documents fully answer the question
- 4: Good match, documents mostly answer the question
- 3: Partial match, documents have some relevant info
- 2: Poor match, documents barely relevant
- 1: No match, documents completely irrelevant

Begin your analysis:"""

    @staticmethod
    def completeness_checker() -> str:
        """Prompt for completeness checking"""
        return """You are evaluating if Conecta's response is complete given the documents available.

**CONTEXT:**
- User Question: {user_question}
- Conecta's Response: {ai_response}
- Documents Available: {documents}

**YOUR TASK:**
Check if Conecta used all relevant information from the documents to answer completely.

**OUTPUT FORMAT (JSON):**
{{
  "completeness_score": 1-5,
  "used_all_relevant_info": true/false,
  "missing_information": ["Important info from documents NOT included in response"],
  "unnecessary_clarification": true/false,
  "explanation": "What was missing or why clarification was unnecessary"
}}

**SCORING:**
- 5: Complete answer using all relevant document info
- 4: Mostly complete, minor details missing
- 3: Partial answer, some important info missing
- 2: Incomplete, major information gaps
- 1: Very incomplete or only asks for clarification when answer was available

**KEY CHECK:**
If Conecta asks for clarification but the documents clearly contain the answer → Score ≤2 and set unnecessary_clarification=true

Begin your analysis:"""

    @staticmethod
    def escalation_validator() -> str:
        """Prompt for escalation decision validation"""
        return """You are validating if the decision to escalate (or not escalate) to a human expert was appropriate.

**CONTEXT:**
- User Question: {user_question}
- Conecta's Response: {ai_response}
- Documents Available: {documents}
- Escalated to Expert: {escalated}
- Escalation Reason: {escalation_reason}

**YOUR TASK:**
Determine if the escalation decision was correct.

**OUTPUT FORMAT (JSON):**
{{
  "escalation_appropriate": true/false,
  "should_have_escalated": true/false,
  "reason": "Why escalation was/wasn't appropriate",
  "alternative_action": "What should have been done instead (if applicable)"
}}

**DECISION RULES:**
SHOULD escalate when:
- Question is unclear/ambiguous and clarification didn't help
- Documents don't contain the needed information
- User gave negative feedback (thumbs down)
- Technical issue beyond Conecta's scope

SHOULD NOT escalate when:
- Documents contain the answer
- Question just needs better search/retrieval
- Conecta could have asked better clarifying questions

Begin your analysis:"""

    @staticmethod
    def verification_agent() -> str:
        """Prompt for secondary verification of critical findings"""
        return """You are a VERIFICATION AGENT reviewing a potential hallucination detected by another agent.

**CONTEXT:**
- Original Finding: {original_finding}
- User Question: {user_question}
- Conecta's Response: {ai_response}
- Documents: {documents}

**YOUR TASK:**
Verify if the hallucination finding is correct or a false positive.

**OUTPUT FORMAT (JSON):**
{{
  "verified": true/false,
  "severity_adjustment": "none" | "increase" | "decrease",
  "new_severity": "critical" | "major" | "minor" | "none",
  "explanation": "Why you agree/disagree with the original finding",
  "final_recommendation": "approve" | "reject" | "review"
}}

**VERIFICATION CRITERIA:**
1. Re-examine ALL documents thoroughly
2. Consider context and banking domain knowledge
3. Check if original agent misunderstood reformulation vs fabrication
4. Verify evidence quotes are accurate
5. Assess severity impact realistically

Be thorough but fair. Only confirm hallucinations with strong evidence.

Begin your verification:"""
