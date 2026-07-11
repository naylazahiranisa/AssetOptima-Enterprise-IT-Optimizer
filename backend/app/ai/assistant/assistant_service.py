"""Enterprise RAG Assistant service.

Entry point for the /ai/chat endpoint. Handles question sanitisation,
injection detection, RAG retrieval, LLM integration, and response construction.
"""

import logging
import time
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.llm.openai_provider import OpenAIProvider
from app.ai.rag.rag_service import RAGService
from app.ai.utils.logging import log_ai_request
from app.ai.utils.sanitizer import is_prompt_injection, sanitize_input
from app.models.asset import Asset
from app.models.employee import Employee
from app.models.license_model import License
from app.models.software import Software

logger = logging.getLogger(__name__)


class AssistantService:
    """Enterprise AI assistant for IT asset management questions."""

    RAG_DOMAINS = {
        "policy": {"category": "company_policy"},
        "procedure": {"category": "procedure"},
        "sop": {"category": "sop"},
        "inventory": {"category": "inventory"},
        "license": {"category": "license"},
        "security": {"category": "security"},
        "asset": {"category": "asset"},
    }

    def __init__(self, rag_service: RAGService, llm: OpenAIProvider | None = None, db: AsyncSession | None = None):
        self.rag = rag_service
        self.llm = llm
        self.db = db

    async def chat(self, question: str, user_id: str | None = None,
                   top_k: int = 5, domain: str | None = None) -> dict[str, Any]:
        start = time.time()
        question = sanitize_input(question)

        if is_prompt_injection(question):
            log_ai_request("/ai/chat", user_id, question, None, time.time() - start, error="prompt_injection_detected")
            return {
                "answer": "I'm sorry, but your question appears to contain instructions that try to override my behaviour. Please ask a legitimate IT asset management question.",
                "source_documents": [],
                "confidence": 0.0,
                "processing_time": round(time.time() - start, 4),
            }

        metadata_filter = None
        if domain and domain in self.RAG_DOMAINS:
            metadata_filter = self.RAG_DOMAINS[domain]

        try:
            rag_result = await self.rag.answer(question, top_k=top_k, metadata_filter=metadata_filter)
        except Exception as exc:
            logger.error("RAG pipeline failed: %s", exc)
            log_ai_request("/ai/chat", user_id, question, None, time.time() - start, error=str(exc))
            return {
                "answer": "I encountered an error while searching the knowledge base. Please try again later.",
                "source_documents": [],
                "confidence": 0.0,
                "processing_time": round(time.time() - start, 4),
            }

        sources = rag_result.get("source_documents", [])
        context = rag_result.get("context", "")
        prompt = rag_result.get("prompt", "")

        answer = ""
        if self.llm and self.llm.available:
            answer = await self.llm.generate(prompt)
        if not answer:
            answer = await self._db_fallback_answer(question)
        if not answer:
            if context and context != "No relevant documents found.":
                answer = context[:500]
            else:
                answer = self._capabilities_message()

        elapsed = round(time.time() - start, 4)
        confidence = min(0.95, 0.5 + 0.1 * len(sources)) if sources else 0.3

        log_ai_request("/ai/chat", user_id, question, None, elapsed)

        return {
            "answer": answer,
            "source_documents": sources,
            "confidence": round(confidence, 4),
            "processing_time": elapsed,
        }

    def _capabilities_message(self) -> str:
        return (
            "I'm **AssetOptima AI** — your IT asset management assistant. I can answer questions about:\n\n"
            "**Assets** 📦\n"
            "- Total assets, available, assigned, or under maintenance\n"
            "- Assets by category, department, or type (laptops, desktops, etc.)\n\n"
            "**Software** 💻\n"
            "- Software catalog size, software by category\n\n"
            "**Licenses** 🔑\n"
            "- Total licenses, active, expired, pending renewal, or inactive\n\n"
            "**Employees** 👥\n"
            "- Employee count, employees by department\n\n"
            "To get started, just ask a question like:\n"
            "• *\"How many assets do we have?\"*\n"
            "• *\"Show active licenses\"*\n"
            "• *\"List employees by department\"*\n"
            "• *\"Which assets are under maintenance?\"*\n\n"
            "For more detailed answers, upload policy or procedure documents using the document upload feature."
        )

    @staticmethod
    def _has_words(text: str, words: set[str]) -> bool:
        return bool(words & set(text.lower().split()))

    @staticmethod
    def _has_all_words(text: str, words: set[str]) -> bool:
        return words.issubset(set(text.lower().split()))

    async def _db_fallback_answer(self, question: str) -> str:
        if not self.db:
            return self._capabilities_message()

        q = question.lower().strip()
        words = set(q.split())

        try:
            from app.models.department import Department
            from app.models.asset_category import AssetCategory
            from app.models.software_category import SoftwareCategory

            has = lambda ws: self._has_words(q, ws)
            has_all = lambda ws: self._has_all_words(q, ws)

            # ── Summary / overview / help ──────────────────────────────
            if has({"summary", "summarize", "overview", "dashboard", "ringkasan"}) or \
               has({"help"}) or has({"capabilities", "fitur", "bantuan"}):
                return self._capabilities_message()

            # ── Asset count / total ────────────────────────────────────
            if has({"assets", "asset"}) and has({"total", "count", "many", "number", "all", "list", "registered", "system", "jumlah", "have"}):
                count = await self.db.scalar(
                    select(func.count(Asset.id)).where(Asset.is_deleted == False)
                )
                return f"We currently have **{count or 0} assets** registered in the system."

            # ── Asset by status ────────────────────────────────────────
            if has({"available", "unused", "unassigned"}) and has({"asset", "assets"}):
                count = await self.db.scalar(
                    select(func.count(Asset.id)).where(
                        Asset.is_deleted == False, Asset.status == "available"
                    )
                )
                return f"There are **{count or 0} assets** currently marked as available (unassigned)."

            if has({"assigned", "in"}) and has({"asset", "assets"}) and not has({"unassigned", "available"}):
                count = await self.db.scalar(
                    select(func.count(Asset.id)).where(
                        Asset.is_deleted == False, Asset.status == "assigned"
                    )
                )
                return f"There are **{count or 0} assets** currently assigned to employees."

            if has({"maintenance", "repair"}) and has({"asset", "assets"}):
                count = await self.db.scalar(
                    select(func.count(Asset.id)).where(
                        Asset.is_deleted == False, Asset.status == "maintenance"
                    )
                )
                return f"There are **{count or 0} assets** currently under maintenance."

            if has({"retired", "decommissioned"}) and has({"asset", "assets"}):
                count = await self.db.scalar(
                    select(func.count(Asset.id)).where(
                        Asset.is_deleted == False, Asset.status == "retired"
                    )
                )
                return f"There are **{count or 0} assets** that have been retired."

            # ── Asset by category ──────────────────────────────────────
            if has({"category", "categories"}) and has({"asset", "assets"}):
                rows = await self.db.execute(
                    select(AssetCategory.name, func.count(Asset.id))
                    .join(Asset, Asset.category_id == AssetCategory.id)
                    .where(Asset.is_deleted == False)
                    .group_by(AssetCategory.name)
                    .order_by(func.count(Asset.id).desc())
                )
                parts = [f"- **{row.name or 'Uncategorized'}**: {row[1]} assets" for row in rows]
                if parts:
                    return "**Assets by category:**\n" + "\n".join(parts)
                return "No assets found by category."

            # ── Asset by department ────────────────────────────────────
            if has({"department", "departments"}) and has({"asset", "assets"}):
                rows = await self.db.execute(
                    select(Department.name, func.count(Asset.id))
                    .join(Employee, Employee.department_id == Department.id)
                    .join(Asset, Asset.current_employee_id == Employee.id)
                    .where(Asset.is_deleted == False)
                    .group_by(Department.name)
                    .order_by(func.count(Asset.id).desc())
                )
                parts = [f"- **{row.name or 'No Department'}**: {row[1]} assets" for row in rows]
                if parts:
                    return "**Assets by department:**\n" + "\n".join(parts)
                return "No department asset data found."

            # ── Asset by type (laptop, desktop, etc) ──────────────────
            if has({"laptop", "laptops", "desktop", "desktops", "monitor", "monitors", "printer", "printers", "server", "servers", "mobile", "tablet", "tablets"}):
                # Check if also asking about a department
                dept_name = None
                for w in words:
                    if w not in {"show", "list", "the", "assigned", "to", "in", "from", "of", "a", "an", "and", "or", "with", "for", "require", "needs", "need", "department", "departments"}:
                        if w not in {"laptop", "laptops", "desktop", "desktops", "monitor", "monitors", "printer", "printers", "server", "servers", "mobile", "tablet", "tablets"}:
                            dept_name = w.capitalize()
                            break

                for t in ["laptop", "desktop", "monitor", "printer", "server", "mobile", "tablet"]:
                    if t in words or t + "s" in words:
                        base_filter = [
                            Asset.is_deleted == False,
                            Asset.name.ilike(f"%{t}%"),
                        ]
                        # If a department was mentioned, filter by it
                        if dept_name:
                            dept = await self.db.scalar(
                                select(Department).where(Department.name.ilike(f"%{dept_name}%"))
                            )
                            if dept:
                                rows = await self.db.execute(
                                    select(func.count(Asset.id))
                                    .join(Employee, Asset.current_employee_id == Employee.id)
                                    .where(*base_filter, Employee.department_id == dept.id)
                                )
                                count = rows.scalar()
                                return f"There are **{count or 0} {t}s** assigned to the **{dept.name}** department."
                            else:
                                return f"Department **{dept_name}** not found in the system."
                        else:
                            count = await self.db.scalar(
                                select(func.count(Asset.id)).where(*base_filter)
                            )
                            return f"There are **{count or 0}** assets matching **{t}** in their name."

            # ── Software count ─────────────────────────────────────────
            if has({"software"}) and has({"total", "count", "many", "number", "catalog", "list", "all", "jumlah"}):
                count = await self.db.scalar(
                    select(func.count(Software.id)).where(Software.is_deleted == False)
                )
                return f"We have **{count or 0} software titles** in the catalog."

            # ── Software by category ───────────────────────────────────
            if has({"software"}) and has({"category", "categories"}):
                rows = await self.db.execute(
                    select(SoftwareCategory.name, func.count(Software.id))
                    .join(Software, Software.category_id == SoftwareCategory.id, isouter=True)
                    .where(Software.is_deleted == False)
                    .group_by(SoftwareCategory.name)
                    .order_by(func.count(Software.id).desc())
                )
                parts = [f"- **{row.name or 'Uncategorized'}**: {row[1]} titles" for row in rows]
                if parts:
                    return "**Software by category:**\n" + "\n".join(parts)
                return "No software category data found."

            # ── License status queries (before generic count) ─────────
            if has({"license", "licenses"}) and has({"inactive", "unused"}):
                active = await self.db.scalar(
                    select(func.count(License.id)).where(
                        License.is_deleted == False, License.status == "active"
                    )
                )
                total = await self.db.scalar(
                    select(func.count(License.id)).where(License.is_deleted == False)
                )
                inactive = (total or 0) - (active or 0)
                return (
                    f"Out of **{total or 0} total licenses**, **{active or 0}** are active "
                    f"and **{inactive}** are inactive (expired, suspended, or cancelled)."
                )

            if has({"expired", "expiring"}) and has({"license", "licenses"}):
                count = await self.db.scalar(
                    select(func.count(License.id)).where(
                        License.is_deleted == False, License.status == "expired"
                    )
                )
                return f"There are **{count or 0} expired licenses** that need attention."

            if has({"pending", "renewal"}) and has({"license", "licenses"}):
                count = await self.db.scalar(
                    select(func.count(License.id)).where(
                        License.is_deleted == False, License.status == "pending_renewal"
                    )
                )
                return f"There are **{count or 0} licenses** pending renewal."

            if has({"suspended", "cancelled"}) and has({"license", "licenses"}):
                suspended = await self.db.scalar(
                    select(func.count(License.id)).where(
                        License.is_deleted == False, License.status == "suspended"
                    )
                )
                cancelled = await self.db.scalar(
                    select(func.count(License.id)).where(
                        License.is_deleted == False, License.status == "cancelled"
                    )
                )
                return f"There are **{suspended or 0} suspended** and **{cancelled or 0} cancelled** licenses."

            if has({"license", "licenses"}) and has({"active"}):
                count = await self.db.scalar(
                    select(func.count(License.id)).where(
                        License.is_deleted == False, License.status == "active"
                    )
                )
                expired = await self.db.scalar(
                    select(func.count(License.id)).where(
                        License.is_deleted == False, License.status == "expired"
                    )
                )
                return (
                    f"There are **{count or 0} active licenses** and "
                    f"**{expired or 0} expired licenses**."
                )

            # ── License count (generic) ───────────────────────────────
            if has({"license", "licenses"}) and has({"total", "count", "many", "number", "all", "list", "registered", "jumlah"}):
                count = await self.db.scalar(
                    select(func.count(License.id)).where(License.is_deleted == False)
                )
                return f"There are **{count or 0} licenses** registered."

            # ── Employee count ─────────────────────────────────────────
            if has({"employee", "employees"}) and has({"total", "count", "many", "number", "all", "list", "registered", "jumlah"}):
                count = await self.db.scalar(
                    select(func.count(Employee.id)).where(Employee.is_deleted == False)
                )
                return f"There are **{count or 0} employees** registered."

            # ── Employee by department ─────────────────────────────────
            if has({"employee", "employees"}) and has({"department", "departments"}):
                rows = await self.db.execute(
                    select(Department.name, func.count(Employee.id))
                    .join(Employee, Employee.department_id == Department.id, isouter=True)
                    .where(Employee.is_deleted == False)
                    .group_by(Department.name)
                    .order_by(func.count(Employee.id).desc())
                )
                parts = [f"- **{row.name or 'No Department'}**: {row[1]} employees" for row in rows]
                if parts:
                    return "**Employees by department:**\n" + "\n".join(parts)
                return "No employee data found."

            # ── Unscanned assets ───────────────────────────────────────
            if has({"unscanned", "scanned"}) and has({"asset", "assets"}):
                from app.models.software_usage_log import SoftwareUsageLog
                scanned_ids = await self.db.execute(
                    select(Asset.id).join(
                        SoftwareUsageLog, Asset.id == SoftwareUsageLog.asset_id, isouter=True
                    ).where(SoftwareUsageLog.id.is_(None))
                )
                count = len(scanned_ids.all())
                return f"There are approximately **{count} assets** with no recent usage logs."

        except Exception as exc:
            logger.warning("DB fallback query failed: %s", exc)

        return ""
